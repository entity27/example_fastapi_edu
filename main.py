from os import access
from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session
import uvicorn

from db import models, crud, schemes
from db.base import SessionLocal, engine
from auth import Auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register", response_model=schemes.Tokens) # TODO: return refresh tokens
def create_user(user: schemes.User, db: Session = Depends(get_db)):
    db_user = crud.get_user(db=db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return Auth.get_token_pair(username=user.username)

@app.post("/login", response_model=schemes.Tokens)
def login(user: schemes.User, db: Session = Depends(get_db)):
    db_user = crud.get_user(db=db, username=user.username)
    if not db_user:
        raise HTTPException(status_code=400, detail="There is no such user")
    if db_user.password != user.password:
        raise HTTPException(status_code=400, detail="Invalid password")
    return Auth.get_token_pair(username=user.username)

@app.post("/refresh", response_model=schemes.Tokens)
def refresh_tokens(request: Request):
    refresh_token = Auth.get_token_from_header(request=request)
    Tokens = Auth.refresh_tokens(refresh_token=refresh_token)
    return Tokens

@app.get("/secret", response_model=schemes.Message)
def secret_data(request: Request):
    access_token = Auth.get_token_from_header(request=request)
    Auth.identify_access_token(token=access_token)
    return schemes.Message(message="Good one")

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)