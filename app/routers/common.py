from fastapi import APIRouter
from typing import Union
router = APIRouter(prefix="/common")


@router.get("/ping", status_code = 200)
async def health_check() -> Union[dict]:
    """_summary_
    Health Check API
    
    Returns:
        dict : return health check message
    """
    return {"status_msg" : "pong"}