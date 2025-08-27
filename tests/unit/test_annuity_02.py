import pytest
from fastapi.testclient import TestClient
from app.main import app, get_current_user, get_async_session
from app.models.annuity import Annuity, Base
from app.services.annuity import calculate_premium
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

@pytest.mark.asyncio
async def test_create_annuity_happy_path(monkeypatch):
    # Mock get_current_user
    async def mock_get_current_user(token: str):
        return {"id": 123, "role": "user"}
    monkeypatch.setattr("app.dependencies.get_current_user", mock_get_current_user)

    # Mock calculate_premium
    def mock_calculate_premium(principal: float, term_years: int, annual_rate: float) -> float:
        return 2124.60
    monkeypatch.setattr("app.services.annuity.calculate_premium", mock_calculate_premium)

    # Mock SQLAlchemy engine, session, and metadata
    mock_engine = MagicMock(spec=create_async_engine)
    mock_sessionmaker = MagicMock(spec=async_sessionmaker)
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.add = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_sessionmaker.return_value.__aenter__.return_value = mock_session
    monkeypatch.setattr("app.dependencies.get_engine", MagicMock(return_value=mock_engine))
    monkeypatch.setattr("app.dependencies.async_sessionmaker", MagicMock(return_value=mock_sessionmaker))
    mock_metadata = MagicMock()
    mock_metadata.create_all = MagicMock()
    mock_metadata.drop_all = MagicMock()
    monkeypatch.setattr("app.models.annuity.Base", MagicMock(metadata=mock_metadata))

    # Mock Annuity object
    mock_annuity = MagicMock(spec=Annuity)
    mock_annuity.id = 1
    mock_annuity.principal = 10000.0
    mock_annuity.term_years = 5
    mock_annuity.annual_rate = 3.0
    mock_annuity.premium = 2124.60
    mock_session.add.side_effect = lambda x: setattr(x, "id", 1)
    mock_session.refresh.side_effect = lambda x: x
    monkeypatch.setattr("app.models.annuity.Annuity", MagicMock(return_value=mock_annuity))

    client = TestClient(app)
    response = client.post(
        "/annuities/premium",
        json={"principal": 10000, "term_years": 5, "annual_rate": 3},
        headers={"Authorization": "Bearer fake-token"}
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
    assert response.json() == {
        "id": 1,
        "principal": 10000.0,
        "term_years": 5,
        "annual_rate": 3.0,
        "premium": 2124.60
    }
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