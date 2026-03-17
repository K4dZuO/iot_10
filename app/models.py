from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Sensor(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: Optional[str] = None
    device_id: str


class Measurement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sensor_id: str = Field(index=True)
    temperature: float
    timestamp: datetime = Field(index=True)
