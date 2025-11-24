import os, json, datetime, subprocess, shutil

EVIDENCE_DIR = "governance"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def git_last():
    try:
        return subprocess.check_output(["git","log","-1","--pretty=%h %s"]).decode().strip()
    except Exception:
        return "local"

def agent_card():
    return f"""# Agent/App Card (Demo)
Purpose: PromptFlow-like evals using pytest + golden_set.csv
Scope: Deterministic /ask endpoint (no external LLM)
Owners: (replace)
Build: {git_last()}
Date (UTC): {datetime.datetime.utcnow().isoformat()}Z

Risks & Controls:
- Hallucination → Golden-set gate
- PII/Salary → Policy refusal + test
- Change control → CI gates + approval on PR
"""

def eval_report():
    path = "reports/evals.json"
    if not os.path.exists(path):
        return "# Evaluation Report\nNo report found."

    data = json.load(open(path, encoding="utf-8"))
    hdr = [
        "# Evaluation Report",
        f"**Summary:** Passed {data['passed']} / {data['total']}  |  Duration: {data['duration_sec']}s",
    ]
    if "latency_ms" in data:
        hdr.append(f"**Latency:** p50={data['latency_ms'].get('p50',0)} ms, p95={data['latency_ms'].get('p95',0)} ms")
    if "estimated_total_cost_usd" in data:
        hdr.append(f"**Est. cost (total):** ${data['estimated_total_cost_usd']}")

    cases = ["\n## Cases"]
    for c in data["cases"]:
        cases.append(
            f"- Q{c['id']} [{c.get('type','contains')}]: ok={c['ok']} | "
            f"lat={c.get('latency_ms',0)} ms | cost=${c.get('estimated_cost_usd',0)} | "
            f"expect=`{c.get('expected','')}`"
        )
    return "\n".join(hdr + cases)


def main():
    write(os.path.join(EVIDENCE_DIR,"AGENT_CARD.md"), agent_card())
    write(os.path.join(EVIDENCE_DIR,"EVAL_REPORT.md"), eval_report())
    # Approval stub & Changelog
    write(os.path.join(EVIDENCE_DIR,"APPROVAL.txt"),
          "Approved: (stub) Replace with CAB/ServiceNow record\n")
    cl = os.path.join(EVIDENCE_DIR,"CHANGELOG.md")
    with open(cl, "a", encoding="utf-8") as f:
        if os.path.getsize(cl) == 0 if os.path.exists(cl) else True:
            f.write("# Changelog\n")
        f.write(f"- {datetime.datetime.utcnow().isoformat()}Z  {git_last()}\n")
    # Lineage placeholder
    os.makedirs(os.path.join(EVIDENCE_DIR,"lineage"), exist_ok=True)
    with open(os.path.join(EVIDENCE_DIR,"lineage","LINEAGE.txt"),"w",encoding="utf-8") as f:
        f.write("Demo lineage: Sources -> Curated -> Index -> Prompt -> Answer\n")

if __name__ == "__main__":
    main()
