from sqlmodel import Session, select

from app.models import Sensor


def get_sensors(session: Session):
    return session.exec(select(Sensor)).all()


def update_sensor(session: Session, sensor_id: str, name: str):
    sensor = session.get(Sensor, sensor_id)

    if not sensor:
        return None

    sensor.name = name
    session.add(sensor)
    session.commit()

    return sensor
