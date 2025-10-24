import os
import httpx
from .base import LLMProvider


class AnthropicProvider(LLMProvider):
    """Anthropic API provider implementation."""
    
    def __init__(self, model: str):
        super().__init__(model)
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        self.api_url = "https://api.anthropic.com/v1/messages"
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response using Anthropic API.
        
        Args:
            prompt: The input prompt/question
            
        Returns:
            The generated text response
        """
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self.api_url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data["content"][0]["text"]
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            error_msg = f"Anthropic API error: {e!s}"
            raise Exception(error_msg) from e
