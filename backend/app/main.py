from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db.session import Base, engine
from app import models  # noqa: F401

settings = get_settings()

app = FastAPI(title=settings.app_name)

origins = [item.strip() for item in settings.allowed_origins.split(",") if item.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(api_router, prefix=settings.api_prefix)
