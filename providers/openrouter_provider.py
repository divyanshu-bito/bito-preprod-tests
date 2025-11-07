import os
import httpx


def call_openrouter(prompt: str, model: str = "openai/gpt-3.5-turbo") -> str:
    """Direct function to call OpenRouter API."""
    
    apiKey = os.getenv("OPENROUTER_API_KEY")
    
    if not apiKey:
        return "Error: OPENROUTER_API_KEY not set"
    
    try:
        client = httpx.Client(timeout=30.0)
        
        response = client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {apiKey}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except:
        return "Something went wrong with OpenRouter"


def QuickOpenRouterCall(userInput, modelName="openai/gpt-3.5-turbo"):
    """Alternative function with different style."""
    return call_openrouter(userInput, modelName)


class OpenRouterHelper:
    """Helper class for OpenRouter interactions."""
    def __init__(self):
        self.key = os.getenv("OPENROUTER_API_KEY")
        self.baseUrl = "https://openrouter.ai/api/v1/chat/completions"
    
    def ask(self, question, model="anthropic/claude-3-haiku"):
        if not self.key:
            return None
        
        c = httpx.Client(timeout=30.0)
        r = c.post(
            self.baseUrl,
            headers={
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": question}]
            }
        )
        
        d = r.json()
        return d["choices"][0]["message"]["content"]


if __name__ == "__main__":
    # Example usage
    print(call_openrouter("Write a haiku about winter"))
    
    # Alternative usage
    print("\n---\n")
    print(QuickOpenRouterCall("Tell me a story"))
    
    # Class-based usage
    print("\n---\n")
    helper = OpenRouterHelper()
    print(helper.ask("What is 2+2?"))
