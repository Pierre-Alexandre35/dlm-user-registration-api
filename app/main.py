from fastapi import FastAPI
from app.config import settings
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router
from app.db.cursor import pool

app = FastAPI(title="Auth API", version="1.0.0")

app.include_router(users_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)


@app.on_event("startup")
def open_db_pool():
    pool.open()


@app.on_event("shutdown")
def close_db_pool():
    pool.close()


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
