import json
from pydantic import BaseModel

class CarInput(BaseModel):
    size: str | None = "m"
    fuel: str | None = "Gasoline"
    doors: int | None = 4
    transmission: str | None = "Auto"
    trips: list[dict] = []

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                "size": "m",
                "doors": 5,
                "transmission": "manual",
                "fuel": "hybrid"
                }
            ]
        }
    }

class CarOutput(CarInput):
    id: int


def load_db() -> list[CarOutput]:
    with open("cars.json", "r") as file:
        return [CarOutput.model_validate(obj) for obj in json.load(file)]
    
def save_db(cars: list[CarOutput]):
    with open("cars.json", "w") as file:
        json.dump([car.model_dump() for car in cars], file, indent=4)