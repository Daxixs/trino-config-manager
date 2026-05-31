from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.config import settings
from app.services.file_service import FileService
from app.validators.catalog_validator import validate_catalog

router = APIRouter(prefix="/catalogs", tags=["catalogs"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def list_catalogs(request: Request):
    catalogs = FileService.list_catalogs()
    return templates.TemplateResponse(
        "catalogs/list.html",
        {"request": request, "catalogs": catalogs, "active": "catalogs"}
    )


@router.get("/new", response_class=HTMLResponse)
async def new_catalog_form(request: Request):
    return templates.TemplateResponse(
        "catalogs/edit.html",
        {
            "request": request,
            "name": "",
            "content": "connector.name=postgresql\nconnection-url=jdbc:postgresql://host:5432/db\nconnection-user=trino\nconnection-password=secret",
            "errors": [],
            "is_new": True,
            "active": "catalogs",
        }
    )


@router.get("/{name}/edit", response_class=HTMLResponse)
async def edit_catalog_form(request: Request, name: str):
    path = settings.TRINO_CATALOG_DIR / f"{name}.properties"
    content = await FileService.read_file(path)
    backups = FileService.list_backups(path)
    return templates.TemplateResponse(
        "catalogs/edit.html",
        {
            "request": request,
            "name": name,
            "content": content,
            "errors": [],
            "is_new": False,
            "backups": backups,
            "active": "catalogs",
        }
    )


@router.post("/{name}/save")
async def save_catalog(
    request: Request,
    name: str,
    content: str = Form(...),
    catalog_name: str = Form(default=""),
):
    # При создании нового — берём имя из формы
    actual_name = catalog_name if catalog_name else name
    errors = validate_catalog(actual_name, content)

    if errors:
        return templates.TemplateResponse(
            "catalogs/edit.html",
            {
                "request": request,
                "name": actual_name,
                "content": content,
                "errors": errors,
                "is_new": name == "new",
                "active": "catalogs",
            },
            status_code=422,
        )

    path = settings.TRINO_CATALOG_DIR / f"{actual_name}.properties"
    await FileService.write_file(path, content)

    return RedirectResponse(url="/catalogs/", status_code=303)


@router.post("/{name}/delete")
async def delete_catalog(name: str):
    path = settings.TRINO_CATALOG_DIR / f"{name}.properties"
    await FileService.delete_file(path)
    return RedirectResponse(url="/catalogs/", status_code=303)
