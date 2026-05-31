from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from services.supabase_client import supabase

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def my_orders(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/auth/login?redirect=/orders", status_code=302)

    try:
        res = supabase.table("orders").select(
            "*, items:order_items(*, product:products(name, image_url))"
        ).eq("user_id", user["id"]).order("created_at", desc=True).execute()
        orders = res.data or []
    except Exception:
        orders = []

    return templates.TemplateResponse("orders.html", {
        "request": request,
        "user": user,
        "orders": orders,
    })
