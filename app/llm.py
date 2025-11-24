import os, random
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

_MODEL_NAME = os.getenv("LOCAL_LLM_NAME", "distilgpt2")

# Lazy globals so the import is cheap
_tokenizer = None
_model = None

def _load():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME)
        _model = AutoModelForCausalLM.from_pretrained(_MODEL_NAME)
        _model.eval()

def generate(prompt: str, max_new_tokens: int = 40, seed: int = 42) -> str:
    _load()
    torch.manual_seed(seed)
    inputs = _tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        outputs = _model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True, temperature=0.8, top_p=0.95, pad_token_id=_tokenizer.eos_token_id
        )
    text = _tokenizer.decode(outputs[0], skip_special_tokens=True)
    return text[len(prompt):].strip()  # just the completion
