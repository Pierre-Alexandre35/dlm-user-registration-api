from fastapi import FastAPI

app = FastAPI(title="Hello API", version="0.1.0")


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


@app.get("/", tags=["root"])
def read_root():
    return {"message": "Hello PAM"}
