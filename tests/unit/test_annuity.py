import pytest
from fastapi.testclient import TestClient
from app.main import app, get_current_user, get_async_session
from app.models.annuity import Annuity
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_create_annuity_happy_path(monkeypatch):
    async def mock_get_current_user(token: str):
        return {"id": 123, "role": "user"}
    monkeypatch.setattr("app.dependencies.get_current_user", mock_get_current_user)

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.add = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    monkeypatch.setattr("app.dependencies.get_async_session", AsyncMock(return_value=mock_session))

    client = TestClient(app)
    response = client.post(
        "/annuities/premium",
        json={"principal": 10000, "term_years": 5, "annual_rate": 3},
        headers={"Authorization": "Bearer fake-token"}
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
    assert response.json()["premium"] == 2124.60
    mock_session.commit.assert_awaited()

@pytest.mark.asyncio
async def test_create_annuity_invalid_input(monkeypatch):
    async def mock_get_current_user(token: str):
        return {"id": 123, "role": "user"}
    monkeypatch.setattr("app.dependencies.get_current_user", mock_get_current_user)

    client = TestClient(app)
    response = client.post(
        "/annuities/premium",
        json={"principal": -100, "term_years": 5, "annual_rate": 3},
        headers={"Authorization": "Bearer fake-token"}
    )
    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.json()}"
    assert "greater than 0" in response.json()["detail"][0]["msg"]