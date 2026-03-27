"""Tests for CWA (Central Weather Administration) crawler with mocked API responses."""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

import httpx

from app.services.cwa_crawler import (
    _make_polygon_wkt,
    _extract_rain_probability,
    _extract_forecast_time,
    parse_and_store,
    fetch_forecast,
    GRID_HALF_SIZE,
    _COUNTY_CENTROIDS,
)


class TestMakePolygonWKT:
    """Test polygon WKT generation from centroids."""

    def test_basic_polygon(self):
        wkt = _make_polygon_wkt(121.5, 25.0)
        assert wkt.startswith("SRID=4326;POLYGON((")
        assert wkt.endswith("))")

    def test_polygon_contains_srid(self):
        wkt = _make_polygon_wkt(121.5, 25.0)
        assert "SRID=4326" in wkt

    def test_polygon_is_closed(self):
        """First and last coordinate should be the same (closed polygon)."""
        wkt = _make_polygon_wkt(121.5, 25.0)
        # Extract coordinate pairs
        coords_str = wkt.split("((")[1].rstrip("))")
        pairs = [p.strip() for p in coords_str.split(",")]
        assert pairs[0] == pairs[-1], "Polygon should be closed"

    def test_polygon_has_5_points(self):
        """A rectangular polygon has 5 points (4 corners + closing point)."""
        wkt = _make_polygon_wkt(121.5, 25.0)
        coords_str = wkt.split("((")[1].rstrip("))")
        pairs = [p.strip() for p in coords_str.split(",")]
        assert len(pairs) == 5

    def test_custom_half_size(self):
        wkt = _make_polygon_wkt(121.5, 25.0, half=0.05)
        assert "121.45" in wkt
        assert "121.55" in wkt


class TestExtractRainProbability:
    """Test rain probability extraction from CWA weather elements."""

    def test_extract_pop(self):
        elements = [
            {
                "elementName": "PoP",
                "time": [
                    {"parameter": {"parameterName": "70"}},
                    {"parameter": {"parameterName": "80"}},
                ]
            }
        ]
        result = _extract_rain_probability(elements)
        assert result == 80.0  # max of 70, 80

    def test_no_pop_element(self):
        elements = [
            {"elementName": "Wx", "time": []}
        ]
        result = _extract_rain_probability(elements)
        assert result is None

    def test_empty_elements(self):
        result = _extract_rain_probability([])
        assert result is None

    def test_invalid_value(self):
        elements = [
            {
                "elementName": "PoP",
                "time": [
                    {"parameter": {"parameterName": "N/A"}}
                ]
            }
        ]
        result = _extract_rain_probability(elements)
        assert result is None

    def test_mixed_valid_invalid(self):
        elements = [
            {
                "elementName": "PoP",
                "time": [
                    {"parameter": {"parameterName": "60"}},
                    {"parameter": {"parameterName": "invalid"}},
                ]
            }
        ]
        result = _extract_rain_probability(elements)
        assert result == 60.0


class TestExtractForecastTime:
    """Test forecast time extraction."""

    def test_valid_time(self):
        elements = [
            {
                "elementName": "PoP",
                "time": [
                    {"startTime": "2026-03-27 06:00:00"}
                ]
            }
        ]
        result = _extract_forecast_time(elements)
        assert isinstance(result, datetime)

    def test_no_time(self):
        elements = [
            {"elementName": "PoP", "time": []}
        ]
        result = _extract_forecast_time(elements)
        assert result is None

    def test_no_pop_element(self):
        elements = [
            {"elementName": "Wx", "time": [{"startTime": "2026-03-27 06:00:00"}]}
        ]
        result = _extract_forecast_time(elements)
        assert result is None


class TestParseAndStore:
    """Test CWA data parsing and DB storage."""

    def test_empty_response(self):
        mock_db = MagicMock()
        count = parse_and_store({}, mock_db)
        assert count == 0

    def test_no_locations(self):
        mock_db = MagicMock()
        data = {"records": {"location": []}}
        count = parse_and_store(data, mock_db)
        assert count == 0

    def test_valid_location_stored(self):
        mock_db = MagicMock()
        data = {
            "records": {
                "location": [
                    {
                        "locationName": "\u81fa\u5317\u5e02",
                        "weatherElement": [
                            {
                                "elementName": "PoP",
                                "time": [
                                    {
                                        "startTime": "2026-03-27 06:00:00",
                                        "parameter": {"parameterName": "70"}
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        count = parse_and_store(data, mock_db)
        assert count == 1
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_unknown_location_skipped(self):
        mock_db = MagicMock()
        data = {
            "records": {
                "location": [
                    {
                        "locationName": "UnknownCity",
                        "weatherElement": [
                            {
                                "elementName": "PoP",
                                "time": [
                                    {
                                        "startTime": "2026-03-27 06:00:00",
                                        "parameter": {"parameterName": "70"}
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        count = parse_and_store(data, mock_db)
        assert count == 0


class TestCountyCentroids:
    """Verify county centroid data."""

    def test_all_centroids_in_taiwan_range(self):
        for name, (lon, lat) in _COUNTY_CENTROIDS.items():
            assert 118 <= lon <= 123, f"{name} longitude {lon} out of range"
            assert 21 <= lat <= 27, f"{name} latitude {lat} out of range"

    def test_taipei_centroid_exists(self):
        assert "\u81fa\u5317\u5e02" in _COUNTY_CENTROIDS

    def test_centroid_count(self):
        assert len(_COUNTY_CENTROIDS) >= 20, "Should have centroids for all counties/cities"


class TestFetchForecast:
    """Test CWA API fetch with mocked HTTP."""

    def test_successful_fetch(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"success": "true", "records": {"location": []}}
        mock_resp.raise_for_status.return_value = None

        with patch("app.services.cwa_crawler.httpx.get", return_value=mock_resp):
            result = fetch_forecast()
            assert result["success"] == "true"

    def test_retry_on_failure(self):
        """Should retry up to 3 times on failure."""
        mock_resp_fail = MagicMock()
        mock_resp_fail.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500", request=MagicMock(), response=MagicMock()
        )

        with patch("app.services.cwa_crawler.httpx.get", return_value=mock_resp_fail):
            with pytest.raises(httpx.HTTPStatusError):
                fetch_forecast()

    def test_timeout_handling(self):
        with patch(
            "app.services.cwa_crawler.httpx.get",
            side_effect=httpx.RequestError("timeout"),
        ):
            with pytest.raises(httpx.RequestError):
                fetch_forecast()
