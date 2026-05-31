import json
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.services.file_service import FileService
from app.validators.resource_group_validator import validate_resource_groups

router = APIRouter(prefix="/resource-groups", tags=["resource_groups"])
templates = Jinja2Templates(directory="app/templates")

RG_FILE = "resource_groups.json"

DEFAULT_RG = json.dumps({
    "rootGroups": [
        {
            "name": "global",
            "maxQueued": 100,
            "hardConcurrencyLimit": 50,
            "softMemoryLimit": "80%",
            "subGroups": [
                {
                    "name": "default",
                    "maxQueued": 100,
                    "hardConcurrencyLimit": 10,
                    "softMemoryLimit": "20%"
                }
            ]
        }
    ],
    "selectors": [
        {"group": "global.default"}
    ]
}, indent=2)


@router.get("/", response_class=HTMLResponse)
async def edit_resource_groups(request: Request):
    path = settings.TRINO_CONFIG_DIR / RG_FILE
    content = await FileService.read_file(path)
    if not content:
        content = DEFAULT_RG
    backups = FileService.list_backups(path)
    return templates.TemplateResponse(
        "resource_groups/edit.html",
        {
            "request": request,
            "content": content,
            "errors": [],
            "backups": backups,
            "active": "resource_groups",
        }
    )


@router.post("/save")
async def save_resource_groups(request: Request, content: str = Form(...)):
    errors = validate_resource_groups(content)

    if errors:
        return templates.TemplateResponse(
            "resource_groups/edit.html",
            {
                "request": request,
                "content": content,
                "errors": errors,
                "active": "resource_groups",
            },
            status_code=422,
        )

    try:
        formatted = json.dumps(json.loads(content), indent=2, ensure_ascii=False)
    except Exception:
        formatted = content

    path = settings.TRINO_CONFIG_DIR / RG_FILE
    await FileService.write_file(path, formatted)

    return RedirectResponse(url="/resource-groups/", status_code=303)
