import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status

# 🔐 Use environment variable (VERY IMPORTANT)
SECRET_KEY = os.getenv("SECRET_KEY", "change_this_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# 🔒 Password hashing (bcrypt only)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ✅ Hash password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# ✅ Verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ✅ Create JWT token
def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()  # issued at
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ✅ Decode JWT token
def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )