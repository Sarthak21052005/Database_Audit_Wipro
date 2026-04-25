from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.dependencies import get_db, get_current_user
from app.auth import hash_password
import app.models as models
import app.schemas as schemas

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
    # 🔍 Get user
    user = db.query(models.User).filter(
        models.User.username == current_user["sub"]
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not updated_data.username and not updated_data.password:
        raise HTTPException(status_code=400, detail="Nothing to update")

    try:
        # 🔥 VERY IMPORTANT: set user BEFORE update
        db.execute(
            text("SELECT set_config('app.current_user', :val, false)"),
            {"val": current_user["sub"]}
        )

        # 🔥 FORCE UPDATE (guarantees trigger fires)
        if updated_data.username:
            existing = db.query(models.User).filter(
                models.User.username == updated_data.username
            ).first()

            if existing and existing.id != user.id:
                raise HTTPException(status_code=400, detail="Username already exists")

            result = db.execute(
                text("UPDATE users SET username = :username WHERE id = :id RETURNING *"),
                {"username": updated_data.username, "id": user.id}
            )

            if result.rowcount == 0:
                raise HTTPException(status_code=500, detail="Update failed")

        if updated_data.password:
            if len(updated_data.password) < 6:
                raise HTTPException(status_code=400, detail="Password too short")

            result = db.execute(
                text("UPDATE users SET password = :password WHERE id = :id RETURNING *"),
                {"password": hash_password(updated_data.password), "id": user.id}
            )

            if result.rowcount == 0:
                raise HTTPException(status_code=500, detail="Password update failed")

        # 🔥 COMMIT (MANDATORY for trigger)
        db.commit()

        # 🔥 DEBUG CHECK (TEMP)
        logs = db.execute(text("SELECT * FROM audit_logs")).fetchall()
        print("DEBUG LOGS:", logs)

        return {"message": "User updated successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))