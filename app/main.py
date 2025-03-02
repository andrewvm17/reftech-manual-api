from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import manual_vanishing_point
from app.core import logging_config  

app = FastAPI()

# Add CORS middleware with production domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://reftech.app", "https://www.reftech.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(manual_vanishing_point.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Vanishing Point API"} 