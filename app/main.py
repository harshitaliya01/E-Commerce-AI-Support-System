from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from app.chatbot.router import router
from fastapi.responses import HTMLResponse
from app.core.config import settings

from app.core.limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware

app = FastAPI(title=settings.APP_NAME)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(router)

templates = Jinja2Templates(directory="templates")
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request,name="index.html",context={"request": request})