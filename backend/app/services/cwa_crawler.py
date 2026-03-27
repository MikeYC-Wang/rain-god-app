"""CWA (Central Weather Administration) forecast crawler.

Fetches township-level weather forecasts from the open-data API
and upserts rain probability data into the weather_grids table.
"""
import logging
from datetime import datetime

import httpx
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.config import settings
from app.models.weather_grid import WeatherGrid

logger = logging.getLogger(__name__)

CWA_FORECAST_URL = (
    "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
)

# Approximate bounding-box size (degrees) for each township centroid.
# CWA data provides town-level forecasts, not polygons, so we generate a
# small rectangular polygon around a nominal centroid for spatial queries.
GRID_HALF_SIZE = 0.02  # ~2 km


def _make_polygon_wkt(lon: float, lat: float, half: float = GRID_HALF_SIZE) -> str:
    """Create a WKT POLYGON string from a centre point."""
    return (
        f"SRID=4326;POLYGON(("
        f"{lon - half} {lat - half},"
        f"{lon + half} {lat - half},"
        f"{lon + half} {lat + half},"
        f"{lon - half} {lat + half},"
        f"{lon - half} {lat - half}"
        f"))"
    )


# Rough centroids for each county/city in Taiwan (used when CWA data does
# not include coordinates).  This is a simplified mapping; a production
# system would maintain a full township geocode table.
_COUNTY_CENTROIDS: dict[str, tuple[float, float]] = {
    "臺北市": (121.5654, 25.0330),
    "新北市": (121.4628, 25.0120),
    "桃園市": (121.3010, 24.9936),
    "臺中市": (120.6736, 24.1477),
    "臺南市": (120.2270, 23.0051),
    "高雄市": (120.3014, 22.6273),
    "基隆市": (121.7419, 25.1276),
    "新竹市": (120.9647, 24.8138),
    "新竹縣": (121.0042, 24.8386),
    "苗栗縣": (120.8214, 24.5602),
    "彰化縣": (120.5161, 24.0518),
    "南投縣": (120.6874, 23.7610),
    "雲林縣": (120.4312, 23.7092),
    "嘉義市": (120.4491, 23.4800),
    "嘉義縣": (120.5740, 23.4518),
    "屏東縣": (120.4879, 22.5519),
    "宜蘭縣": (121.7535, 24.7021),
    "花蓮縣": (121.6014, 23.9872),
    "臺東縣": (121.1466, 22.7972),
    "澎湖縣": (119.5793, 23.5711),
    "金門縣": (118.3176, 24.4324),
    "連江縣": (119.9399, 26.1605),
}


def fetch_forecast() -> dict:
    """Call CWA open-data API and return the JSON response."""
    params = {
        "Authorization": settings.CWA_API_KEY,
        "format": "JSON",
    }
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            resp = httpx.get(CWA_FORECAST_URL, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            logger.warning("CWA API attempt %d/%d failed: %s", attempt, max_retries, exc)
            if attempt == max_retries:
                raise
    return {}


def parse_and_store(data: dict, db: Session) -> int:
    """Parse CWA JSON and upsert weather_grids rows. Returns row count."""
    records = data.get("records", {})
    locations = records.get("location", [])
    if not locations:
        logger.warning("No location data in CWA response")
        return 0

    # Clear old forecast data before inserting fresh data
    db.execute(delete(WeatherGrid))

    count = 0
    for loc in locations:
        town_name = loc.get("locationName", "")
        centroid = _COUNTY_CENTROIDS.get(town_name)
        if centroid is None:
            logger.debug("No centroid for %s, skipping", town_name)
            continue

        lon, lat = centroid

        # Extract rain probability from weather elements
        weather_elements = loc.get("weatherElement", [])
        rain_prob = _extract_rain_probability(weather_elements)
        forecast_time = _extract_forecast_time(weather_elements)

        if rain_prob is None:
            continue

        grid = WeatherGrid(
            grid_polygon=_make_polygon_wkt(lon, lat),
            rain_probability=rain_prob,
            forecast_time=forecast_time or datetime.utcnow(),
            town_name=town_name,
        )
        db.add(grid)
        count += 1

    db.commit()
    logger.info("Stored %d weather grid records", count)
    return count


def _extract_rain_probability(elements: list) -> float | None:
    """Return the max rain probability (PoP) from weather elements."""
    for el in elements:
        if el.get("elementName") == "PoP":
            times = el.get("time", [])
            probs = []
            for t in times:
                param = t.get("parameter", {})
                val = param.get("parameterName")
                if val is not None:
                    try:
                        probs.append(float(val))
                    except (ValueError, TypeError):
                        pass
            if probs:
                return max(probs)
    return None


def _extract_forecast_time(elements: list) -> datetime | None:
    """Return the start time of the first forecast period."""
    for el in elements:
        if el.get("elementName") == "PoP":
            times = el.get("time", [])
            if times:
                start = times[0].get("startTime")
                if start:
                    try:
                        return datetime.fromisoformat(start)
                    except ValueError:
                        pass
    return None


def run_crawler(db: Session) -> int:
    """Main entry: fetch forecast and store. Returns record count."""
    data = fetch_forecast()
    return parse_and_store(data, db)
