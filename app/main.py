from fastapi import FastAPI
from app.api.endpoints import vanishing_point
from app.core import logging_config  

app = FastAPI()

app.include_router(vanishing_point.router)

@app.get("/")
def root():
    return {"message": "wtf are you doing here?"} 