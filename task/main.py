from fastapi import Depends, FastAPI, HTTPException

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas
from .database import SessionLocal, engine
from .models import User

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create a user
@app.post("/api", response_model=schemas.UserReturn)
def create_user(user: schemas.UserCRUD, db: Session = Depends(get_db)):
    if not user.name:
        raise HTTPException(status_code=400, detail='Name is required')

    db_user = User(name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return db_user


# Read a user
@app.get("/api/{user_id}", response_model=schemas.UserReturn)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter_by(id=user_id).first()
    db.close()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# Update a user
@app.put("/api/{user_id}", response_model=schemas.UserReturn)
def update_user(user_id: int, user: schemas.UserCRUD, db: Session = Depends(get_db)):
    if not user.name:
        raise HTTPException(status_code=400, detail='Name is required')

    db_user = db.query(User).filter_by(id=user_id).first()

    if db_user is None:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")

    db_user.name = user.name

    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        db.close()
        raise HTTPException(status_code=400, detail="User with this name already exists")

    db.close()
    return db_user


# Delete a user
@app.delete("/api/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter_by(id=user_id).first()

    if db_user is None:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        db.close()
        raise HTTPException(status_code=400, detail="User with this name already exists")

    db.close()
    return {"detail": "User successfully deleted"}
