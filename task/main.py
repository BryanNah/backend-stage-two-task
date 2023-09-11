from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas
from .database import SessionLocal, engine
from .models import User

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    validation_error_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    validation_error_model=schemas.CustomValidationError,
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create a user
@app.post("/api", response_model=schemas.UserCRUD)
def create_user(user: schemas.UserCRUD, db: Session = Depends(get_db)):
    name = user.name
    db_user = db.query(User).filter_by(name=name).first()

    if db_user is None:
        db_user = User(name=name)
        db.add(db_user)
    else:
        db.close()
        raise HTTPException(status_code=400, detail="User with this name already exists")

    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        db.close()
        raise HTTPException(status_code=400, detail="User with this name already exists")

    db.close()
    return db_user


# Read a user
@app.get("/api", response_model=schemas.UserCRUD)
def read_user(name: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter_by(name=name).first()
    db.close()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# Update a user
@app.put("/api", response_model=schemas.UserCRUD)
def update_user(name: str, user: schemas.UserCRUD, db: Session = Depends(get_db)):
    db_user = db.query(User).filter_by(name=name).first()

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
@app.delete("/api")
def delete_user(name: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter_by(name=name).first()

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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Name should be a valid string"},
    )
