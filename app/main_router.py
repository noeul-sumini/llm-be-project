from fastapi import APIRouter
from routers.common import router as common_router
from routers.qa import router as qa_router


api_router = APIRouter(prefix="/v1")
api_router.include_router(common_router, tags=["Common"])
api_router.include_router(qa_router, tags = ["QA"])

