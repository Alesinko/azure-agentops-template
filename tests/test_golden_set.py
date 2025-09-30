import csv, json, time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200

def test_golden_set(tmp_path):
    rows, passed = [], 0
    start = time.time()

    with open("evals/golden_set.csv", newline='', encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f), start=1):
            q = row["question"].strip().strip('"')
            expect = row["expected_contains"]
            r = client.post("/ask", json={"question": q})
            ok = (r.status_code == 200) and (expect in r.text)
            passed += int(ok)
            rows.append({
                "id": i,
                "question": q,
                "expected_contains": expect,
                "status_code": r.status_code,
                "ok": ok
            })

    end = time.time()
    report = {
        "started_at": start,
        "ended_at": end,
        "duration_sec": round(end - start, 3),
        "passed": passed,
        "total": len(rows),
        "cases": rows
    }
    tmp = tmp_path / "evals.json"
    tmp.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # save to repo-local path for evidence packaging
    import os
    os.makedirs("reports", exist_ok=True)
    with open("reports/evals.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Gate: require all cases to pass
    assert passed == len(rows), f"Golden-set failed: {passed}/{len(rows)}"
