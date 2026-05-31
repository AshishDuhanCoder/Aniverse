import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

from routers import home, shop, auth, orders, payment, admin

load_dotenv()

app = FastAPI(title="Aniverse — Wear The Universe")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "change-me-in-production"),
    max_age=60 * 60 * 24 * 7,  # 7 days
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(home.router)
app.include_router(shop.router)
app.include_router(auth.router, prefix="/auth")
app.include_router(orders.router, prefix="/orders")
app.include_router(payment.router, prefix="/payment")
app.include_router(admin.router, prefix="/admin")


@app.exception_handler(404)
async def not_found(request: Request, exc):
    templates = Jinja2Templates(directory="templates")
    return templates.TemplateResponse(
        "404.html", {"request": request, "user": request.session.get("user")}, status_code=404
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
