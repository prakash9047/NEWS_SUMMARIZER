from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.routes import news, auth, summarization
from backend.database import Base, engine
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="News Summarizer API")

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend_file/static"), name="static")

# Include routers with proper prefixes
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(summarization.router, prefix="/api/summarize", tags=["summarization"])

@app.get("/env-debug")
def debug_env():
    return {
        "NEWS_API_KEY": os.getenv("NEWS_API_KEY"),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "SECRET_KEY": os.getenv("SECRET_KEY"),
    }


@app.get("/")
async def root():
    return FileResponse("frontend_file/index.html")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"} 
