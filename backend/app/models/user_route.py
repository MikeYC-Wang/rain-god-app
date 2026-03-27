from datetime import datetime

from sqlalchemy import Column, Integer, Text, DateTime
from geoalchemy2 import Geometry

from app.database import Base


class UserRoute(Base):
    __tablename__ = "user_routes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Text, nullable=False, index=True)
    route_name = Column(Text, nullable=False)
    route_path = Column(Geometry("LINESTRING", srid=4326), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
