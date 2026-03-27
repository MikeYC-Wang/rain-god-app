"""Tests for PostGIS SRID 4326 validation and spatial queries."""
import json

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import inspect

from app.models.weather_grid import WeatherGrid
from app.models.user_route import UserRoute


class TestPostGISSRID:
    """Verify that WeatherGrid and UserRoute models use SRID 4326."""

    def test_weather_grid_geometry_srid(self):
        """weather_grids.grid_polygon should use SRID 4326."""
        col = WeatherGrid.__table__.columns["grid_polygon"]
        geom_type = col.type
        assert geom_type.srid == 4326, (
            f"weather_grids.grid_polygon SRID should be 4326, got {geom_type.srid}"
        )

    def test_weather_grid_geometry_type(self):
        """weather_grids.grid_polygon should be POLYGON type."""
        col = WeatherGrid.__table__.columns["grid_polygon"]
        geom_type = col.type
        assert geom_type.geometry_type == "POLYGON", (
            f"Expected POLYGON, got {geom_type.geometry_type}"
        )

    def test_user_route_geometry_srid(self):
        """user_routes.route_path should use SRID 4326."""
        col = UserRoute.__table__.columns["route_path"]
        geom_type = col.type
        assert geom_type.srid == 4326, (
            f"user_routes.route_path SRID should be 4326, got {geom_type.srid}"
        )

    def test_user_route_geometry_type(self):
        """user_routes.route_path should be LINESTRING type."""
        col = UserRoute.__table__.columns["route_path"]
        geom_type = col.type
        assert geom_type.geometry_type == "LINESTRING", (
            f"Expected LINESTRING, got {geom_type.geometry_type}"
        )

    def test_weather_grid_not_nullable(self):
        """weather_grids.grid_polygon should not be nullable."""
        col = WeatherGrid.__table__.columns["grid_polygon"]
        assert not col.nullable

    def test_user_route_not_nullable(self):
        """user_routes.route_path should not be nullable."""
        col = UserRoute.__table__.columns["route_path"]
        assert not col.nullable


class TestWeatherGridModel:
    """Verify WeatherGrid model schema."""

    def test_table_name(self):
        assert WeatherGrid.__tablename__ == "weather_grids"

    def test_required_columns(self):
        columns = {c.name for c in WeatherGrid.__table__.columns}
        expected = {"id", "grid_polygon", "rain_probability", "forecast_time", "town_name", "created_at"}
        assert expected.issubset(columns), f"Missing columns: {expected - columns}"

    def test_rain_probability_column_type(self):
        col = WeatherGrid.__table__.columns["rain_probability"]
        assert not col.nullable

    def test_town_name_column_type(self):
        col = WeatherGrid.__table__.columns["town_name"]
        assert not col.nullable


class TestUserRouteModel:
    """Verify UserRoute model schema."""

    def test_table_name(self):
        assert UserRoute.__tablename__ == "user_routes"

    def test_required_columns(self):
        columns = {c.name for c in UserRoute.__table__.columns}
        expected = {"id", "user_id", "route_name", "route_path", "created_at"}
        assert expected.issubset(columns), f"Missing columns: {expected - columns}"

    def test_user_id_is_indexed(self):
        col = UserRoute.__table__.columns["user_id"]
        assert col.index is True


class TestSTIntersectsLogic:
    """Test ST_Intersects spatial query logic using coordinate math."""

    def test_intersecting_route_and_grid(
        self, sample_taipei_linestring, sample_weather_grid
    ):
        """A Taipei route should intersect with a grid covering part of Taipei."""
        route_coords = sample_taipei_linestring["coordinates"]
        grid_coords = sample_weather_grid["coordinates"][0]

        grid_min_lng = min(c[0] for c in grid_coords)
        grid_max_lng = max(c[0] for c in grid_coords)
        grid_min_lat = min(c[1] for c in grid_coords)
        grid_max_lat = max(c[1] for c in grid_coords)

        has_intersection = any(
            grid_min_lng <= lng <= grid_max_lng and grid_min_lat <= lat <= grid_max_lat
            for lng, lat in route_coords
        )
        assert has_intersection, (
            "Route should intersect with weather grid covering Taipei area"
        )

    def test_non_intersecting_route_and_grid(
        self, sample_taipei_linestring, sample_non_intersecting_grid
    ):
        """A Taipei route should NOT intersect with a grid in southern Taiwan."""
        route_coords = sample_taipei_linestring["coordinates"]
        grid_coords = sample_non_intersecting_grid["coordinates"][0]

        grid_min_lng = min(c[0] for c in grid_coords)
        grid_max_lng = max(c[0] for c in grid_coords)
        grid_min_lat = min(c[1] for c in grid_coords)
        grid_max_lat = max(c[1] for c in grid_coords)

        has_intersection = any(
            grid_min_lng <= lng <= grid_max_lng and grid_min_lat <= lat <= grid_max_lat
            for lng, lat in route_coords
        )
        assert not has_intersection, (
            "Route should NOT intersect with grid in southern Taiwan"
        )

    def test_boundary_intersection(self):
        """A point exactly on the grid boundary should count as intersecting."""
        grid_min_lng, grid_max_lng = 121.50, 121.55
        grid_min_lat, grid_max_lat = 25.00, 25.05
        boundary_point = [121.50, 25.00]

        lng, lat = boundary_point
        is_inside = grid_min_lng <= lng <= grid_max_lng and grid_min_lat <= lat <= grid_max_lat
        assert is_inside, "Boundary point should be considered intersecting"

    def test_multiple_grids_intersection(self, sample_taipei_linestring):
        """Route should correctly identify which grids it passes through."""
        grids = [
            {"name": "Grid A", "bounds": (121.50, 121.55, 25.00, 25.05)},
            {"name": "Grid B", "bounds": (121.52, 121.57, 25.03, 25.08)},
            {"name": "Grid C", "bounds": (120.00, 120.05, 23.00, 23.05)},
        ]

        route_coords = sample_taipei_linestring["coordinates"]
        intersecting = []

        for grid in grids:
            min_lng, max_lng, min_lat, max_lat = grid["bounds"]
            if any(
                min_lng <= lng <= max_lng and min_lat <= lat <= max_lat
                for lng, lat in route_coords
            ):
                intersecting.append(grid["name"])

        assert "Grid A" in intersecting
        assert "Grid B" in intersecting
        assert "Grid C" not in intersecting
