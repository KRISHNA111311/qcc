from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import circuit_router
from .api.auth import router as auth_router
from .api.content import router as content_router
from .api.progress import router as progress_router
from .config import get_settings
from .logging import setup_logging
from .db.session import engine
from .db.models import Base

settings = get_settings()
setup_logging()

# Initialize database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="QCC API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(circuit_router)
app.include_router(auth_router)
app.include_router(content_router)
app.include_router(progress_router)

@app.get("/")
async def root():
    return {"message": "QCC API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.qcc.main:app", host="0.0.0.0", port=8000, reload=True)
