from sqlalchemy.orm import Session
from .models import Address
from .schemas import AddressCreate, AddressUpdate

def create_address(db: Session, address: AddressCreate):
    new_address = Address(**address.dict())
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address

def get_all_addresses(db: Session):
    return db.query(Address).all()

def update_address(db: Session, address_id: int, address: AddressUpdate):
    db_address = db.query(Address).filter(Address.id == address_id).first()
    if not db_address:
        return None

    for key, value in address.dict().items():
        setattr(db_address, key, value)

    db.commit()
    return db_address

def delete_address(db: Session, address_id: int):
    db_address = db.query(Address).filter(Address.id == address_id).first()
    if not db_address:
        return None

    db.delete(db_address)
    db.commit()
    return db_address
