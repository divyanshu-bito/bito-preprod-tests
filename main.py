from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from providers import ProviderFactory

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="LLM Proxy API", description="A simple proxy API for multiple LLM providers")


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    provider: str
    model: str
    prompt: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    provider: str
    model: str
    response: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint that proxies requests to different LLM providers.
    
    Args:
        request: ChatRequest with provider, model, and prompt
        
    Returns:
        ChatResponse with the generated response
        
    Raises:
        HTTPException: If provider is invalid or API call fails
    """
    try:
        # Get the appropriate provider using the factory
        provider = ProviderFactory.get_provider(request.provider, request.model)
        
        # Generate response
        response_text = provider.generate_response(request.prompt)
        
        return ChatResponse(
            provider=request.provider,
            model=request.model,
            response=response_text
        )
    except ValueError as e:
        # Handle invalid provider name
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle API errors
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "LLM Proxy API",
        "endpoints": {
            "/chat": "POST - Send prompts to different LLM providers",
            "/docs": "GET - Interactive API documentation"
        },
        "supported_providers": ["openai", "anthropic"]
    }
