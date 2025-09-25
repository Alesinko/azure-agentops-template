import csv, json, os, datetime
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def run():
    rows = []
    with open("evals/golden_set.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            q = row["question"].strip().strip('"')
            expect = row["expected_contains"]
            r = client.post("/ask", json={"question": q})
            ok = (r.status_code == 200) and (expect in r.text)
            rows.append({
                "id": i, "question": q, "expected_contains": expect,
                "status_code": r.status_code, "ok": ok
            })
    result = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "passed": sum(1 for r in rows if r["ok"]),
        "total": len(rows),
        "cases": rows
    }
    os.makedirs("reports", exist_ok=True)
    with open("reports/evals.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    # exit non-zero if any failed (gate)
    if result["passed"] != result["total"]:
        raise SystemExit(1)

if __name__ == "__main__":
    run()
