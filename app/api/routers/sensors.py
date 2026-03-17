from fastapi import APIRouter, Depends, HTTPException

from app.db import get_session
from app.schemas import SensorUpdate
from app.services.sensor_service import get_sensors, update_sensor

router = APIRouter(prefix="/api/sensors", tags=["sensors"])


@router.get("")
def read_sensors(session=Depends(get_session)):
    return get_sensors(session)


@router.patch("/{sensor_id}")
def patch_sensor(sensor_id: str, payload: SensorUpdate, session=Depends(get_session)):
    sensor = update_sensor(session, sensor_id, payload.name)

    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    return {"status": "updated"}
