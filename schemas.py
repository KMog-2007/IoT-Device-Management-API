from pydantic import BaseModel
from datetime import datetime


class DeviceCreate(BaseModel):
    name: str
    device_type: str
    location: str
    status: str = "active"


class DeviceResponse(BaseModel):
    id: int
    name: str
    device_type: str
    location: str
    status: str

    class Config:
        from_attributes = True


class SensorReadingCreate(BaseModel):
    sensor_type: str
    value: float
    unit: str


class SensorReadingResponse(BaseModel):
    id: int
    device_id: int
    sensor_type: str
    value: float
    unit: str
    timestamp: datetime

    class Config:
        from_attributes = True