from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.auth import hash_password
import app.models as models
import app.schemas as schemas
from sqlalchemy import text

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/profile")
def get_profile(user=Depends(get_current_user)):
    return user

@router.put("/update")
def update_user(
    updated_data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user = db.query(models.User).filter(
        models.User.username == current_user["sub"]
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not updated_data.username and not updated_data.password:
        raise HTTPException(status_code=400, detail="Nothing to update")

    if updated_data.username:
        existing = db.query(models.User).filter(
            models.User.username == updated_data.username
        ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user.username = updated_data.username

    # ✅ update password
    if updated_data.password:
        user.password = hash_password(updated_data.password)
    conn = db.connection()

    conn.execute(
    text('SET LOCAL "app.current_user" = :username'),
    {"username": current_user["sub"]})

    db.commit()
    db.refresh(user)

    return {"message": "User updated successfully"}