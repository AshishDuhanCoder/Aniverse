from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from services.supabase_client import supabase
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/shop")
async def shop(
    request: Request,
    category: Optional[str] = None,
    filter: Optional[str] = None,
    sort: str = "created_at:desc",
    max_price: Optional[int] = None,
):
    user = request.session.get("user")

    try:
        query = supabase.table("products").select("*, category:categories(name,slug)")

        if filter == "new":
            query = query.order("created_at", desc=True).limit(20)
        elif filter == "bestsellers":
            query = query.eq("featured", True)
        else:
            sort_field, sort_dir = sort.split(":") if ":" in sort else ("created_at", "desc")
            query = query.order(sort_field, desc=(sort_dir == "desc"))

        if max_price:
            query = query.lte("price", max_price)

        if category:
            cats_res = supabase.table("categories").select("id").eq("slug", category).execute()
            cat_ids = [c["id"] for c in (cats_res.data or [])]
            if cat_ids:
                query = query.in_("category_id", cat_ids)

        res = query.execute()
        products = res.data or []

        categories_res = supabase.table("categories").select("*").execute()
        categories = categories_res.data or []
    except Exception:
        products, categories = [], []

    return templates.TemplateResponse("shop.html", {
        "request": request,
        "user": user,
        "products": products,
        "categories": categories,
        "current_category": category,
        "current_filter": filter,
        "current_sort": sort,
        "max_price": max_price or 5000,
    })


@router.get("/product/{product_id}")
async def product_detail(request: Request, product_id: str):
    user = request.session.get("user")

    try:
        res = supabase.table("products").select("*, category:categories(name,slug)").eq("id", product_id).single().execute()
        product = res.data
    except Exception:
        product = None

    if not product:
        return templates.TemplateResponse("404.html", {"request": request, "user": user}, status_code=404)

    return templates.TemplateResponse("product.html", {
        "request": request,
        "user": user,
        "product": product,
    })
