# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Web page routes — Jinja2 templates for the frontend."""

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Environment, FileSystemLoader, Template

from app.api.deps import get_current_user_for_web

BASE_DIR = Path(__file__).resolve().parent.parent
template_dir = str(BASE_DIR / "templates")

# Create environment with cache disabled to avoid Jinja2 LRUCache issue
env = Environment(
    loader=FileSystemLoader(template_dir),
    auto_reload=False,
    cache_size=0,  # Disable template cache
)
JINJA2_GLOBALS: dict[str, Any] = {}


def template_response(name: str, context: dict[str, Any]) -> HTMLResponse:
    """Render a Jinja2 template and return HTMLResponse."""
    template: Template = env.get_template(name)
    combined = {**JINJA2_GLOBALS, **context}
    html = template.render(**combined)
    return HTMLResponse(content=html)

router = APIRouter(tags=["web"])


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(
    request: Request,
    _current_user: dict = Depends(get_current_user_for_web),
) -> HTMLResponse:
    """Dashboard page."""
    return template_response("index.html", {"request": request})


@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request) -> HTMLResponse:
    """Login page (public)."""
    return template_response("login.html", {"request": request})


@router.get("/players", response_class=HTMLResponse, include_in_schema=False)
async def players_list(
    request: Request,
    _current_user: dict = Depends(get_current_user_for_web),
) -> HTMLResponse:
    """Players list page."""
    return template_response("players/list.html", {"request": request})


@router.get("/players/create", response_class=HTMLResponse, include_in_schema=False)
async def player_create_page(
    request: Request,
    current_user: dict = Depends(get_current_user_for_web),
) -> HTMLResponse:
    """Player create form (admin only)."""
    if not current_user.is_admin:
        return RedirectResponse(url="/players", status_code=303)
    return template_response("players/create.html", {"request": request})


@router.get("/players/{player_id}/edit", response_class=HTMLResponse, include_in_schema=False)
async def player_edit_page(
    request: Request,
    player_id: int,
    current_user: dict = Depends(get_current_user_for_web),
) -> HTMLResponse:
    """Player edit form (admin only)."""
    if not current_user.is_admin:
        return RedirectResponse(url="/players", status_code=303)
    return template_response("players/edit.html", {"request": request, "player_id": player_id})


@router.get("/players/{player_id}/delete", response_class=HTMLResponse, include_in_schema=False)
async def player_delete_page(
    request: Request,
    player_id: int,
    current_user: dict = Depends(get_current_user_for_web),
) -> HTMLResponse:
    """Player delete confirmation (admin only, redirects after delete)."""
    if not current_user.is_admin:
        return RedirectResponse(url="/players", status_code=303)
    return RedirectResponse(url=f"/players/{player_id}", status_code=303)


@router.get("/players/{player_id}", response_class=HTMLResponse, include_in_schema=False)
async def player_detail(
    request: Request,
    player_id: int,
    _current_user: dict = Depends(get_current_user_for_web),
) -> HTMLResponse:
    """Player detail page."""
    return template_response("players/detail.html", {"request": request, "player_id": player_id})


@router.get("/tournaments", response_class=HTMLResponse, include_in_schema=False)
async def tournaments_list(
    request: Request,
    _current_user: dict = Depends(get_current_user_for_web),
) -> HTMLResponse:
    """Tournaments list page."""
    return template_response("tournaments/list.html", {"request": request})


@router.get("/tournaments/create", response_class=HTMLResponse, include_in_schema=False)
async def tournament_create_page(
    request: Request,
    current_user: dict = Depends(get_current_user_for_web),
) -> HTMLResponse:
    """Tournament create form (admin only)."""
    if not current_user.is_admin:
        return RedirectResponse(url="/tournaments", status_code=303)
    return template_response("tournaments/create.html", {"request": request})


@router.get("/tournaments/{tournament_id}/edit", response_class=HTMLResponse, include_in_schema=False)
async def tournament_edit_page(
    request: Request,
    tournament_id: int,
    current_user: dict = Depends(get_current_user_for_web),
) -> HTMLResponse:
    """Tournament edit form (admin only)."""
    if not current_user.is_admin:
        return RedirectResponse(url="/tournaments", status_code=303)
    return template_response("tournaments/edit.html", {"request": request, "tournament_id": tournament_id})


@router.get("/tournaments/{tournament_id}", response_class=HTMLResponse, include_in_schema=False)
async def tournament_detail(
    request: Request,
    tournament_id: int,
    _current_user: dict = Depends(get_current_user_for_web),
) -> HTMLResponse:
    """Tournament detail page."""
    return template_response("tournaments/detail.html", {"request": request, "tournament_id": tournament_id})
