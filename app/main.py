from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI(title="Azure AgentOps Template")

class AskRequest(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(req: AskRequest):
    # Deterministic, skeleton response (no external LLM)
    answer = f"Answer: {req.question} [SOURCE: demo_corpus]"
    return {"answer": answer, "citations": ["https://example.com/demo-source"]}

