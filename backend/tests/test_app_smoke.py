"""
Smoke test: exercises signup/login/health without hitting the network-gated
embedding model, by monkeypatching get_embeddings with a fake in-process
embedding function. This proves the FastAPI app, routing, auth, and DB layers
are wired correctly end to end.
"""
import os
import sys

os.environ["DATABASE_URL"] = "sqlite:///./test_smoke.db"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app.services.document_service as document_service


class FakeEmbeddings:
    def embed_documents(self, texts):
        return [[float(len(t) % 7)] * 8 for t in texts]

    def embed_query(self, text):
        return [float(len(text) % 7)] * 8


document_service.get_embeddings = lambda: FakeEmbeddings()

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_signup_login_flow():
    r = client.post("/api/auth/signup", json={"email": "a@test.com", "password": "pw123456"})
    assert r.status_code == 201, r.text

    r = client.post(
        "/api/auth/login",
        data={"username": "a@test.com", "password": "pw123456"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    assert token

    r = client.get("/api/documents/", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text
    assert r.json() == []


def test_wrong_password_rejected():
    r = client.post(
        "/api/auth/login",
        data={"username": "a@test.com", "password": "wrongpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 401


def _get_token(email):
    client.post("/api/auth/signup", json={"email": email, "password": "pw123456"})
    r = client.post(
        "/api/auth/login",
        data={"username": email, "password": "pw123456"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return r.json()["access_token"]


def test_upload_and_chat_flow(tmp_path):
    import app.services.rag_service as rag_service

    class FakeLLMResponse:
        content = "This is a fake answer citing the document."

    class FakeLLM:
        def invoke(self, prompt):
            return FakeLLMResponse()

    rag_service.get_llm = lambda: FakeLLM()

    token = _get_token("b@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Build a minimal real PDF with actual text content (not just a blank page)
    # so the ingestion pipeline (loader -> splitter -> embed -> store) is
    # exercised end to end, matching a real upload.
    from reportlab.pdfgen import canvas

    pdf_path = tmp_path / "sample.pdf"
    c = canvas.Canvas(str(pdf_path))
    c.drawString(100, 750, "This is a technical document about RAG systems.")
    c.drawString(100, 730, "It explains retrieval augmented generation in detail.")
    c.save()

    with open(pdf_path, "rb") as f:
        r = client.post(
            "/api/documents/upload",
            headers=headers,
            files={"file": ("sample.pdf", f, "application/pdf")},
        )
    assert r.status_code == 200, r.text

    r = client.get("/api/documents/", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) == 1

    r = client.post("/api/chat/", headers=headers, json={"query": "What is this document about?"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert "answer" in body

    r = client.get("/api/chat/history", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) >= 1
