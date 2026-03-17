from sqlmodel import Session, select
from datetime import datetime
from typing import List, Optional

from app.models import Measurement, Sensor


def ingest_measurements(batch, session: Session):
    for m in batch.measurements:

        # фильтр очевидных ошибок датчика
        if m.temperature in (-127, 85):
            continue

        sensor = session.get(Sensor, m.sensorId)
        if not sensor:
            sensor = Sensor(id=m.sensorId, device_id=batch.deviceId)
            session.add(sensor)

        timestamp = m.timestamp or datetime.utcnow()

        # простая идемпотентность
        exists = session.exec(
            select(Measurement).where(
                Measurement.sensor_id == m.sensorId,
                Measurement.timestamp == timestamp
            )
        ).first()

        if exists:
            continue

        measurement = Measurement(
            sensor_id=m.sensorId,
            temperature=m.temperature,
            timestamp=timestamp
        )
        session.add(measurement)

    session.commit()


def get_measurements(session: Session, sensor_ids: Optional[List[str]], from_, to, limit: int, cursor):
    query = select(Measurement)

    if sensor_ids:
        query = query.where(Measurement.sensor_id.in_(sensor_ids))

    if from_:
        query = query.where(Measurement.timestamp >= from_)

    if to:
        query = query.where(Measurement.timestamp <= to)

    if cursor:
        query = query.where(Measurement.timestamp < cursor)

    query = query.order_by(Measurement.timestamp.desc()).limit(limit)

    return session.exec(query).all()


