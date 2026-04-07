import os
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

MODEL_ID = os.getenv("MODEL_ID", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "180"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

app = FastAPI(title="Hermes HF Gateway")
_generator = None


class ChatReq(BaseModel):
    model: str = "default"
    messages: list[dict[str, Any]]


def get_generator():
    global _generator
    if _generator is None:
        _generator = pipeline("text-generation", model=MODEL_ID)
    return _generator


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "hermes-hf-gateway",
        "health": "/health",
        "chat": "/v1/chat/completions",
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {"ok": True, "model": MODEL_ID}


@app.post("/v1/chat/completions")
def chat_completions(req: ChatReq) -> dict[str, Any]:
    gen = get_generator()
    prompt_lines: list[str] = []
    for msg in req.messages:
        role = str(msg.get("role", "user")).upper()
        content = str(msg.get("content", ""))
        prompt_lines.append(f"{role}: {content}")
    prompt_lines.append("ASSISTANT:")
    prompt = "\n".join(prompt_lines)

    out = gen(
        prompt,
        max_new_tokens=MAX_NEW_TOKENS,
        do_sample=True,
        temperature=TEMPERATURE,
    )
    generated = out[0]["generated_text"]
    answer = generated.split("ASSISTANT:")[-1].strip()

    return {
        "id": "chatcmpl-hf-space",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": answer},
                "finish_reason": "stop",
            }
        ],
    }
