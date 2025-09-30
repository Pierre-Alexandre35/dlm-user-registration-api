from fastapi import FastAPI, Body
from pydantic import BaseModel
import sys
import re

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
    # Extract 4-digit code from body if present
    match = re.search(r"\b(\d{4})\b", payload.body)
    code = match.group(1) if match else "????"

    # Important: match smoke test parser (expects "Code: XXXX")
    print(
        f"[SMTP] Code: {code} To={payload.to} Subject={payload.subject}",
        file=sys.stderr,
    )
    return {"status": "sent"}
