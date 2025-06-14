from typing import Annotated
from fastapi import APIRouter, Request, Form, Depends, Cookie
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlmodel import Session

from db import get_session
from routers.cars import get_cars

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)

def read_index(request: Request, session: Annotated[Session, Depends(get_session)], cars_cookie: Annotated[str | None, Cookie()]):
    print(cars_cookie)
    cars = get_cars(session=session)
    return templates.TemplateResponse("index.html", {"request": request, "cars": cars})

@router.post("/search", response_class=HTMLResponse)
def search(size: Annotated[str, Form()], 
           doors: Annotated[int, Form()], 
           request: Request, 
           session: Annotated[Session, Depends(get_session)]):
    cars = get_cars(size=size, doors=doors, session=session)
    return templates.TemplateResponse("search_results.html", {"request": request, "cars": cars})