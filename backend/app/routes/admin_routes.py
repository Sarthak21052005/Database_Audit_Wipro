from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import app.models as models
from fastapi import HTTPException
from sqlalchemy import text
from app.dependencies import get_db, require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/logs")
def get_logs(db: Session = Depends(get_db), admin=Depends(require_admin)):
    logs = db.query(models.AuditLog).all()
    return logs


@router.post("/rollback/{log_id}")
def rollback(log_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    log = db.query(models.AuditLog).filter(models.AuditLog.id == log_id).first()

    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    table = log.table_name
    old = log.old_data

    # ⚠️ Allow only specific tables (security)
    if table != "users":
        raise HTTPException(status_code=400, detail="Unsupported table")

    # 🔁 Handle UPDATE rollback
    if log.operation == "UPDATE":
        db.execute(
            text("""
                UPDATE users
                SET username = :username,
                    password = :password,
                    role = :role
                WHERE id = :id
            """),
            {
                "id": old.get("id"),
                "username": old.get("username"),
                "password": old.get("password"),
                "role": old.get("role"),
            }
        )

    # 🔁 Handle DELETE rollback (re-insert old data)
    elif log.operation == "DELETE":
        db.execute(
            text("""
                INSERT INTO users (id, username, password, role)
                VALUES (:id, :username, :password, :role)
            """),
            {
                "id": old.get("id"),
                "username": old.get("username"),
                "password": old.get("password"),
                "role": old.get("role"),
            }
        )

    # 🔁 Handle INSERT rollback (delete new record)
    elif log.operation == "INSERT":
        db.execute(
            text("DELETE FROM users WHERE id = :id"),
            {"id": log.new_data.get("id")}
        )

    else:
        raise HTTPException(status_code=400, detail="Unsupported operation")

    db.commit()

    return {"message": "Rollback executed successfully"}