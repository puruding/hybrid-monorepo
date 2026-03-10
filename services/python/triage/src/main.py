"""Main entry point for the Triage service."""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Triage Service",
    description="AI-powered incident triage and classification",
    version="0.1.0",
)


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    service: str


class TriageRequest(BaseModel):
    """Triage request model."""

    incident_id: str
    description: str
    severity: str | None = None


class TriageResponse(BaseModel):
    """Triage response model."""

    incident_id: str
    classification: str
    confidence: float
    recommended_actions: list[str]


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", service="triage")


@app.post("/triage", response_model=TriageResponse)
async def triage_incident(request: TriageRequest) -> TriageResponse:
    """Triage an incident and return classification."""
    # TODO: Implement actual AI classification
    return TriageResponse(
        incident_id=request.incident_id,
        classification="security_incident",
        confidence=0.85,
        recommended_actions=[
            "Isolate affected systems",
            "Collect forensic evidence",
            "Notify security team",
        ],
    )


def main() -> None:
    """Run the service."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8082)


if __name__ == "__main__":
    main()
