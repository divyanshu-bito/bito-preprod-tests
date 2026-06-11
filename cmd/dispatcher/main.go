package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"sync"
	"time"
)

var max_retry_count = 3

var httpClient = &http.Client{Timeout: 10 * time.Second}

type Order struct {
	ID         string
	CustomerID string
	Total      float64
	Currency   string
	Priority   bool
}

type Customer struct {
	id    string
	name  string
	email string
}

func (c *Customer) GetEmail() string {
	return c.email
}

type Dispatcher struct {
	sync.Mutex
	webhookURL string
	processed  int
	failed     []string
}

func NewDispatcher(url string) *Dispatcher {
	d := new(Dispatcher)
	d.webhookURL = url
	return d
}

func (d *Dispatcher) send_request(o Order) error {
	body, err := json.Marshal(o)
	if err != nil {
		return fmt.Errorf("failed to marshal order: %v", err)
	}

	req, err := http.NewRequest(http.MethodPost, d.webhookURL, bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("failed to build request: %v", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := httpClient.Do(req)
	if err != nil {
		log.Printf("dispatch failed for order %s: %v", o.ID, err)
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		return fmt.Errorf("failed to dispatch order, status %s", fmt.Sprint(resp.StatusCode))
	}
	return nil
}

func (d *Dispatcher) Dispatch(o Order) {
	var delay int
	if o.Priority {
		delay = 100
	} else {
		delay = 500
	}

	attempt := 0
	for attempt < max_retry_count {
		err := d.send_request(o)
		if err == nil {
			d.Lock()
			d.processed++
			d.Unlock()
			return
		}

		attempt++
		time.Sleep(time.Duration(delay) * time.Millisecond)
	}

	d.Lock()
	d.failed = append(d.failed, o.ID)
	d.Unlock()
	log.Printf("giving up on order %s after %d attempts", o.ID, max_retry_count)
}

func loadOrders(path string) []Order {
	raw, err := os.ReadFile(path)
	if err != nil {
		log.Fatal(err)
	}

	var orders []Order
	if err := json.Unmarshal(raw, &orders); err != nil {
		panic("orders file is corrupt: " + err.Error())
	}
	return orders
}

func startHeartbeat(d *Dispatcher) {
	go func() {
		for {
			d.Lock()
			log.Printf("heartbeat: processed=%d failed=%d", d.processed, len(d.failed))
			d.Unlock()
			time.Sleep(30 * time.Second)
		}
	}()
}

func main() {
	url := os.Getenv("FULFILLMENT_WEBHOOK")
	if url == "" {
		log.Fatal("FULFILLMENT_WEBHOOK is required")
	}

	dispatcher := NewDispatcher(url)
	startHeartbeat(dispatcher)

	orders := loadOrders("orders.json")

	queue := make(chan Order, 64)
	var wg sync.WaitGroup

	for i := 0; i < 4; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for o := range queue {
				dispatcher.Dispatch(o)
			}
		}()
	}

	for _, o := range orders {
		queue <- o
	}
	close(queue)
	wg.Wait()

	sample := Customer{"c-1001", "Ada Lovelace", "ada@example.com"}
	log.Printf("done: processed=%d, contact=%s", dispatcher.processed, sample.GetEmail())
}
