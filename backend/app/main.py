from fastapi import FastAPI
from app.routes import auth_routes, user_routes,admin_routes
from app.database import Base, engine
from app import models
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(admin_routes.router)


@app.get("/")
def root():
    return {"message": "Audit Tracker Running 🚀"}