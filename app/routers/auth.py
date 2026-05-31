from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
import secrets

from app.config import settings


def check_auth(request: Request) -> bool:
    return request.session.get("authenticated") is True


def require_auth(request: Request):
    if not check_auth(request):
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"},
        )
