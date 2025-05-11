from fastapi import FastAPI
from src.api import analysis

app = FastAPI()

app.include_router(analysis.router)
@app.get("/")
def read_root():
    return {"message": "Backend is running 🚀"}
