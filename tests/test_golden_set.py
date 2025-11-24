import csv, json, time, os, math
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

TOKEN_EST_DIVISOR = 4.0    # ~4 chars per token (very rough)
USD_PER_1K_TOKENS = 0.0005 # toy price for demo; adjust as needed

def estimate_tokens(s: str) -> int:
    return max(1, int(len(s) / TOKEN_EST_DIVISOR))

def test_health():
    r = client.get("/health")
    assert r.status_code == 200

def test_golden_set(tmp_path):
    rows, passed = [], 0
    start_all = time.time()

    with open("evals/golden_set.csv", newline='', encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f), start=1):
            q = row.get("question","").strip().strip('"')
            expect = row.get("expected_contains","").strip()
            rtype = row.get("type","contains").strip()  # NEW: supports "refuse" and "citations"
            t0 = time.time()
            r = client.post("/ask", json={"question": q})
            elapsed_ms = int((time.time() - t0) * 1000)

            ok = False
            cost_usd = 0.0
            if r.status_code == 200:
                j = r.json()
                ans_text = j.get("answer","")
                body_text = r.text
                # cost estimate: prompt+answer length
                tokens = estimate_tokens(q + " " + ans_text)
                cost_usd = (tokens / 1000.0) * USD_PER_1K_TOKENS

                if rtype == "refuse":
                    ok = ("can’t share" in ans_text.lower() or "cannot share" in ans_text.lower())
                elif rtype == "citations":
                    ok = ("citations" in j and isinstance(j["citations"], list) and len(j["citations"]) >= 1)
                else:
                    ok = (expect in body_text)

            passed += int(ok)
            rows.append({
                "id": i,
                "type": rtype,
                "question": q,
                "expected": expect,
                "status_code": r.status_code,
                "ok": ok,
                "latency_ms": elapsed_ms,
                "estimated_cost_usd": round(cost_usd, 6)
            })

    duration_sec = round(time.time() - start_all, 3)
    agg_latency_p50 = percentile([r["latency_ms"] for r in rows], 50)
    agg_latency_p95 = percentile([r["latency_ms"] for r in rows], 95)
    total_cost = round(sum(r["estimated_cost_usd"] for r in rows), 6)

    report = {
        "duration_sec": duration_sec,
        "passed": passed,
        "total": len(rows),
        "latency_ms": {"p50": agg_latency_p50, "p95": agg_latency_p95},
        "estimated_total_cost_usd": total_cost,
        "cases": rows
    }

    os.makedirs("reports", exist_ok=True)
    with open("reports/evals.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    assert passed == len(rows), f"Golden-set failed: {passed}/{len(rows)}"

def percentile(values, p):
    if not values:
        return 0
    values = sorted(values)
    k = (len(values)-1) * (p/100.0)
    f = math.floor(k); c = math.ceil(k)
    if f == c: return values[int(k)]
    d0 = values[f] * (c-k); d1 = values[c] * (k-f)
    return int(d0 + d1)
