from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import analysis
import os

FRONTEND_HOST = os.getenv("FRONTEND_HOST")

app = FastAPI()

# Allowed origins for CORS (add your frontend URLs here)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://into-the-repo.vercel.app/"
]

if FRONTEND_HOST:
    origins.append(FRONTEND_HOST)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router)

@app.get("/")
def read_root():
    return {"message": "Backend is running 🚀"}
