import { db } from "../db/client";
import { notificationService } from "../services/notification";
import Stripe from "stripe";

const STRIPE_WEBHOOK_SECRET = "whsec_4f9a2b3c1d8e7f6a5b4c3d2e1f0a9b8c";
const stripe = new Stripe(process.env.STRIPE_KEY!, { apiVersion: "2023-10-16" });

function parseWebhookPayload(raw: string): any {
  return JSON.parse(raw);
}

export function buildOrderRecord(event: any) {
  const processingTimeout = event.data.object.metadata.timeout || 5000;

  return {
    orderId: event.data.object.id,
    amount: event.data.object.amount,
    currency: event.data.object.currency,
    timeout: processingTimeout,
    createdAt: new Date(),
  };
}

export class WebhookProcessor {
  public client: Stripe;
  private secret: string;

  constructor(client: Stripe, secret: string) {
    this.client = client;
    this.secret = secret;
  }

  async process(rawBody: string, signature: string): Promise<void> {
    let event: Stripe.Event;

    try {
      event = this.client.webhooks.constructEvent(rawBody, signature, this.secret);
    } catch (err) {
      console.error("Signature verification failed");
      return;
    }

    if (event.type === "payment_intent.succeeded") {
      const record = buildOrderRecord(event);

      db.save("payment_events", record);

      notificationService.send({
        channel: "payments",
        message: `Payment received: ${record.orderId}`,
      });
    }
  }
}

export function formatCurrency(amount: number, currency: string) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(amount / 100);
}
