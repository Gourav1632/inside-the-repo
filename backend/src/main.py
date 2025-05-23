from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import analysis

app = FastAPI()

# Allowed origins for CORS (add your frontend URLs here)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Add other frontend URLs if any
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Or ["*"] to allow all origins (not recommended in prod)
    allow_credentials=True,
    allow_methods=["*"],          # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],          # Allow all headers
)

app.include_router(analysis.router)

@app.get("/")
def read_root():
    return {"message": "Backend is running 🚀"}
