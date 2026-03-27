-- 001_create_tables.sql
-- Rain God Companion - Initial schema with PostGIS

CREATE EXTENSION IF NOT EXISTS postgis;

-- Weather forecast grid polygons
CREATE TABLE IF NOT EXISTS weather_grids (
    id SERIAL PRIMARY KEY,
    grid_polygon GEOMETRY(Polygon, 4326) NOT NULL,
    rain_probability FLOAT NOT NULL,
    forecast_time TIMESTAMP NOT NULL,
    town_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User commute routes
CREATE TABLE IF NOT EXISTS user_routes (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    route_name TEXT NOT NULL,
    route_path GEOMETRY(LineString, 4326) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Spatial indexes for ST_Intersects performance
CREATE INDEX IF NOT EXISTS idx_weather_grids_polygon
    ON weather_grids USING GIST (grid_polygon);

CREATE INDEX IF NOT EXISTS idx_user_routes_path
    ON user_routes USING GIST (route_path);

-- B-tree indexes
CREATE INDEX IF NOT EXISTS idx_user_routes_user_id
    ON user_routes (user_id);

CREATE INDEX IF NOT EXISTS idx_weather_grids_forecast_time
    ON weather_grids (forecast_time);
