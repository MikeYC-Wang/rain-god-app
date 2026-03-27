"""Initialize database tables and PostGIS extension."""
from sqlalchemy import text

from app.database import engine, Base
from app.models import WeatherGrid, UserRoute  # noqa: F401 – register models


def init_db():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        conn.commit()
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")
