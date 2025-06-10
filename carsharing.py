from fastapi import FastAPI, HTTPException, Depends
from contextlib import asynccontextmanager
from typing import Annotated
from schemas import CarInput, TripInput, TripOutput, Car, Trip, CarOutput
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session, select

engine = create_engine(
    "sqlite:///cars.db",
    connect_args={"check_same_thread": False},
    echo=True
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

def get_session():
    with Session(engine) as session:
        yield session  

app = FastAPI(title="Car Sharing API", lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}

@app.get("/cars")
def read_cars(session: Annotated[Session, Depends(get_session)], size : str | None = None, doors: int | None = None) -> list:
        query = select(Car)
        if size:
            query = query.where(Car.size == size)
        if doors:
            query = query.where(Car.doors >= doors)
        return session.exec(query).all()

@app.get("/car/{id}")
def read_car(session: Annotated[Session, Depends(get_session)], id: int) -> CarOutput:
        car = session.get(Car, id)
        if car:
            return car
        else:
            raise HTTPException(status_code=404, detail="Car not found")
        
@app.post("/car")
def save_car(session: Annotated[Session, Depends(get_session)], car_input: CarInput) -> Car:
        new_car = Car.model_validate(car_input)
        session.add(new_car)
        session.commit()
        session.refresh(new_car)
        return new_car

@app.delete("/car/{id}")
def delete_car(session: Annotated[Session, Depends(get_session)], id: int)-> None:
    car = session.get(Car, id)
    if car:
        session.delete(car)
        session.commit()
        return {"message": "Car deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Car not found")

@app.put("/car/{id}")
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

@app.post("/api/cars/{car_id}/trips")
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
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("carsharing:app", reload=True)