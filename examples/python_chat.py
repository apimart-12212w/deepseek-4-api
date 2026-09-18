#!/usr/bin/env python3
"""DeepSeek 4 (deepseek-v4-pro) client: non-streaming, streaming and tool calling."""

import argparse, json, os
import requests

BASE = os.environ.get("APIMART_BASE_URL", "https://api.apimart.ai/v1")
HEADERS = {"Authorization": f"Bearer {os.environ['APIMART_API_KEY']}", "Content-Type": "application/json"}


def chat(prompt: str, model: str = "deepseek-v4-pro", **extra) -> dict:
    """Non-streaming call. `stream: false` is explicit: the endpoint streams by default."""
    body = {"model": model, "stream": False, "messages": [{"role": "user", "content": prompt}], **extra}
    response = requests.post(f"{BASE}/chat/completions", headers=HEADERS, json=body, timeout=120)
    response.raise_for_status()
    return response.json()


def stream(prompt: str, model: str = "deepseek-v4-pro"):
    body = {"model": model, "stream": True, "messages": [{"role": "user", "content": prompt}]}
    with requests.post(f"{BASE}/chat/completions", headers=HEADERS, json=body, stream=True, timeout=120) as response:
        for raw in response.iter_lines():
            if not raw:
                continue
            line = raw.decode()
            if not line.startswith("data:"):
                continue
            chunk = line[5:].strip()
            if chunk == "[DONE]":
                break
            delta = json.loads(chunk)["choices"][0]["delta"].get("content")
            if delta:
                yield delta


def main() -> None:
    ap = argparse.ArgumentParser(description="DeepSeek 4 chat client")
    ap.add_argument("--prompt", default="Explain cached input pricing in one sentence.")
    ap.add_argument("--stream", action="store_true")
    args = ap.parse_args()

    if args.stream:
        for piece in stream(args.prompt):
            print(piece, end="", flush=True)
        print()
        return

    payload = chat(args.prompt)
    choice = payload["choices"][0]
    print(choice["message"]["content"][:600])
    print("usage:", payload.get("usage"))


if __name__ == "__main__":
    main()
