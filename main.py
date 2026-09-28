from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, SessionLocal


# Create database tables
models.Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="IoT Device Management API",
    description="A REST API for managing IoT devices and sensor readings.",
    version="1.0.0"
)


# API Authentication
security = HTTPBearer()

API_TOKEN = "iot-secret-123"


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )

    return credentials.credentials


# Database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to the IoT Device Management API!",
        "status": "Running"
    }


# About endpoint
@app.get("/about")
def about():
    return {
        "project": "IoT Device Management API",
        "framework": "FastAPI",
        "database": "SQLite"
    }


# CREATE - Add a new device
@app.post(
    "/devices",
    response_model=schemas.DeviceResponse,
    dependencies=[Depends(verify_token)]
)
def create_device(
    device: schemas.DeviceCreate,
    db: Session = Depends(get_db)
):
    new_device = models.Device(
        name=device.name,
        device_type=device.device_type,
        location=device.location,
        status=device.status
    )

    db.add(new_device)
    db.commit()
    db.refresh(new_device)

    return new_device


# READ - Get all devices
@app.get(
    "/devices",
    response_model=list[schemas.DeviceResponse],
    dependencies=[Depends(verify_token)]
)
def get_devices(db: Session = Depends(get_db)):
    devices = db.query(models.Device).all()
    return devices


# READ - Get one device by ID
@app.get(
    "/devices/{device_id}",
    response_model=schemas.DeviceResponse,
    dependencies=[Depends(verify_token)]
)
def get_device(
    device_id: int,
    db: Session = Depends(get_db)
):
    device = db.query(models.Device).filter(
        models.Device.id == device_id
    ).first()

    if device is None:
        raise HTTPException(
            status_code=404,
            detail="Device not found"
        )

    return device


# UPDATE - Update an existing device
@app.put(
    "/devices/{device_id}",
    response_model=schemas.DeviceResponse,
    dependencies=[Depends(verify_token)]
)
def update_device(
    device_id: int,
    device: schemas.DeviceCreate,
    db: Session = Depends(get_db)
):
    existing_device = db.query(models.Device).filter(
        models.Device.id == device_id
    ).first()

    if existing_device is None:
        raise HTTPException(
            status_code=404,
            detail="Device not found"
        )

    existing_device.name = device.name
    existing_device.device_type = device.device_type
    existing_device.location = device.location
    existing_device.status = device.status

    db.commit()
    db.refresh(existing_device)

    return existing_device


# DELETE - Delete a device
@app.delete(
    "/devices/{device_id}",
    dependencies=[Depends(verify_token)]
)
def delete_device(
    device_id: int,
    db: Session = Depends(get_db)
):
    existing_device = db.query(models.Device).filter(
        models.Device.id == device_id
    ).first()

    if existing_device is None:
        raise HTTPException(
            status_code=404,
            detail="Device not found"
        )

    db.delete(existing_device)
    db.commit()

    return {
        "message": "Device deleted successfully"
    }


# CREATE - Add a sensor reading
@app.post(
    "/devices/{device_id}/readings",
    response_model=schemas.SensorReadingResponse,
    dependencies=[Depends(verify_token)]
)
def create_sensor_reading(
    device_id: int,
    reading: schemas.SensorReadingCreate,
    db: Session = Depends(get_db)
):
    device = db.query(models.Device).filter(
        models.Device.id == device_id
    ).first()

    if device is None:
        raise HTTPException(
            status_code=404,
            detail="Device not found"
        )

    new_reading = models.SensorReading(
        device_id=device_id,
        sensor_type=reading.sensor_type,
        value=reading.value,
        unit=reading.unit
    )

    db.add(new_reading)
    db.commit()
    db.refresh(new_reading)

    return new_reading


# READ - Get all sensor readings for a device
@app.get(
    "/devices/{device_id}/readings",
    response_model=list[schemas.SensorReadingResponse],
    dependencies=[Depends(verify_token)]
)
def get_sensor_readings(
    device_id: int,
    db: Session = Depends(get_db)
):
    device = db.query(models.Device).filter(
        models.Device.id == device_id
    ).first()

    if device is None:
        raise HTTPException(
            status_code=404,
            detail="Device not found"
        )

    readings = db.query(models.SensorReading).filter(
        models.SensorReading.device_id == device_id
    ).all()

    return readings


# READ - Get one sensor reading
@app.get(
    "/readings/{reading_id}",
    response_model=schemas.SensorReadingResponse,
    dependencies=[Depends(verify_token)]
)
def get_sensor_reading(
    reading_id: int,
    db: Session = Depends(get_db)
):
    reading = db.query(models.SensorReading).filter(
        models.SensorReading.id == reading_id
    ).first()

    if reading is None:
        raise HTTPException(
            status_code=404,
            detail="Sensor reading not found"
        )

    return reading