from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import app.models as models
from app.dependencies import get_db, require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])

# ✅ Whitelist tables (IMPORTANT for security)
ALLOWED_TABLES = ["users", "audit_logs"]


@router.get("/logs")
def get_logs(db: Session = Depends(get_db), admin=Depends(require_admin)):
    return db.query(models.AuditLog).all()


@router.post("/rollback/{log_id}")
def rollback(
    log_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    log = db.query(models.AuditLog).filter(models.AuditLog.id == log_id).first()

    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    table = log.table_name

    # ✅ Prevent SQL injection
    if table not in ALLOWED_TABLES:
        raise HTTPException(status_code=400, detail="Invalid table")

    try:
        # ✅ Set user context for audit logic
        db.execute(
            text("SELECT set_config('app.current_user', :val, false)"),
            {"val": f"{admin['sub']}_rollback"}
        )

        # 🔥 Disable triggers
        db.execute(text("SET session_replication_role = 'replica'"))

        # =========================
        # 🔁 HANDLE UPDATE
        # =========================
        if log.operation == "UPDATE":
            old_data = log.old_data

            if not old_data or "id" not in old_data:
                raise HTTPException(status_code=400, detail="Invalid old_data")

            set_clause = ", ".join([f"{k} = :{k}" for k in old_data.keys()])
            query = text(f"UPDATE {table} SET {set_clause} WHERE id = :id")

            db.execute(query, old_data)

        # =========================
        # 🔁 HANDLE INSERT → DELETE
        # =========================
        elif log.operation == "INSERT":
            new_data = log.new_data

            if not new_data or "id" not in new_data:
                raise HTTPException(status_code=400, detail="Invalid new_data")

            query = text(f"DELETE FROM {table} WHERE id = :id")
            db.execute(query, {"id": new_data["id"]})

        # =========================
        # 🔁 HANDLE DELETE → INSERT
        # =========================
        elif log.operation == "DELETE":
            old_data = log.old_data

            if not old_data:
                raise HTTPException(status_code=400, detail="Invalid old_data")

            columns = ", ".join(old_data.keys())
            values = ", ".join([f":{k}" for k in old_data.keys()])

            query = text(f"INSERT INTO {table} ({columns}) VALUES ({values})")
            db.execute(query, old_data)

        else:
            raise HTTPException(status_code=400, detail="Unsupported operation")

        # 🔥 Re-enable triggers BEFORE commit
        db.execute(text("SET session_replication_role = 'origin'"))

        # ✅ Commit only on success
        db.commit()

        return {"message": "Rollback successful"}

    except Exception as e:
        # ❗ Rollback DB changes
        db.rollback()

        # 🔥 Ensure triggers are re-enabled
        db.execute(text("SET session_replication_role = 'origin'"))
        db.commit()

        raise HTTPException(status_code=500, detail=str(e))