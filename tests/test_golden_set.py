import csv, json, time, os
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

            ok = False
            if r.status_code == 200:
                # parse JSON for more robust checks
                j = r.json()
                # if we're checking "citations", verify the key exists (and optionally non-empty)
                if expect == "citations":
                    ok = ("citations" in j)  # or: ("citations" in j and len(j["citations"]) >= 1)
                else:
                    # fall back to substring match on text for other cases
                    ok = (expect in r.text)

            passed += int(ok)
            rows.append({
                "id": i,
                "question": q,
                "expected_contains": expect,
                "status_code": r.status_code,
                "ok": ok
            })

    report = {
        "started_at": start,
        "ended_at": time.time(),
        "duration_sec": round(time.time() - start, 3),
        "passed": passed,
        "total": len(rows),
        "cases": rows
    }
    os.makedirs("reports", exist_ok=True)
    with open("reports/evals.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    assert passed == len(rows), f"Golden-set failed: {passed}/{len(rows)}"
