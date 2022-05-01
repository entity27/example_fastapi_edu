from sqlalchemy.orm import Session
from . import models, schemes
from datetime import datetime

def get_user(db: Session, username: str):
    return db.query(models.UserModel).filter(models.UserModel.username == username).first()

def create_user(db: Session, user: schemes.User):
    db_user = models.UserModel(username=user.username, password=user.password, created=datetime.now())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user