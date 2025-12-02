# api/server.py

from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="Real-Time Metrics API")

app.include_router(router)


# Optional root endpoint
@app.get("/")
def home():
    return {"msg": "Real-time Metrics API is running"}
