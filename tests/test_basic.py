from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_ask_returns_citation():
    r = client.post("/ask", json={"question": "What is governance?"})
    j = r.json()
    assert r.status_code == 200
    assert "Answer:" in j["answer"]
    assert isinstance(j["citations"], list) and len(j["citations"]) >= 1
