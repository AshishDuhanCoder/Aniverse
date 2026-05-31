from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from services.supabase_client import supabase
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def _set_session(request: Request, user, session):
    request.session["user"] = {
        "id": user.id,
        "email": user.email,
        "name": (user.user_metadata or {}).get("full_name", user.email.split("@")[0]),
        "is_admin": (user.app_metadata or {}).get("role") == "admin",
    }
    request.session["access_token"] = session.access_token


@router.get("/login")
async def login_page(request: Request, redirect: str = "/"):
    if request.session.get("user"):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("auth/login.html", {
        "request": request, "user": None, "redirect": redirect, "error": None
    })


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    redirect: str = Form("/"),
):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        _set_session(request, res.user, res.session)
        return RedirectResponse(redirect, status_code=302)
    except Exception as e:
        return templates.TemplateResponse("auth/login.html", {
            "request": request,
            "user": None,
            "redirect": redirect,
            "error": "Invalid email or password.",
        })


@router.get("/register")
async def register_page(request: Request):
    if request.session.get("user"):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("auth/register.html", {
        "request": request, "user": None, "error": None, "success": False
    })


@router.post("/register")
async def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm: str = Form(...),
):
    if password != confirm:
        return templates.TemplateResponse("auth/register.html", {
            "request": request, "user": None,
            "error": "Passwords do not match.", "success": False,
        })
    if len(password) < 6:
        return templates.TemplateResponse("auth/register.html", {
            "request": request, "user": None,
            "error": "Password must be at least 6 characters.", "success": False,
        })
    try:
        supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"full_name": name}},
        })
        return templates.TemplateResponse("auth/register.html", {
            "request": request, "user": None, "error": None,
            "success": True, "registered_email": email,
        })
    except Exception as e:
        return templates.TemplateResponse("auth/register.html", {
            "request": request, "user": None,
            "error": str(e), "success": False,
        })


@router.get("/google")
async def google_login(request: Request, redirect: str = "/"):
    try:
        import os
        base_url = os.getenv("SITE_URL", "http://localhost:8000")
        res = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {"redirect_to": f"{base_url}/auth/callback?redirect={redirect}"},
        })
        return RedirectResponse(res.url, status_code=302)
    except Exception:
        return RedirectResponse("/auth/login?error=oauth_failed", status_code=302)


@router.get("/callback")
async def auth_callback(request: Request, code: Optional[str] = None, redirect: str = "/"):
    if code:
        try:
            res = supabase.auth.exchange_code_for_session({"auth_code": code})
            _set_session(request, res.user, res.session)
        except Exception:
            pass
    return RedirectResponse(redirect, status_code=302)


@router.get("/logout")
async def logout(request: Request):
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    request.session.clear()
    return RedirectResponse("/", status_code=302)
