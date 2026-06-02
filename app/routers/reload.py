from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.trino_service import TrinoService

router = APIRouter(prefix="/reload", tags=["reload"])
templates = Jinja2Templates(directory="app/templates")


@router.post("/", response_class=JSONResponse)
async def reload_trino():
    result = await TrinoService.reload_config()
    return JSONResponse(content=result, status_code=200 if result["success"] else 500)


@router.get("/status", response_class=JSONResponse)
async def health_check():
    alive = await TrinoService.check_health()
    return JSONResponse(content={"alive": alive})
