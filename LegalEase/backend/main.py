from fastapi import FastAPI
from backend.routes import router

app = FastAPI(
    title="LegalEase",
    description="AI-Powered Legal Document Generator",
    version="1.0"
)

app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "LegalEase Backend is Running!"
    }