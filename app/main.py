from fastapi import FastAPI
from pydantic import BaseModel
import re, time

try:
    from app.llm import generate as llm_generate
    USE_LLM = True
except Exception:
    # Fallback if transformers isn't available
    USE_LLM = False
    def llm_generate(prompt: str, max_new_tokens: int = 40, seed: int = 42) -> str:
        return "Answer: " + prompt[:80]

app = FastAPI(title="PromptFlow-Mimic Demo (Local LLM)")

class Ask(BaseModel):
    question: str

# simple PII-ish detector for demo purposes
PII_PATTERNS = [
    r"\bssn\b",
    r"\bsocial security\b",
    r"\bsalary\b",
    r"\bcredit card\b",
    r"\biban\b",
    r"\bpassport\b",
    r"\bpersonal (email|e-mail)\b"
]
PII_RE = re.compile("|".join(PII_PATTERNS), re.IGNORECASE)

REFUSAL_TEXT = (
    "I can’t share personal or sensitive information. "
    "I cannot share that data due to our policy."
)


@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(payload: Ask):
    q = payload.question.strip()
    # guardrail/refusal demo
    if PII_RE.search(q):
        return {"answer": REFUSAL_TEXT, "citations": []}

    # pretend we build a prompt with "retrieved context"
    context = "Context: company policy; payment terms net 60; see demo source."
    prompt = f"{context}\n\nQ: {q}\nA:"
    start = time.time()
    completion = llm_generate(prompt, max_new_tokens=40, seed=123)
    latency_ms = int((time.time() - start) * 1000)

    # fake a single citation
    citations = ["https://example.com/source"]
    answer = completion if completion else "Answer: (no output)"
    # include a SOURCE tag for demos if you prefer
    # answer += " [SOURCE: demo_corpus]"

    return {"answer": answer, "citations": citations, "latency_ms": latency_ms}
