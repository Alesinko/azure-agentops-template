from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="PromptFlow-Mimic Demo")

class Ask(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(payload: Ask):
    q = payload.question.lower()
    # pretend we retrieved from a corpus and enforced policy
    if "salary" in q:
        return {"answer": "I can’t share personal salary information.", "citations": []}
    return {"answer": f"Answer: {payload.question}", "citations": ["https://example.com/source"]}
