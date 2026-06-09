from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import auth      

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AY-VocabVault API",
    description="LLM-powered personalized vocabulary learning",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth.router)     

@app.get("/")
def root():
    return {"message": "AY-VocabVault API is running "}