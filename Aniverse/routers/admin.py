from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from services.supabase_client import supabase_admin as db
from typing import Optional
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def require_admin(request: Request):
    user = request.session.get("user")
    if not user or not user.get("is_admin"):
        return None
    return user


@router.get("/")
async def dashboard(request: Request):
    user = require_admin(request)
    if not user:
        return RedirectResponse("/", status_code=302)

    try:
        products = db.table("products").select("id", count="exact").execute()
        orders = db.table("orders").select("id, total_amount, status, created_at").order("created_at", desc=True).limit(10).execute()
        subscribers = db.table("newsletter_subscribers").select("id", count="exact").execute()

        total_revenue = sum(o["total_amount"] for o in (orders.data or []))
        stats = {
            "products": products.count or 0,
            "orders": orders.count or 0,
            "revenue": total_revenue,
            "subscribers": subscribers.count or 0,
        }
        recent_orders = orders.data or []
    except Exception:
        stats = {"products": 0, "orders": 0, "revenue": 0, "subscribers": 0}
        recent_orders = []

    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request, "user": user,
        "stats": stats, "recent_orders": recent_orders,
    })


@router.get("/products")
async def products_list(request: Request):
    user = require_admin(request)
    if not user:
        return RedirectResponse("/", status_code=302)

    res = db.table("products").select("*, category:categories(name)").order("created_at", desc=True).execute()
    return templates.TemplateResponse("admin/products.html", {
        "request": request, "user": user, "products": res.data or [],
    })


@router.get("/products/new")
async def new_product_page(request: Request):
    user = require_admin(request)
    if not user:
        return RedirectResponse("/", status_code=302)

    cats = db.table("categories").select("*").execute()
    return templates.TemplateResponse("admin/product_form.html", {
        "request": request, "user": user,
        "categories": cats.data or [], "product": None, "error": None,
    })


@router.post("/products/new")
async def create_product(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    original_price: Optional[float] = Form(None),
    image_url: str = Form(""),
    category_id: str = Form(""),
    stock_count: int = Form(100),
    featured: bool = Form(False),
    slug: str = Form(""),
    sizes: str = Form("S,M,L,XL"),
    colors: str = Form('[{"name":"Black","hex":"#000000"}]'),
    tags: str = Form(""),
):
    user = require_admin(request)
    if not user:
        return RedirectResponse("/", status_code=302)

    try:
        payload = {
            "name": name,
            "description": description,
            "price": price,
            "original_price": original_price,
            "image_url": image_url,
            "category_id": category_id or None,
            "stock_count": stock_count,
            "featured": featured,
            "slug": slug or name.lower().replace(" ", "-"),
            "sizes": [s.strip() for s in sizes.split(",") if s.strip()],
            "colors": json.loads(colors) if colors else [],
            "tags": [t.strip() for t in tags.split(",") if t.strip()],
        }
        db.table("products").insert(payload).execute()
        return RedirectResponse("/admin/products", status_code=302)
    except Exception as e:
        cats = db.table("categories").select("*").execute()
        return templates.TemplateResponse("admin/product_form.html", {
            "request": request, "user": user,
            "categories": cats.data or [], "product": None, "error": str(e),
        })


@router.get("/products/{product_id}/edit")
async def edit_product_page(request: Request, product_id: str):
    user = require_admin(request)
    if not user:
        return RedirectResponse("/", status_code=302)

    product = db.table("products").select("*").eq("id", product_id).single().execute()
    cats = db.table("categories").select("*").execute()
    return templates.TemplateResponse("admin/product_form.html", {
        "request": request, "user": user,
        "categories": cats.data or [],
        "product": product.data,
        "error": None,
    })


@router.post("/products/{product_id}/edit")
async def update_product(
    request: Request,
    product_id: str,
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    original_price: Optional[float] = Form(None),
    image_url: str = Form(""),
    category_id: str = Form(""),
    stock_count: int = Form(100),
    featured: bool = Form(False),
    slug: str = Form(""),
    sizes: str = Form("S,M,L,XL"),
    colors: str = Form('[{"name":"Black","hex":"#000000"}]'),
    tags: str = Form(""),
):
    user = require_admin(request)
    if not user:
        return RedirectResponse("/", status_code=302)

    payload = {
        "name": name, "description": description, "price": price,
        "original_price": original_price, "image_url": image_url,
        "category_id": category_id or None, "stock_count": stock_count,
        "featured": featured,
        "slug": slug or name.lower().replace(" ", "-"),
        "sizes": [s.strip() for s in sizes.split(",") if s.strip()],
        "colors": json.loads(colors) if colors else [],
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
    }
    db.table("products").update(payload).eq("id", product_id).execute()
    return RedirectResponse("/admin/products", status_code=302)


@router.post("/products/{product_id}/delete")
async def delete_product(request: Request, product_id: str):
    user = require_admin(request)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    db.table("products").delete().eq("id", product_id).execute()
    return RedirectResponse("/admin/products", status_code=302)


@router.get("/orders")
async def orders_list(request: Request):
    user = require_admin(request)
    if not user:
        return RedirectResponse("/", status_code=302)

    res = db.table("orders").select("*, items:order_items(*)").order("created_at", desc=True).execute()
    return templates.TemplateResponse("admin/orders.html", {
        "request": request, "user": user, "orders": res.data or [],
    })


@router.post("/orders/{order_id}/status")
async def update_order_status(request: Request, order_id: str, status: str = Form(...)):
    user = require_admin(request)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    db.table("orders").update({"status": status}).eq("id", order_id).execute()
    return RedirectResponse("/admin/orders", status_code=302)


@router.get("/categories")
async def categories_page(request: Request):
    user = require_admin(request)
    if not user:
        return RedirectResponse("/", status_code=302)

    res = db.table("categories").select("*").order("created_at").execute()
    return templates.TemplateResponse("admin/categories.html", {
        "request": request, "user": user, "categories": res.data or [],
    })


@router.post("/categories/add")
async def add_category(
    request: Request,
    name: str = Form(...),
    slug: str = Form(""),
    description: str = Form(""),
):
    user = require_admin(request)
    if not user:
        return RedirectResponse("/", status_code=302)
    db.table("categories").insert({
        "name": name,
        "slug": slug or name.lower().replace(" ", "-"),
        "description": description,
    }).execute()
    return RedirectResponse("/admin/categories", status_code=302)


@router.post("/categories/{cat_id}/delete")
async def delete_category(request: Request, cat_id: str):
    user = require_admin(request)
    if not user:
        return RedirectResponse("/", status_code=302)
    db.table("categories").delete().eq("id", cat_id).execute()
    return RedirectResponse("/admin/categories", status_code=302)


@router.get("/settings")
async def settings_page(request: Request):
    user = require_admin(request)
    if not user:
        return RedirectResponse("/", status_code=302)

    res = db.table("site_settings").select("*").order("key").execute()
    return templates.TemplateResponse("admin/settings.html", {
        "request": request, "user": user, "settings": res.data or [],
    })


@router.post("/settings/update")
async def update_settings(request: Request):
    user = require_admin(request)
    if not user:
        return RedirectResponse("/", status_code=302)

    form = await request.form()
    for key, value in form.items():
        db.table("site_settings").upsert({"key": key, "value": value}).execute()
    return RedirectResponse("/admin/settings?saved=1", status_code=302)
