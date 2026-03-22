from sqlmodel import SQLModel
from typing import Optional, List
from datetime import datetime


class MeasurementInput(SQLModel):
    sensorId: str
    temperature: float
    humidity: Optional[float] = None
    timestamp: Optional[datetime] = None


class MeasurementBatch(SQLModel):
    deviceId: str
    measurements: List[MeasurementInput]


class MeasurementResponse(SQLModel):
    sensorId: str
    temperature: float
    timestamp: datetime


class MeasurementListResponse(SQLModel):
    data: List[MeasurementResponse]
    nextCursor: Optional[datetime]


class SensorUpdate(SQLModel):
    name: Optional[str]
    type: Optional[str]
