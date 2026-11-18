
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from database import create_db_and_tables, get_session
from models import User, Parcel, ParcelEvent


# Create database tables when the application starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


# Request models
class UserCreate(BaseModel):
    name: str
    email: str


class ParcelCreate(BaseModel):
    tracking_number: str
    courier: str
    description: str
    recipient_id: int


# E1: Create a user
@app.post("/users", response_model=User, status_code=201)
def create_user(
    data: UserCreate,
    session: Session = Depends(get_session)
):
    user = User(
        name=data.name,
        email=data.email
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


# E2: Create a parcel
@app.post("/parcels", response_model=Parcel, status_code=201)
def create_parcel(
    data: ParcelCreate,
    session: Session = Depends(get_session)
):
    # Check whether recipient exists
    recipient = session.get(User, data.recipient_id)

    if not recipient:
        raise HTTPException(
            status_code=404,
            detail="Recipient not found"
        )

    # Check required fields
    if (
        not data.tracking_number.strip()
        or not data.courier.strip()
        or not data.description.strip()
    ):
        raise HTTPException(
            status_code=400,
            detail="Required fields cannot be blank"
        )

    # Check duplicate tracking number
    existing_parcel = session.exec(
        select(Parcel).where(
            Parcel.tracking_number == data.tracking_number
        )
    ).first()

    if existing_parcel:
        raise HTTPException(
            status_code=409,
            detail="Tracking number already exists"
        )

    # Create parcel
    parcel = Parcel(
        tracking_number=data.tracking_number,
        courier=data.courier,
        description=data.description,
        recipient_id=data.recipient_id,
        status="registered"
    )

    session.add(parcel)
    session.commit()
    session.refresh(parcel)

    return parcel


# E3: Get all parcels
@app.get("/parcels", response_model=list[Parcel])
def list_parcels(
    session: Session = Depends(get_session)
):
    return session.exec(select(Parcel)).all()


# E3: Get a parcel by ID
@app.get("/parcels/{parcel_id}", response_model=Parcel)
def get_parcel(
    parcel_id: int,
    session: Session = Depends(get_session)
):
    parcel = session.get(Parcel, parcel_id)

    if not parcel:
        raise HTTPException(
            status_code=404,
            detail="Parcel not found"
        )

    return parcel


# E4: Update a parcel
@app.put("/parcels/{parcel_id}", response_model=Parcel)
def update_parcel(
    parcel_id: int,
    data: ParcelCreate,
    session: Session = Depends(get_session)
):
    parcel = session.get(Parcel, parcel_id)

    if not parcel:
        raise HTTPException(
            status_code=404,
            detail="Parcel not found"
        )

    # Check required fields
    if (
        not data.tracking_number.strip()
        or not data.courier.strip()
        or not data.description.strip()
    ):
        raise HTTPException(
            status_code=400,
            detail="Required fields cannot be blank"
        )

    # Check whether new recipient exists
    recipient = session.get(User, data.recipient_id)

    if not recipient:
        raise HTTPException(
            status_code=404,
            detail="Recipient not found"
        )

    # Check whether another parcel uses this tracking number
    existing_parcel = session.exec(
        select(Parcel).where(
            Parcel.tracking_number == data.tracking_number
        )
    ).first()

    if existing_parcel and existing_parcel.id != parcel_id:
        raise HTTPException(
            status_code=409,
            detail="Tracking number already exists"
        )

    # Update allowed fields only
    parcel.tracking_number = data.tracking_number
    parcel.courier = data.courier
    parcel.description = data.description
    parcel.recipient_id = data.recipient_id
    parcel.updated_at = datetime.now(timezone.utc)

    session.add(parcel)
    session.commit()
    session.refresh(parcel)

    return parcel


# E5: Delete a parcel
@app.delete("/parcels/{parcel_id}")
def delete_parcel(
    parcel_id: int,
    session: Session = Depends(get_session)
):
    parcel = session.get(Parcel, parcel_id)

    if not parcel:
        raise HTTPException(
            status_code=404,
            detail="Parcel not found"
        )

    # Do not delete collected parcels
    if parcel.status == "collected":
        raise HTTPException(
            status_code=409,
            detail="Collected parcels cannot be deleted"
        )

    # Check whether parcel has event history
    event = session.exec(
        select(ParcelEvent).where(
            ParcelEvent.parcel_id == parcel_id
        )
    ).first()

    if event:
        raise HTTPException(
            status_code=409,
            detail="Parcel with event history cannot be deleted"
        )

    session.delete(parcel)
    session.commit()

    return {"message": "Parcel deleted"}
