from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from db import engine
import uvicorn
from routers import cars, web

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(title="Car Sharing API", lifespan=lifespan)
app.include_router(cars.router) 
app.include_router(web.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("carsharing:app", reload=True)