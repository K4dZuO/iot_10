from fastapi import APIRouter, Depends
from typing import Optional, List
from datetime import datetime

from app.db import get_session
from app.schemas import MeasurementBatch, MeasurementListResponse, MeasurementResponse
from app.services.measurement_service import ingest_measurements, get_measurements

router = APIRouter(prefix="/api/measurements", tags=["measurements"])


@router.post("", status_code=201)
def post_measurements(batch: MeasurementBatch, session=Depends(get_session)):
    ingest_measurements(batch, session)
    return {"status": "ok"}


@router.get("", response_model=MeasurementListResponse)
def read_measurements(
    sensorIds: Optional[List[str]] = None,
    from_: Optional[datetime] = None,
    to: Optional[datetime] = None,
    limit: int = 500,
    cursor: Optional[datetime] = None,
    session=Depends(get_session)
):
    results = get_measurements(session, sensorIds, from_, to, limit, cursor)

    data = [
        MeasurementResponse(
            sensorId=m.sensor_id,
            temperature=m.temperature,
            timestamp=m.timestamp
        ) for m in results
    ]

    next_cursor = results[-1].timestamp if results else None

    return {"data": data, "nextCursor": next_cursor}
