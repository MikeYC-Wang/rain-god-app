import json
from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from app.main import app
from app.database import Base, get_db


# ---------------------------------------------------------------------------
# Test DB fixtures (uses SQLite for unit tests, PostGIS tests use mock)
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_taipei_linestring():
    """Taipei commute route: Taipei 101 -> NTU -> Wanhua."""
    return {
        "type": "LineString",
        "coordinates": [
            [121.5654, 25.0330],
            [121.5308, 25.0478],
            [121.5023, 25.0624]
        ]
    }


@pytest.fixture
def sample_short_linestring():
    """A short route with only 2 points."""
    return {
        "type": "LineString",
        "coordinates": [
            [121.5654, 25.0330],
            [121.5308, 25.0478]
        ]
    }


@pytest.fixture
def sample_weather_grid():
    """Weather grid polygon covering part of Taipei."""
    return {
        "type": "Polygon",
        "coordinates": [[
            [121.50, 25.00],
            [121.55, 25.00],
            [121.55, 25.05],
            [121.50, 25.05],
            [121.50, 25.00]
        ]]
    }


@pytest.fixture
def sample_non_intersecting_grid():
    """Weather grid polygon that does NOT intersect with the Taipei route."""
    return {
        "type": "Polygon",
        "coordinates": [[
            [120.00, 23.00],
            [120.05, 23.00],
            [120.05, 23.05],
            [120.00, 23.05],
            [120.00, 23.00]
        ]]
    }


@pytest.fixture
def sample_cwa_response():
    """Mock CWA (Central Weather Administration) API response for township forecasts."""
    return {
        "success": "true",
        "records": {
            "locations": [
                {
                    "datasetDescription": "Township forecast",
                    "location": [
                        {
                            "locationName": "Zhongzheng Dist.",
                            "geocode": "6300500",
                            "lat": "25.0324",
                            "lon": "121.5187",
                            "weatherElement": [
                                {
                                    "elementName": "PoP12h",
                                    "time": [
                                        {
                                            "startTime": "2026-03-27 06:00:00",
                                            "endTime": "2026-03-27 18:00:00",
                                            "elementValue": [
                                                {"value": "80"}
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "locationName": "Da'an Dist.",
                            "geocode": "6300600",
                            "lat": "25.0266",
                            "lon": "121.5433",
                            "weatherElement": [
                                {
                                    "elementName": "PoP12h",
                                    "time": [
                                        {
                                            "startTime": "2026-03-27 06:00:00",
                                            "endTime": "2026-03-27 18:00:00",
                                            "elementValue": [
                                                {"value": "30"}
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }


@pytest.fixture
def sample_check_rain_request(sample_taipei_linestring):
    """Standard request body for POST /api/routes/check-rain."""
    return {
        "route": sample_taipei_linestring
    }


@pytest_asyncio.fixture
async def async_client():
    """Async HTTP client for testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
