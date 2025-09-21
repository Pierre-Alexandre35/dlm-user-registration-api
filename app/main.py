from fastapi import FastAPI
from app.routers.users import router as users_router

app = FastAPI(title="Hello API", version="0.1.0")
app.include_router(users_router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


@app.get("/", tags=["root"])
def read_root():
    return {"message": "Hello PAM"}
