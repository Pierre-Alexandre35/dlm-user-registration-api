from fastapi import FastAPI
from app.config import settings
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router

app = FastAPI(title="Hello API", version="0.1.0")

# Mount routers under /v1 (from settings.api_prefix)
app.include_router(users_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


@app.get("/", tags=["root"])
def read_root():
    return {"message": "Hello PAM"}
