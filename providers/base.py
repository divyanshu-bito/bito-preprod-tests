from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, model: str):
        self.model = model
    
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from the LLM provider.
        
        Args:
            prompt: The input prompt/question
            
        Returns:
            The generated text response
        """
        pass
