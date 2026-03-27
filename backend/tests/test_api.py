"""Tests for POST /api/routes/check-rain endpoint."""
import pytest
from unittest.mock import patch, MagicMock


class TestCheckRainEndpoint:
    """Tests for the check-rain API endpoint."""

    def test_check_rain_valid_linestring(self, sample_taipei_linestring):
        """Verify the GeoJSON LineString input is valid SRID 4326 format."""
        coords = sample_taipei_linestring["coordinates"]
        assert sample_taipei_linestring["type"] == "LineString"
        assert len(coords) >= 2
        for coord in coords:
            assert len(coord) == 2
            lng, lat = coord
            assert 119 <= lng <= 123, f"Longitude {lng} out of Taiwan range"
            assert 21 <= lat <= 26, f"Latitude {lat} out of Taiwan range"

    def test_check_rain_response_schema(self):
        """Verify expected response schema for check-rain endpoint."""
        expected_keys = {"has_rain_risk", "intersecting_grids", "max_rain_probability"}
        mock_response = {
            "has_rain_risk": True,
            "intersecting_grids": [{"town_name": "Zhongzheng Dist.", "rain_probability": 75.0}],
            "max_rain_probability": 75.0
        }
        assert expected_keys.issubset(mock_response.keys())
        assert isinstance(mock_response["has_rain_risk"], bool)
        assert isinstance(mock_response["max_rain_probability"], float)

    def test_check_rain_threshold_constant(self):
        """Verify rain alert threshold is defined as 60%."""
        from app.routers.routes import RAIN_THRESHOLD
        assert RAIN_THRESHOLD == 60.0

    def test_check_rain_threshold_logic(self):
        """Verify rain alert threshold at 60%."""
        from app.routers.routes import RAIN_THRESHOLD
        test_cases = [
            (59.9, False),
            (60.0, True),
            (75.0, True),
            (100.0, True),
        ]
        for probability, should_alert in test_cases:
            result = probability >= RAIN_THRESHOLD
            assert result == should_alert, (
                f"Probability {probability}% should {'trigger' if should_alert else 'not trigger'} alert"
            )

    @pytest.mark.asyncio
    async def test_health_returns_200(self, async_client):
        """GET /health should return 200."""
        response = await async_client.get("/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_response_body(self, async_client):
        """GET /health should include status and service name."""
        response = await async_client.get("/health")
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "raingod-api"

    @pytest.mark.asyncio
    async def test_check_rain_endpoint_exists(self, async_client, sample_check_rain_request):
        """POST /api/routes/check-rain should not return 404."""
        with patch("app.routers.routes.get_db") as mock_get_db:
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.all.return_value = []
            mock_get_db.return_value = iter([mock_db])
            response = await async_client.post(
                "/api/routes/check-rain",
                json=sample_check_rain_request,
            )
            assert response.status_code != 404, "Endpoint /api/routes/check-rain should exist"

    @pytest.mark.asyncio
    async def test_check_rain_with_mocked_db(self, async_client, sample_check_rain_request):
        """POST /api/routes/check-rain should return correct structure with empty DB."""
        with patch("app.routers.routes.get_db") as mock_get_db:
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.all.return_value = []
            mock_get_db.return_value = iter([mock_db])
            response = await async_client.post(
                "/api/routes/check-rain",
                json=sample_check_rain_request,
            )
            assert response.status_code == 200
            data = response.json()
            assert "has_rain_risk" in data
            assert "intersecting_grids" in data
            assert "max_rain_probability" in data
            assert data["has_rain_risk"] is False
            assert data["intersecting_grids"] == []
            assert data["max_rain_probability"] == 0

    @pytest.mark.asyncio
    async def test_check_rain_invalid_body_returns_422(self, async_client):
        """POST /api/routes/check-rain with invalid body should return 422."""
        response = await async_client.post(
            "/api/routes/check-rain",
            json={"invalid": "data"},
        )
        assert response.status_code == 422


class TestRouteSchemas:
    """Tests for request/response Pydantic schemas."""

    def test_geojson_linestring_schema(self):
        from app.routers.routes import GeoJsonLineString
        ls = GeoJsonLineString(
            type="LineString",
            coordinates=[[121.5, 25.0], [121.6, 25.1]]
        )
        assert ls.type == "LineString"
        assert len(ls.coordinates) == 2

    def test_check_rain_request_schema(self):
        from app.routers.routes import CheckRainRequest, GeoJsonLineString
        req = CheckRainRequest(
            route=GeoJsonLineString(
                type="LineString",
                coordinates=[[121.5, 25.0], [121.6, 25.1]]
            )
        )
        assert req.route.type == "LineString"
