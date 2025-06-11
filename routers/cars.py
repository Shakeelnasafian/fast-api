from typing import Annotated

from fastapi import HTTPException, Depends, APIRouter
from sqlmodel import Session, select

from db import get_session

from schemas import CarInput, TripInput, TripOutput, Car, Trip, CarOutput

router = APIRouter(prefix="/api/cars")

@router.get("/")
def get_cars(session: Annotated[Session, Depends(get_session)], size : str | None = None, doors: int | None = None) -> list:
        query = select(Car)
        if size:
            query = query.where(Car.size == size)
        if doors:
            query = query.where(Car.doors >= doors)
        return session.exec(query).all()

@router.get("/{id}")
def read_car(session: Annotated[Session, Depends(get_session)], id: int) -> CarOutput:
        car = session.get(Car, id)
        if car:
            return car
        else:
            raise HTTPException(status_code=404, detail="Car not found")
        
@router.post("/")
def save_car(session: Annotated[Session, Depends(get_session)], car_input: CarInput) -> Car:
        new_car = Car.model_validate(car_input)
        session.add(new_car)
        session.commit()
        session.refresh(new_car)
        return new_car

@router.delete("/{id}")
def delete_car(session: Annotated[Session, Depends(get_session)], id: int)-> None:
    car = session.get(Car, id)
    if car:
        session.delete(car)
        session.commit()
        return {"message": "Car deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Car not found")

@router.put("/{id}")
def update_car(session : Annotated[Session, Depends(get_session)], id: int, new_data : CarInput)-> Car:
    car = session.get(Car, id)
    if car:
        car.fuel = new_data.fuel
        car.size = new_data.size
        car.doors = new_data.doors
        car.transmission = new_data.transmission
        session.commit()
        return car
    else:
        raise HTTPException(status_code=404, detail="Car not found")

@router.post("/{car_id}/trips")
def add_trip(session: Annotated[Session, Depends(get_session)],
             car_id: int, trip_input: TripInput) -> Trip:
    car = session.get(Car, car_id)
    if car:
        new_trip = Trip.model_validate(trip_input, update={'car_id': car_id})
        car.trips.append(new_trip)
        session.commit()
        session.refresh(new_trip)
        return new_trip
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={id}.")