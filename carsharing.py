from fastapi import FastAPI, HTTPException
from schemas import load_db, save_db, CarOutput, CarInput

app = FastAPI(title="Car Sharing API")

db = load_db()

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}

@app.get("/cars", tags='size')
def read_cars(size : str = None):
    if size is None:
        return db
    return [car for car in db if car.size == size]

@app.get("/car/{car_id}")
def read_car(car_id: int):
   result = [car for car in db if car.id == car_id]
   if result:
       return result[0]
   else:
       raise HTTPException(status_code=404, detail="Car not found")
   
@app.post("/car")
def save_car(car: CarInput) -> CarOutput:
    new_car = CarOutput(
        id=len(db) + 1,
        size=car.size,
        fuel=car.fuel,
        doors=car.doors,
        transmission=car.transmission,
        trips=car.trips
    )
    db.append(new_car)
    save_db(db)
    return new_car

@app.delete("/car/{car_id}")
def delete_car(car_id: int):
    result = [car for car in db if car.id == car_id]
    if result:
        db.remove(result[0])
        save_db(db)
        return {"message": "Car deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Car not found")

@app.put("/car/{car_id}")
def update_car(car_id: int, new_data: CarInput)-> CarOutput:
    match = [car for car in db if car.id == car_id]
    if match:
        car = match[0]
        car.fuel = new_data.fuel
        car.size = new_data.size
        car.doors = new_data.doors
        car.transmission = new_data.transmission
        car.trips = new_data.trips
        save_db(db)
        return car
    else:
        raise HTTPException(status_code=404, detail="Car not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("carsharing:app", reload=True)