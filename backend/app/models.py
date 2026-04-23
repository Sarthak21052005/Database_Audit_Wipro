from sqlalchemy import Column, Integer, String, JSON, TIMESTAMP, text
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="user")  # user / admin


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String)
    table_name = Column(String)
    operation = Column(String)
    old_data = Column(JSON)
    new_data = Column(JSON)
    timestamp = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))