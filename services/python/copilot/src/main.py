"""Main entry point for the Copilot service."""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Copilot Service",
    description="AI-powered security operations copilot",
    version="0.1.0",
)


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    service: str


class ChatRequest(BaseModel):
    """Chat request model."""

    session_id: str
    message: str
    context: dict | None = None


class ChatResponse(BaseModel):
    """Chat response model."""

    session_id: str
    response: str
    suggestions: list[str]


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", service="copilot")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a chat message and return AI response."""
    # TODO: Implement actual AI chat with OpenAI
    return ChatResponse(
        session_id=request.session_id,
        response=f"I received your message: {request.message}",
        suggestions=[
            "Would you like me to analyze the logs?",
            "Should I check for similar incidents?",
            "Do you want me to create a report?",
        ],
    )


def main() -> None:
    """Run the service."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8083)


if __name__ == "__main__":
    main()
