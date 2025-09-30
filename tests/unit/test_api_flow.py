from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register_and_activate(monkeypatch):
    sent_codes = {}

    # Patch mailer to capture OTP
    def fake_send_code(email, code):
        sent_codes[email] = code

    monkeypatch.setattr(
        "app.infrastructure.smtp.smtp_client.SmtpMailer.send_code", fake_send_code
    )

    # 1) Register user
    r = client.post(
        "/users", json={"email": "carol@example.com", "password": "Secret123!"}
    )
    assert r.status_code == 201
    uid = r.json()["id"]

    # 2) Activate user with Basic Auth
    code = sent_codes["carol@example.com"]
    r = client.post(
        f"/auth/activate?code={code}", auth=("carol@example.com", "Secret123!")
    )
    assert r.status_code == 200
    assert r.json()["detail"] == "Account activated"
