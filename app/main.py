from fastapi import FastAPI

# from app.auth.router import router as auth_router
from app.ai.router import router as new_graph
# from app.products.router import router as product_router
# from app.orders.router import router as order_router
# from app.chatbot.router import router as chatbot_router
# from app.websocket.router import router as websocket_router

from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
)


from slowapi.errors import (
    RateLimitExceeded
)

from slowapi.middleware import (
    SlowAPIMiddleware
)

from app.core.limiter import limiter

app.state.limiter = limiter

app.add_middleware(
    SlowAPIMiddleware
)

app.include_router(new_graph)
# app.include_router(websocket_router)
# app.include_router(chatbot_router)
# app.include_router(auth_router)
# app.include_router(product_router)
# app.include_router(order_router)


from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(
    directory="templates"
)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        }
    )




# @app.get("/")
# async def root():
#     return {
#         "message": "AI Ecommerce Support Running"
#     }