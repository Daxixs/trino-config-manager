import json
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.services.file_service import FileService
from app.validators.role_validator import validate_roles

router = APIRouter(prefix="/roles", tags=["roles"])
templates = Jinja2Templates(directory="app/templates")

ROLES_FILE = "access-control/rules.json"

DEFAULT_RULES = json.dumps({
    "catalogs": [
        {"user": "admin", "allow": "all"},
        {"allow": "read-only"}
    ],
    "schemas": [],
    "tables": [],
    "queries": [
        {"user": "admin", "allow": ["execute", "kill", "view"]}
    ]
}, indent=2)


@router.get("/", response_class=HTMLResponse)
async def edit_roles(request: Request):
    path = settings.TRINO_CONFIG_DIR / ROLES_FILE
    content = await FileService.read_file(path)
    if not content:
        content = DEFAULT_RULES
    backups = FileService.list_backups(path)
    return templates.TemplateResponse(
        "roles/edit.html",
        {
            "request": request,
            "content": content,
            "errors": [],
            "backups": backups,
            "active": "roles",
        }
    )


@router.post("/save")
async def save_roles(request: Request, content: str = Form(...)):
    errors = validate_roles(content)

    if errors:
        return templates.TemplateResponse(
            "roles/edit.html",
            {
                "request": request,
                "content": content,
                "errors": errors,
                "active": "roles",
            },
            status_code=422,
        )

    # Форматируем JSON перед сохранением
    try:
        formatted = json.dumps(json.loads(content), indent=2, ensure_ascii=False)
    except Exception:
        formatted = content

    path = settings.TRINO_CONFIG_DIR / ROLES_FILE
    await FileService.write_file(path, formatted)

    return RedirectResponse(url="/roles/", status_code=303)
