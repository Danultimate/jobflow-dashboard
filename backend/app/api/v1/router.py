from fastapi import APIRouter, Depends

from app.api.v1.auth import router as auth_router
from app.api.v1.ai import router as ai_router
from app.api.v1.applications import router as applications_router
from app.api.v1.documents import router as documents_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.linkedin import router as linkedin_router
from app.core.security import require_auth

api_router = APIRouter()
protected_router = APIRouter(dependencies=[Depends(require_auth)])
protected_router.include_router(jobs_router)
protected_router.include_router(applications_router)
protected_router.include_router(documents_router)
protected_router.include_router(ai_router)
protected_router.include_router(linkedin_router)

api_router.include_router(auth_router)
api_router.include_router(protected_router)
