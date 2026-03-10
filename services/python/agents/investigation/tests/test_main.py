"""Tests for main module."""

import pytest

from src.main import InvestigationAgent, InvestigationStatus


@pytest.fixture
def agent() -> InvestigationAgent:
    """Create test agent."""
    return InvestigationAgent()


@pytest.mark.asyncio
async def test_investigate(agent: InvestigationAgent) -> None:
    """Test investigation."""
    result = await agent.investigate(
        incident_id="INC-001",
        evidence=["log1.txt", "log2.txt"],
    )
    assert result.investigation_id == "INV-INC-001"
    assert result.status == InvestigationStatus.COMPLETED
    assert len(result.findings) > 0
    assert len(result.recommendations) > 0
    assert 0 <= result.confidence <= 1
