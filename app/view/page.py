from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="./app/view/templates")

@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/assets/favicon.ico")

@router.get("/sitemap.xml", include_in_schema=False)
async def sitemap():
    return FileResponse("app/static/assets/sitemap.xml")

@router.get("/robots.txt", include_in_schema=False)
async def robots():
    return FileResponse("app/static/assets/robots.txt")

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/convert-page", response_class=HTMLResponse)
def convert(request: Request):
    return templates.TemplateResponse("convert.html", {"request": request})
