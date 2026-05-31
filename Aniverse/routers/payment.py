import os
import hmac
import hashlib
import httpx
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from services.supabase_client import supabase

router = APIRouter()
templates = Jinja2Templates(directory="templates")

KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")


@router.get("/checkout")
async def checkout_page(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/auth/login?redirect=/payment/checkout", status_code=302)
    return templates.TemplateResponse("checkout.html", {
        "request": request,
        "user": user,
        "razorpay_key_id": KEY_ID,
    })


@router.post("/create-order")
async def create_order(request: Request):
    user = request.session.get("user")
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    body = await request.json()
    amount = body.get("amount", 0)

    # if not KEY_ID or not KEY_SECRET:
    #     return JSONResponse({"error": "Payment gateway not configured"}, status_code=500)

    # try:
    #     import base64
    #     credentials = base64.b64encode(f"{KEY_ID}:{KEY_SECRET}".encode()).decode()
    #     async with httpx.AsyncClient() as client:
    #         res = await client.post(
    #             "https://api.razorpay.com/v1/orders",
    #             headers={
    #                 "Authorization": f"Basic {credentials}",
    #                 "Content-Type": "application/json",
    #             },
    #             json={
    #                 "amount": int(amount * 100),
    #                 "currency": "INR",
    #                 "receipt": f"aniverse_{int(__import__('time').time())}",
    #             },
    #         )
    #     order = res.json()
    #     return JSONResponse({
    #         "order_id": order["id"],
    #         "amount": order["amount"],
    #         "currency": order["currency"],
    #         "key_id": KEY_ID,
    #     })
    # except Exception as e:
    #     return JSONResponse({"error": str(e)}, status_code=500)

    return JSONResponse({
        "order_id": "mock_order_id",
        "amount": int(amount * 100),
        "currency": "INR",
        "key_id": KEY_ID,
    })


@router.post("/verify")
async def verify_payment(request: Request):
    user = request.session.get("user")
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    body = await request.json()
    rzp_order_id = body.get("razorpay_order_id", "")
    rzp_payment_id = body.get("razorpay_payment_id", "")
    rzp_signature = body.get("razorpay_signature", "")
    cart_items = body.get("cart_items", [])
    shipping_address = body.get("shipping_address", {})
    total_amount = body.get("total_amount", 0)

    # Verify signature
    # generated = hmac.new(
    #     KEY_SECRET.encode(),
    #     f"{rzp_order_id}|{rzp_payment_id}".encode(),
    #     hashlib.sha256,
    # ).hexdigest()

    # if generated != rzp_signature:
    #     return JSONResponse({"error": "Payment verification failed"}, status_code=400)

    # try:
    #     order_res = supabase.table("orders").insert({
    #         "user_id": user["id"],
    #         "status": "processing",
    #         "total_amount": total_amount,
    #         "shipping_address": shipping_address,
    #     }).execute()

    #     order_id = order_res.data[0]["id"]

    #     items = [
    #         {
    #             "order_id": order_id,
    #             "product_id": item["id"],
    #             "quantity": item["quantity"],
    #             "size": item["size"],
    #             "color": item["color"],
    #             "price": item["price"],
    #         }
    #         for item in cart_items
    #     ]
    #     supabase.table("order_items").insert(items).execute()

    #     return JSONResponse({"success": True, "order_id": order_id})
    # except Exception as e:
    #     return JSONResponse({"error": str(e)}, status_code=500)

    return JSONResponse({"success": True, "order_id": "mock_order_id"})


@router.get("/success")
async def success(request: Request, order_id: str = ""):
    user = request.session.get("user")
    return templates.TemplateResponse("checkout_success.html", {
        "request": request,
        "user": user,
        "order_id": order_id,
    })
