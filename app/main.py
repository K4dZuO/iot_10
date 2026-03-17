from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel

from app.db import engine
from app.api.routers import measurements, sensors


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    SQLModel.metadata.create_all(engine)
    yield
    # shutdown (если понадобится — добавить сюда)


app = FastAPI(lifespan=lifespan)

app.include_router(measurements.router)
app.include_router(sensors.router)
