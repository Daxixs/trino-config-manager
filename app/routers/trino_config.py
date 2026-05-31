from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.services.file_service import FileService
from app.validators.config_validator import (
    validate_trino_config,
    validate_jvm_config,
    validate_node_properties,
)

router = APIRouter(prefix="/config", tags=["config"])
templates = Jinja2Templates(directory="app/templates")

DEFAULT_CONFIG = """coordinator=true
node-scheduler.include-coordinator=true
http-server.http.port=8080
discovery.uri=http://localhost:8080
query.max-memory=5GB
query.max-memory-per-node=1GB
query.max-total-memory-per-node=2GB
"""

DEFAULT_JVM = """-server
-Xmx16G
-Xms16G
-XX:InitialRAMPercentage=80
-XX:MaxRAMPercentage=80
-XX:G1HeapRegionSize=32M
-XX:+ExplicitGCInvokesConcurrent
-XX:+HeapDumpOnOutOfMemoryError
-XX:+ExitOnOutOfMemoryError
-XX:-OmitStackTraceInFastThrow
-XX:ReservedCodeCacheSize=512M
-XX:PerMethodRecompilationCutoff=10000
-XX:PerBytecodeRecompilationCutoff=10000
-Djdk.attach.allowAttachSelf=true
-Djdk.nio.maxCachedBufferSize=2000000
"""

DEFAULT_NODE = """node.environment=production
node.id=ffffffff-ffff-ffff-ffff-ffffffffffff
node.data-dir=/var/trino/data
"""


@router.get("/", response_class=HTMLResponse)
async def edit_config(request: Request):
    config_path = settings.TRINO_CONFIG_DIR / "config.properties"
    jvm_path = settings.TRINO_CONFIG_DIR / "jvm.config"
    node_path = settings.TRINO_CONFIG_DIR / "node.properties"

    config_content = await FileService.read_file(config_path) or DEFAULT_CONFIG
    jvm_content = await FileService.read_file(jvm_path) or DEFAULT_JVM
    node_content = await FileService.read_file(node_path) or DEFAULT_NODE

    return templates.TemplateResponse(
        "config/edit.html",
        {
            "request": request,
            "config_content": config_content,
            "jvm_content": jvm_content,
            "node_content": node_content,
            "config_errors": [],
            "jvm_errors": [],
            "node_errors": [],
            "active": "config",
        }
    )


@router.post("/save")
async def save_config(
    request: Request,
    config_content: str = Form(...),
    jvm_content: str = Form(...),
    node_content: str = Form(...),
):
    config_errors = validate_trino_config(config_content)
    jvm_errors = validate_jvm_config(jvm_content)
    node_errors = validate_node_properties(node_content)

    if config_errors or jvm_errors or node_errors:
        return templates.TemplateResponse(
            "config/edit.html",
            {
                "request": request,
                "config_content": config_content,
                "jvm_content": jvm_content,
                "node_content": node_content,
                "config_errors": config_errors,
                "jvm_errors": jvm_errors,
                "node_errors": node_errors,
                "active": "config",
            },
            status_code=422,
        )

    await FileService.write_file(settings.TRINO_CONFIG_DIR / "config.properties", config_content)
    await FileService.write_file(settings.TRINO_CONFIG_DIR / "jvm.config", jvm_content)
    await FileService.write_file(settings.TRINO_CONFIG_DIR / "node.properties", node_content)

    return RedirectResponse(url="/config/", status_code=303)
