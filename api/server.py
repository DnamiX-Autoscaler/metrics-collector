# api/server.py

from fastapi import FastAPI
from api.routes import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Real-Time Metrics API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://localhost:1573",
        "http://localhost:1574",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3004",
        "http://127.0.0.1:3005",
        "http://127.0.0.1:1573",
        "http://127.0.0.1:1574",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


# Optional root endpoint
@app.get("/")
def home():
    return {"msg": "Real-time Metrics API is running"}
