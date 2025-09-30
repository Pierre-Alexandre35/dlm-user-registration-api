from fastapi import FastAPI
from app.api.routers import users, auth

app = FastAPI(title="User Registration API")

app.include_router(users.router)
app.include_router(auth.router)


@app.get("/health")
def health():
    return {"status": "ok"}
