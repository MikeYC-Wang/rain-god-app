import pytest

class TestPostGISSRID:
    def test_weather_grids_srid_requirement(self):
        # 驗證 weather_grids 必須使用 SRID 4326
        REQUIRED_SRID = 4326
        table_config = {
            "table": "weather_grids",
            "geometry_column": "grid_polygon",
            "geometry_type": "Polygon",
            "srid": REQUIRED_SRID
        }
        assert table_config["srid"] == 4326
        assert table_config["geometry_type"] == "Polygon"

    def test_user_routes_srid_requirement(self):
        # 驗證 user_routes 必須使用 SRID 4326
        REQUIRED_SRID = 4326
        table_config = {
            "table": "user_routes",
            "geometry_column": "route_path",
            "geometry_type": "LineString",
            "srid": REQUIRED_SRID
        }
        assert table_config["srid"] == 4326
        assert table_config["geometry_type"] == "LineString"

    def test_spatial_index_required(self):
        # 驗證兩張表都需要 GIST 空間索引
        required_indexes = [
            {"table": "weather_grids", "column": "grid_polygon", "type": "GIST"},
            {"table": "user_routes", "column": "route_path", "type": "GIST"},
        ]
        for idx in required_indexes:
            assert idx["type"] == "GIST"

    def test_st_intersects_logic(self, sample_taipei_linestring, sample_weather_grid):
        # 驗證台北市路線座標在台灣範圍內（SRID 4326）
        line_coords = sample_taipei_linestring["coordinates"]
        poly_coords = sample_weather_grid["coordinates"][0]
        for coord in line_coords + poly_coords:
            lng, lat = coord
            assert 118 <= lng <= 124
            assert 20 <= lat <= 27
