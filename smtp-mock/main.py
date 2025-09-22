from fastapi import FastAPI, Body
from pydantic import BaseModel
import sys

app = FastAPI(title="SMTP Mock")


class SendPayload(BaseModel):
    to: str
    subject: str
    body: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/send")
def send_email(payload: SendPayload = Body(...)):
    print(
        f"[SMTP-MOCK] To={payload.to} Subject={payload.subject} Body={payload.body}",
        file=sys.stderr,
    )
    return {"status": "sent"}
