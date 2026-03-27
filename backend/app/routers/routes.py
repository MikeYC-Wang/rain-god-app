from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_route import UserRoute
from app.models.weather_grid import WeatherGrid

router = APIRouter(prefix="/api/routes", tags=["routes"])

RAIN_THRESHOLD = 60.0  # percentage


# ---------- Schemas ----------

class GeoJsonLineString(BaseModel):
    type: str = "LineString"
    coordinates: list[list[float]]


class CheckRainRequest(BaseModel):
    route: GeoJsonLineString


class RouteCreate(BaseModel):
    user_id: str
    route_name: str
    route: GeoJsonLineString


class RouteOut(BaseModel):
    id: int
    user_id: str
    route_name: str
    created_at: Any


# ---------- Endpoints ----------

@router.post("/check-rain")
def check_rain(body: CheckRainRequest, db: Session = Depends(get_db)):
    """Check if a route intersects high-rain-probability grids (>= 60%)."""
    coords = body.route.coordinates
    coord_str = ", ".join(f"{lon} {lat}" for lon, lat in coords)
    route_wkt = f"SRID=4326;LINESTRING({coord_str})"

    route_geom = func.ST_GeomFromEWKT(route_wkt)

    grids = (
        db.query(WeatherGrid)
        .filter(
            func.ST_Intersects(WeatherGrid.grid_polygon, route_geom),
            WeatherGrid.rain_probability >= RAIN_THRESHOLD,
        )
        .all()
    )

    result_grids = [
        {
            "id": g.id,
            "town_name": g.town_name,
            "rain_probability": g.rain_probability,
            "forecast_time": g.forecast_time.isoformat() if g.forecast_time else None,
        }
        for g in grids
    ]

    max_prob = max((g.rain_probability for g in grids), default=0)

    return {
        "has_rain_risk": len(grids) > 0,
        "max_rain_probability": max_prob,
        "intersecting_grids": result_grids,
    }


@router.get("/{user_id}")
def list_routes(user_id: str, db: Session = Depends(get_db)):
    """List all saved routes for a user."""
    routes = (
        db.query(UserRoute)
        .filter(UserRoute.user_id == user_id)
        .order_by(UserRoute.created_at.desc())
        .all()
    )
    return [
        RouteOut(
            id=r.id,
            user_id=r.user_id,
            route_name=r.route_name,
            created_at=r.created_at.isoformat() if r.created_at else None,
        )
        for r in routes
    ]


@router.post("")
def create_route(body: RouteCreate, db: Session = Depends(get_db)):
    """Save a new user route."""
    coords = body.route.coordinates
    coord_str = ", ".join(f"{lon} {lat}" for lon, lat in coords)
    route_wkt = f"SRID=4326;LINESTRING({coord_str})"

    route = UserRoute(
        user_id=body.user_id,
        route_name=body.route_name,
        route_path=route_wkt,
    )
    db.add(route)
    db.commit()
    db.refresh(route)

    return {"id": route.id, "status": "created"}
