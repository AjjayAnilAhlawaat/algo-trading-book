from fastapi.testclient import TestClient

from phonetic_engine.app import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_align_contract_shape():
    r = client.post("/v1/align", json={"text": "the water", "observed": ["ð", "ə", "ʋ", "ɔː", "ʈ", "ə", "r"]})
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"tokens", "markers", "top_levers", "unknown_words"}
    assert {t["state"] for t in body["tokens"]} <= {"match", "near", "miss"}
    assert len(body["markers"]) == 6


def test_align_rejects_empty_text():
    assert client.post("/v1/align", json={"text": "", "observed": []}).status_code == 422


def test_passage_endpoint():
    assert "Victor" in client.get("/v1/diagnostic/passage").json()["text"]
