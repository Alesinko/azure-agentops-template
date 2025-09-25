import os, json, shutil, datetime, subprocess, textwrap

GIT_SHA = os.getenv("GITHUB_SHA", "local")
RUN_ID  = os.getenv("GITHUB_RUN_ID", "local")
RUN_NUM = os.getenv("GITHUB_RUN_NUMBER", "0")

EVIDENCE_DIR = "governance"
REPORTS = "reports"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def agent_card():
    return f"""# Agent Card (Template)

**Purpose:** Demo skeleton for audit-ready LLMOps/AgentOps (no external LLM).
**Scope:** Echo-style /ask endpoint with deterministic citations.
**Owners:** You (replace)
**Limits:** Demo-only, no PII, no real corpus.

## Build
- Commit: `{GIT_SHA}`
- Run: `{RUN_ID}` #{RUN_NUM}
- Date (UTC): {datetime.datetime.utcnow().isoformat()}Z

## Risk & Controls (abridged)
- Hallucination risk → Golden-set eval gate
- Cost/latency → N/A (no external model)
- Change control → CI checks, approvals
"""

def eval_report():
    p = os.path.join(REPORTS, "evals.json")
    if os.path.exists(p):
        data = json.load(open(p, encoding="utf-8"))
        summary = f"Passed {data['passed']} / {data['total']} at {data['timestamp']}"
    else:
        summary = "NO EVAL REPORT FOUND"
        data = {"cases": []}
    lines = [f"# Evaluation Report\n\n**Summary:** {summary}\n\n## Cases\n"]
    for c in data["cases"]:
        lines.append(f"- Q{c['id']}: ok={c['ok']} (expect contains `{c['expected_contains']}`)")
    return "\n".join(lines)

def approval_stub():
    return textwrap.dedent(f"""\
    # Release Approval (Stub)
    Build: {RUN_ID} #{RUN_NUM}  Commit: {GIT_SHA}
    Decision: APPROVED (template)
    Approver: [REDACTED]
    Notes: Sample only. Replace with real CAB/approver record.
    """)

def changelog_entry():
    # Best effort get short git log
    try:
        log = subprocess.check_output(["git", "log", "-1", "--pretty=%h %s"]).decode().strip()
    except Exception:
        log = GIT_SHA
    return f"- {datetime.datetime.utcnow().isoformat()}Z  {log}\n"

def main():
    write(os.path.join(EVIDENCE_DIR, "AGENT_CARD.md"), agent_card())
    write(os.path.join(EVIDENCE_DIR, "EVAL_REPORT.md"), eval_report())
    write(os.path.join(EVIDENCE_DIR, "APPROVAL.txt"), approval_stub())
    # Append to CHANGELOG
    cl_path = os.path.join(EVIDENCE_DIR, "CHANGELOG.md")
    mode = "a" if os.path.exists(cl_path) else "w"
    with open(cl_path, mode, encoding="utf-8") as f:
        if mode == "w":
            f.write("# Changelog\n")
        f.write(changelog_entry())
    # Copy lineage placeholder
    os.makedirs(os.path.join(EVIDENCE_DIR, "lineage"), exist_ok=True)
    shutil.copyfile("docs/lineage_placeholder.png",
                    os.path.join(EVIDENCE_DIR, "lineage", "LINEAGE.png"))

if __name__ == "__main__":
    main()
