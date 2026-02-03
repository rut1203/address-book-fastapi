from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
import os

from .database import Base, engine, SessionLocal
from . import crud, schemas
from .utils import haversine_distance

# ---------- DATABASE ----------
Base.metadata.create_all(bind=engine)

# ---------- LOGGING ----------
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------- APP ----------
app = FastAPI(title="Address Book API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/addresses", response_model=schemas.AddressResponse)
def create_address(address: schemas.AddressCreate, db: Session = Depends(get_db)):
    logging.info("Creating address")
    return crud.create_address(db, address)

@app.get("/addresses", response_model=list[schemas.AddressResponse])
def get_addresses(db: Session = Depends(get_db)):
    return crud.get_all_addresses(db)

@app.put("/addresses/{address_id}", response_model=schemas.AddressResponse)
def update_address(address_id: int, address: schemas.AddressUpdate, db: Session = Depends(get_db)):
    updated = crud.update_address(db, address_id, address)
    if not updated:
        raise HTTPException(status_code=404, detail="Address not found")
    return updated

@app.delete("/addresses/{address_id}")
def delete_address(address_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_address(db, address_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Address not found")
    return {"message": "Deleted successfully"}

@app.get("/addresses/nearby", response_model=list[schemas.AddressResponse])
def nearby_addresses(
    latitude: float,
    longitude: float,
    distance_km: float,
    db: Session = Depends(get_db)
):
    results = []
    addresses = crud.get_all_addresses(db)

    for addr in addresses:
        dist = haversine_distance(
            latitude, longitude,
            addr.latitude, addr.longitude
        )
        if dist <= distance_km:
            results.append(addr)

    return results