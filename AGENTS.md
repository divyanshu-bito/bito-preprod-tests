# LLM Proxy Architecture & Design Document

## Document Overview

### Purpose
This document serves as a coding guideline and technical reference for AI agents working with this codebase. It provides comprehensive information about the current architecture, design patterns, implementation details, and the rationale behind design decisions. AI agents should use this document to understand the existing code structure, maintain consistency when making modifications, and follow established patterns when extending functionality.

### What This Document Covers
- **System Architecture**: High-level overview of components and their interactions
- **Design Patterns**: Detailed explanation of the Factory Pattern implementation
- **Component Design**: In-depth analysis of each system component
- **Data Flow**: Request/response lifecycle through the system
- **Design Decisions**: Rationale behind current architectural choices
- **Implementation Details**: Code structure, conventions, and patterns in use

---

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Design Patterns](#design-patterns)
3. [Component Design](#component-design)
4. [Data Flow](#data-flow)
5. [Design Decisions](#design-decisions)
6. [Error Handling Strategy](#error-handling-strategy)
7. [Security Considerations](#security-considerations)
8. [Coding Conventions](#coding-conventions)

---

## System Architecture

### High-Level Overview

The LLM Proxy application follows a layered architecture with clear separation between the presentation layer (FastAPI), business logic layer (Provider implementations), and integration layer (external LLM APIs).

```
┌─────────────────────────────────────────────┐
│           FastAPI Application               │
│         (Presentation Layer)                │
│   - Request validation (Pydantic)           │
│   - Route handling (/chat endpoint)         │
│   - Response formatting                     │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│          Provider Factory                   │
│        (Abstraction Layer)                  │
│   - Provider selection logic                │
│   - Instance creation                       │
└────────────────┬────────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
┌──────────────┐   ┌──────────────┐
│   OpenAI     │   │  Anthropic   │
│   Provider   │   │   Provider   │
│              │   │              │
│ (Concrete    │   │ (Concrete    │
│  Impl.)      │   │  Impl.)      │
└──────┬───────┘   └──────┬───────┘
       │                  │
       ▼                  ▼
┌──────────────┐   ┌──────────────┐
│  OpenAI API  │   │ Anthropic API│
└──────────────┘   └──────────────┘
```

### Component Layers

1. **Presentation Layer** (`main.py`)
   - Handles HTTP requests/responses
   - Validates input using Pydantic models
   - Manages API endpoints

2. **Abstraction Layer** (`providers/factory.py`)
   - Implements Factory Pattern
   - Routes requests to appropriate providers
   - Decouples client code from concrete implementations

3. **Business Logic Layer** (`providers/*.py`)
   - Abstract base class defines contract
   - Concrete providers implement LLM-specific logic
   - Handles API communication and response parsing

4. **Integration Layer**
   - External API calls via httpx
   - Authentication management
   - Network error handling

---

## Design Patterns

### Factory Design Pattern

The application implements the **Factory Design Pattern** to create provider instances without exposing creation logic to the client.

#### Pattern Components

1. **Abstract Product** (`LLMProvider`)
```python
class LLMProvider(ABC):
    def __init__(self, model: str):
        self.model = model
    
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass
```

**Purpose**: Defines the contract that all concrete providers must implement.

2. **Concrete Products** (`OpenAIProvider`, `AnthropicProvider`)
```python
class OpenAIProvider(LLMProvider):
    def generate_response(self, prompt: str) -> str:
        # OpenAI-specific implementation
        pass
```

**Purpose**: Implement provider-specific logic while adhering to the base contract.

3. **Factory** (`ProviderFactory`)
```python
class ProviderFactory:
    @staticmethod
    def get_provider(provider_name: str, model: str) -> LLMProvider:
        providers = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider
        }
        return providers[provider_name.lower()](model)
```

**Purpose**: Encapsulates provider instantiation logic.

#### Benefits of This Pattern

- **Loose Coupling**: Client code depends on abstractions, not concrete classes
- **Open/Closed Principle**: Open for extension (new providers), closed for modification
- **Single Responsibility**: Each provider handles only its specific implementation
- **Testability**: Easy to mock providers for testing
- **Scalability**: Adding new providers requires minimal changes

---

## Component Design

### 1. Base Provider (`providers/base.py`)

**Responsibility**: Define the contract for all LLM providers

**Key Design Decisions**:
- Uses ABC (Abstract Base Class) to enforce implementation
- Stores model name as instance variable for reuse
- Single abstract method keeps interface simple

**Design Rationale**:
- Python's ABC ensures compile-time checking of implementations
- Simple interface reduces cognitive load for implementers
- Storing model allows for provider-specific model validation in future

### 2. OpenAI Provider (`providers/openai_provider.py`)

**Responsibility**: Implement OpenAI Chat Completions API integration

**Key Features**:
- Environment-based API key management
- Message format conversion (user prompt → OpenAI format)
- Response parsing (extract content from choices)
- Timeout handling (30 seconds)

**API Contract**:
```
POST https://api.openai.com/v1/chat/completions
Headers: Authorization: Bearer <key>
Body: {
  "model": "gpt-4",
  "messages": [{"role": "user", "content": "prompt"}]
}
```

**Error Handling**:
- Validates API key presence on initialization
- Catches HTTP errors and wraps with descriptive messages
- Re-raises exceptions for upstream handling

### 3. Anthropic Provider (`providers/anthropic_provider.py`)

**Responsibility**: Implement Anthropic Messages API integration

**Key Features**:
- Custom header format (x-api-key, anthropic-version)
- Max tokens configuration (1024)
- Content array response parsing

**API Contract**:
```
POST https://api.anthropic.com/v1/messages
Headers: 
  x-api-key: <key>
  anthropic-version: 2023-06-01
Body: {
  "model": "claude-3-sonnet",
  "max_tokens": 1024,
  "messages": [{"role": "user", "content": "prompt"}]
}
```

**Design Choices**:
- Hard-coded max_tokens provides consistent behavior
- Version header ensures API stability
- Array access for content assumes single response

### 4. Provider Factory (`providers/factory.py`)

**Responsibility**: Create provider instances based on string identifiers

**Implementation Strategy**:
- Dictionary-based mapping for O(1) lookup
- Case-insensitive provider names
- Descriptive error messages for invalid providers

**Extensibility**:
```python
# Adding new provider:
providers = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "deepseek": DeepseekProvider,  # Just add here
}
```

### 5. FastAPI Application (`main.py`)

**Responsibility**: HTTP interface and request orchestration

**Key Components**:

1. **Request Model**:
```python
class ChatRequest(BaseModel):
    provider: str
    model: str
    prompt: str
```
- Leverages Pydantic for automatic validation
- Clear field names match user expectations

2. **Response Model**:
```python
class ChatResponse(BaseModel):
    provider: str
    model: str
    response: str
```
- Echoes input parameters for traceability
- Returns plain text response

3. **Endpoint Handler**:
```python
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    provider = ProviderFactory.get_provider(request.provider, request.model)
    response_text = provider.generate_response(request.prompt)
    return ChatResponse(...)
```

**Error Mapping**:
- `ValueError` (invalid provider) → HTTP 400
- Generic `Exception` (API errors) → HTTP 500

---

## Data Flow

### Request Lifecycle

```
1. Client sends POST /chat
   ↓
2. FastAPI receives request
   ↓
3. Pydantic validates request body
   ↓
4. ProviderFactory.get_provider() called
   ↓
5. Factory returns concrete provider instance
   ↓
6. provider.generate_response() called
   ↓
7. Provider makes HTTP call to LLM API
   ↓
8. Provider parses response
   ↓
9. Response wrapped in ChatResponse model
   ↓
10. JSON response sent to client
```

### Detailed Flow Example (OpenAI)

```python
# Client Request
POST /chat
{
  "provider": "openai",
  "model": "gpt-4",
  "prompt": "Tell me a joke"
}

# Internal Processing
1. Pydantic validates: ChatRequest object created
2. Factory called: ProviderFactory.get_provider("openai", "gpt-4")
3. OpenAIProvider instantiated with model="gpt-4"
4. generate_response("Tell me a joke") called
5. HTTP POST to OpenAI API:
   {
     "model": "gpt-4",
     "messages": [{"role": "user", "content": "Tell me a joke"}]
   }
6. OpenAI responds with completion
7. Extract: data["choices"][0]["message"]["content"]
8. Return text to endpoint
9. Wrap in ChatResponse

# Client Response
{
  "provider": "openai",
  "model": "gpt-4",
  "response": "Why did the chicken cross the road?..."
}
```

---

## Design Decisions

### 1. Why Factory Pattern?

**Decision**: Use Factory Pattern instead of simple if/else logic

**Rationale**:
- **Scalability**: Adding providers doesn't require modifying existing code
- **Testability**: Easy to mock factory for unit tests
- **Maintainability**: Provider logic isolated in separate classes
- **Professional Standard**: Industry-recognized pattern for this use case

**Alternative Considered**: Direct instantiation with if/else
```python
# Rejected approach
if provider == "openai":
    result = OpenAIProvider(model).generate_response(prompt)
elif provider == "anthropic":
    result = AnthropicProvider(model).generate_response(prompt)
```
**Why Rejected**: Violates Open/Closed Principle, harder to extend

### 2. Why httpx Over Official SDKs?

**Decision**: Use httpx for HTTP calls instead of official provider SDKs

**Rationale**:
- **Minimal Dependencies**: Keeps requirements.txt small
- **Unified Interface**: Single HTTP client for all providers
- **Transparency**: Direct API calls are easier to debug
- **Control**: Full control over request/response handling

**Trade-offs**:
- Less abstraction (must handle response parsing)
- No built-in retry logic
- Manual API version management

### 3. Synchronous vs Asynchronous

**Decision**: Use synchronous HTTP calls with httpx.Client

**Rationale**:
- **Simplicity**: Easier to understand and debug
- **Current Scale**: Single request doesn't benefit from async
- **API Constraints**: LLM APIs are inherently blocking

**Future Consideration**: Switch to async if supporting streaming responses

### 4. Error Handling Strategy

**Decision**: Simple try/except with HTTP status code mapping

**Rationale**:
- **Simplicity**: Requirements specified basic error handling
- **Client Clarity**: HTTP status codes are standard
- **Debugging**: Error messages preserved in exceptions

**Not Included** (but recommended for production):
- Structured logging
- Retry logic
- Rate limiting
- Circuit breakers

### 5. Environment Variables for API Keys

**Decision**: Use environment variables instead of configuration files

**Rationale**:
- **Security**: Prevents accidental commit of credentials
- **12-Factor App**: Follows best practices for configuration
- **Flexibility**: Easy to change without code modification
- **Cloud-Ready**: Works seamlessly with container orchestration


---

## Error Handling Strategy

### Current Implementation

```python
try:
    provider = ProviderFactory.get_provider(request.provider, request.model)
    response_text = provider.generate_response(request.prompt)
    return ChatResponse(...)
except ValueError as e:
    # Invalid provider name
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    # API errors, network issues, etc.
    raise HTTPException(status_code=500, detail=str(e))
```

### Error Categories

1. **Client Errors (400)**:
   - Invalid provider name
   - Unsupported model
   - Malformed request

2. **Server Errors (500)**:
   - Missing API keys
   - Network timeouts
   - API errors (rate limits, service unavailable)
   - Response parsing failures


---

## Security Considerations

### Current Implementation

1. **API Key Management**:
   - Stored in environment variables
   - Never logged or returned in responses
   - Validated on provider initialization

2. **Request Validation**:
   - Pydantic models enforce type safety
   - No SQL injection risk (no database)
   - No command injection (no shell execution)

### Current Limitations

1. **No Rate Limiting**: The application does not implement rate limiting
2. **No Authentication**: Endpoints are publicly accessible
3. **No Input Sanitization**: Prompt length and content are not validated beyond Pydantic type checking
4. **No Retry Logic**: Failed API calls are not automatically retried

---

## Coding Conventions

### File Organization

**Current Structure**:
```
llm-proxy/
├── main.py                      # FastAPI application entry point
├── providers/                   # Provider package
│   ├── __init__.py             # Package exports
│   ├── base.py                 # Abstract base class
│   ├── openai_provider.py      # OpenAI implementation
│   ├── anthropic_provider.py   # Anthropic implementation
│   └── factory.py              # Factory implementation
├── requirements.txt             # Python dependencies
├── .env.example                # Environment variable template
└── README.md                   # User documentation
```

### Naming Conventions

1. **Classes**: PascalCase (e.g., `LLMProvider`, `OpenAIProvider`)
2. **Functions/Methods**: snake_case (e.g., `generate_response`, `get_provider`)
3. **Constants**: UPPER_SNAKE_CASE (e.g., `OPENAI_API_KEY`)
4. **Files**: snake_case (e.g., `openai_provider.py`)

### Code Patterns

1. **Provider Implementation**:
   - Inherit from `LLMProvider`
   - Validate API key in `__init__`
   - Implement `generate_response(prompt: str) -> str`
   - Use httpx.Client with 30-second timeout
   - Wrap errors with descriptive messages

2. **Error Handling**:
   - Use `try/except` blocks in provider implementations
   - Raise `ValueError` for missing API keys
   - Raise generic `Exception` with descriptive messages for API errors
   - Let FastAPI endpoint handle HTTP status code mapping

3. **Environment Variables**:
   - Load with `os.getenv()`
   - Validate presence in provider `__init__`
   - Use pattern: `{PROVIDER}_API_KEY`

4. **Type Hints**:
   - All methods should include type hints
   - Use Pydantic models for request/response validation
   - Return type explicitly stated

### Documentation Standards

1. **Docstrings**: All classes and methods include docstrings
2. **Comments**: Inline comments explain non-obvious logic
3. **README**: User-facing documentation with examples

### Dependencies

**Current Dependencies**:
- `fastapi==0.109.0`: Web framework
- `uvicorn[standard]==0.27.0`: ASGI server
- `pydantic==2.5.3`: Data validation
- `httpx==0.26.0`: HTTP client
- `python-dotenv==1.0.0`: Environment variable management

**Rationale**: Minimal, well-maintained dependencies that serve specific purposes.

---

## Summary

This document captures the current state of the LLM Proxy application. When working with this codebase, AI agents should:

1. **Follow the Factory Pattern**: All new providers must inherit from `LLMProvider` and be registered in `ProviderFactory`
2. **Maintain Consistency**: Use the same error handling, timeout values, and code structure as existing providers
3. **Respect Abstractions**: Keep provider-specific logic within provider classes
4. **Update Documentation**: Any changes to architecture should be reflected in this document
5. **Preserve Simplicity**: The design prioritizes simplicity and clarity over advanced features

The architecture demonstrates clean separation of concerns through the Factory Design Pattern, making the codebase maintainable and understandable for both human developers and AI agents.
