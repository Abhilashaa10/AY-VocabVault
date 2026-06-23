# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize the app
app = FastAPI(
    title="AY-VocabVault API",
    description="LLM-powered personalized vocabulary learning",
    version="1.0.0"
)

# CORS — allows React frontend to talk to this backend
# Without this the browser blocks all requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check route
# Visit http://localhost:8000 to confirm server is running
@app.get("/")
def root():
    return {
        "message": "AY-VocabVault API is running ✅",
        "version": "1.0.0"
    }