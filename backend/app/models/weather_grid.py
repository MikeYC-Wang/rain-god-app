from datetime import datetime

from sqlalchemy import Column, Integer, Float, Text, DateTime
from geoalchemy2 import Geometry

from app.database import Base


class WeatherGrid(Base):
    __tablename__ = "weather_grids"

    id = Column(Integer, primary_key=True, index=True)
    grid_polygon = Column(Geometry("POLYGON", srid=4326), nullable=False)
    rain_probability = Column(Float, nullable=False)
    forecast_time = Column(DateTime, nullable=False)
    town_name = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
