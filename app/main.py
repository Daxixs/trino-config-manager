from fastapi import FastAPI, Request, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.routers import catalogs, roles, resource_groups, trino_config, reload
from app.services.trino_service import TrinoService
from app.services.file_service import FileService

app = FastAPI(
    title="Trino Config Manager",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# Роутеры
app.include_router(catalogs.router)
app.include_router(roles.router)
app.include_router(resource_groups.router)
app.include_router(trino_config.router)
app.include_router(reload.router)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login")
async def login(request: Request):
    form = await request.form()
    username = form.get("username", "")
    password = form.get("password", "")

    if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
        request.session["authenticated"] = True
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Неверный логин или пароль"},
        status_code=401,
    )


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not request.session.get("authenticated"):
        return RedirectResponse(url="/login", status_code=303)

    trino_alive = await TrinoService.check_health()
    catalogs_list = FileService.list_catalogs()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "trino_alive": trino_alive,
            "catalogs": catalogs_list,
            "catalogs_count": len(catalogs_list),
            "active": "dashboard",
        }
    )
