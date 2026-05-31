from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from services.supabase_client import supabase

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def home(request: Request):
    user = request.session.get("user")

    try:
        products_res = supabase.table("products").select("*, category:categories(name,slug)").eq("featured", True).order("created_at", desc=True).limit(8).execute()
        categories_res = supabase.table("categories").select("*").order("created_at").limit(4).execute()
        settings_res = supabase.table("site_settings").select("*").execute()

        settings = {s["key"]: s["value"] for s in (settings_res.data or [])}
        products = products_res.data or []
        categories = categories_res.data or []
    except Exception:
        products, categories, settings = [], [], {}

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "products": products,
        "categories": categories,
        "settings": settings,
    })


@router.post("/newsletter")
async def newsletter(request: Request):
    try:
        body = await request.json()
        email = (body.get("email") or "").strip()
        if not email:
            return JSONResponse({"ok": False, "message": "Email required"})
        supabase.table("newsletter_subscribers").upsert({"email": email}).execute()
        return JSONResponse({"ok": True, "message": "You're in! 🎉"})
    except Exception:
        return JSONResponse({"ok": False, "message": "Something went wrong."})
