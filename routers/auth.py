from typing import Annotated, Dict
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select

from db import get_session
from schemas import User, UserOutput, UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

_tokens: Dict[str, int] = {}

@router.post("/register", response_model=UserOutput)
def register(user_in: UserCreate, session: Annotated[Session, Depends(get_session)]):
    user = User(username=user_in.username)
    user.set_password(user_in.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
):
    query = select(User).where(User.username == form_data.username)
    user = session.exec(query).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = secrets.token_urlsafe(32)
    _tokens[token] = user.id
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    user_id = _tokens.get(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user

@router.get("/me", response_model=UserOutput)
def read_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
