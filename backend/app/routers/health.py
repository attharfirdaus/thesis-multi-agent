from fastapi import APIRouter, Response, status

from app import db
from app.config import get_settings
from app.schemas import HealthOut

router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=HealthOut)
def healthz(response: Response) -> HealthOut:
    database = "ok"
    try:
        with db.plain_tx() as conn:
            conn.execute("select 1")
    except Exception:
        database = "error"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthOut(status="ok", env=get_settings().env, database=database)  # type: ignore[arg-type]
