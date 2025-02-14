from fastapi import FastAPI
import uvicorn
from app.api.v1.endpoints import converter
from app.core.config import settings

app = FastAPI(
  title=settings.PROJECT_NAME,
  openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(
  converter.router,
  prefix=settings.API_V1_STR,
  tags=["converter"]
)