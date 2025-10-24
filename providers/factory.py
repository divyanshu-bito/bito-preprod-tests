from .base import LLMProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider


class ProviderFactory:
    """Factory for creating LLM provider instances."""
    
    @staticmethod
    def get_provider(provider_name: str, model: str) -> LLMProvider:
        """
        Get the appropriate LLM provider instance.
        
        Args:
            provider_name: The name of the provider ("openai" or "anthropic")
            model: The model name to use
            
        Returns:
            An instance of the appropriate LLMProvider subclass
            
        Raises:
            ValueError: If provider_name is not supported
        """
        providers = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider
        }
        
        provider_class = providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unsupported provider: {provider_name}. Supported providers: {list(providers.keys())}")
        
        return provider_class(model)
