from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import app.models as models
from fastapi.security import OAuth2PasswordRequestForm
import app.schemas as schemas
from app.database import SessionLocal
from app.auth import hash_password, verify_password, create_access_token
from app.dependencies import get_db ,get_current_user
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(
        username=user.username,
        password=hash_password(user.password),
        role=user.role
    )
    db.add(db_user)
    db.commit()
    return {"message": "User created"}

@router.post("/login", response_model=schemas.TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)   # ✅ FIXED
):
    db_user = db.query(models.User).filter(
        models.User.username == form_data.username
    ).first()

    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": db_user.username,
        "role": db_user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }
