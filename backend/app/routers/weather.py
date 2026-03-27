from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.cwa_crawler import run_crawler

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.post("/fetch")
def fetch_weather(db: Session = Depends(get_db)):
    """Trigger CWA forecast fetch and store results."""
    count = run_crawler(db)
    return {"status": "ok", "records_stored": count}
