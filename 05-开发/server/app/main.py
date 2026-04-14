"""应用入口。"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import users, spots, categories, forbidden_zones, weather, share

settings = get_settings()

app = FastAPI(title="钓了吗 API", version="1.0.0")

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/v1", tags=["用户"])
app.include_router(spots.router, prefix="/v1", tags=["标点"])
app.include_router(categories.router, prefix="/v1", tags=["分类"])
app.include_router(forbidden_zones.router, prefix="/v1", tags=["禁钓区"])
app.include_router(weather.router, prefix="/v1", tags=["天气"])
app.include_router(share.router, prefix="/v1", tags=["分享"])


@app.get("/")
async def root():
    return {"msg": "钓了吗 API v1.0.0", "status": "ok"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
