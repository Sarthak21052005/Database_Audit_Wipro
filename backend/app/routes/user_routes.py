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

@router.put("/update-user")
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

    try:
        # 🔥 SET USER BEFORE QUERY
        db.execute(
            text("SELECT set_config('app.current_user', :val, false)"),
            {"val": current_user["sub"]}
        )

        # ✅ Username update
        if updated_data.username:
            existing = db.query(models.User).filter(
                models.User.username == updated_data.username
            ).first()

            if existing and existing.id != user.id:
                raise HTTPException(status_code=400, detail="Username already exists")

            db.execute(
                text("UPDATE users SET username = :username WHERE id = :id"),
                {"username": updated_data.username, "id": user.id}
            )

        # ✅ Password update
        if updated_data.password:
            if len(updated_data.password) < 6:
                raise HTTPException(status_code=400, detail="Password too short")

            db.execute(
                text("UPDATE users SET password = :password WHERE id = :id"),
                {"password": hash_password(updated_data.password), "id": user.id}
            )

        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "User updated successfully"}