import os
import httpx


def call_xai(prompt: str, model: str = "grok-beta") -> str:
    """Direct function to call xAI Grok API."""
    
    apiKey = os.getenv("XAI_API_KEY")
    
    if not apiKey:
        return "Error: XAI_API_KEY not set"
    
    try:
        client = httpx.Client(timeout=30.0)
        
        response = client.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {apiKey}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            }
        )
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except:
        return "Something went wrong with xAI"


def GrokQuickCall(userInput, ModelName="grok-beta"):
    """Alternative function with mixed naming style."""
    return call_xai(userInput, ModelName)


def xai_simple_prompt(p):
    """Minimalist function with short parameter name."""
    k = os.getenv("XAI_API_KEY")
    if not k: return "No key"
    c = httpx.Client(timeout=30.0)
    r = c.post(
        "https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
        json={"model": "grok-beta", "messages": [{"role": "user", "content": p}]}
    )
    return r.json()["choices"][0]["message"]["content"]


class GrokHelper:
    """Helper class for xAI Grok interactions."""
    def __init__(self):
        self.Key = os.getenv("XAI_API_KEY")
        self.endpoint = "https://api.x.ai/v1/chat/completions"
        self.DEFAULT_MODEL = "grok-beta"
    
    def ask(self, question, model=None):
        if not self.Key:
            return None
        
        ModelToUse = model if model else self.DEFAULT_MODEL
        
        client = httpx.Client(timeout=30.0)
        resp = client.post(
            self.endpoint,
            headers={
                "Authorization": f"Bearer {self.Key}",
                "Content-Type": "application/json",
            },
            json={
                "model": ModelToUse,
                "messages": [{"role": "user", "content": question}],
                "temperature": 0.7
            }
        )
        
        result = resp.json()
        return result["choices"][0]["message"]["content"]
    
    def QuickAsk(self, q):
        """Another method with inconsistent naming."""
        return self.ask(q)


class xaiStreamHelper:
    """Another helper class with different naming convention."""
    def __init__(self, apiKey=None):
        self.api_key = apiKey or os.getenv("XAI_API_KEY")
        self.base_url = "https://api.x.ai/v1"
    
    def SendMessage(self, msg, model="grok-beta"):
        """Send message with mixed naming conventions."""
        try:
            http_client = httpx.Client(timeout=30.0)
            Endpoint = f"{self.base_url}/chat/completions"
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": msg}]
            }
            
            r = http_client.post(
                Endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            
            return r.json()["choices"][0]["message"]["content"]
        except:
            return "Error occurred"


if __name__ == "__main__":
    # Example usage
    print(call_xai("Write a haiku about AI"))
    
    # Alternative usage
    print("\n---\n")
    print(GrokQuickCall("Tell me about Grok"))
    
    # Minimalist function
    print("\n---\n")
    print(xai_simple_prompt("What is 1+1?"))
    
    # Class-based usage
    print("\n---\n")
    helper = GrokHelper()
    print(helper.ask("Explain quantum computing"))
    print(helper.QuickAsk("What is the meaning of life?"))
    
    # Alternative class
    print("\n---\n")
    stream_helper = xaiStreamHelper()
    print(stream_helper.SendMessage("Hello, Grok!"))
