#!/usr/bin/env bash
# DeepSeek 4 (deepseek-v4-pro): non-streaming, streaming and tool-calling request shapes.
set -euo pipefail
: "${APIMART_API_KEY:?export APIMART_API_KEY first}"
BASE="${APIMART_BASE_URL:-https://api.apimart.ai/v1}"
AUTH=(-H "Authorization: Bearer $APIMART_API_KEY" -H 'Content-Type: application/json')

echo "== non-streaming (explicit stream:false) =="
curl -sS "$BASE/chat/completions" "${AUTH[@]}" \
  -d '{"model":"deepseek-v4-pro","stream":false,"messages":[{"role":"user","content":"Name three retry rules, one per line."}]}' \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["choices"][0]["message"]["content"][:300]); print("usage:", d.get("usage",{}).get("total_tokens"))'

echo
echo "== streaming (default mode: iterate SSE lines) =="
curl -sS "$BASE/chat/completions" "${AUTH[@]}" \
  -d '{"model":"deepseek-v4-pro","stream":true,"messages":[{"role":"user","content":"Count to five."}]}' \
  | head -c 400; echo

echo
echo "== tool calling =="
curl -sS "$BASE/chat/completions" "${AUTH[@]}" \
  -d '{"model":"deepseek-v4-pro","stream":false,"messages":[{"role":"user","content":"What is the weather in Paris? Use the tool."}],
       "tools":[{"type":"function","function":{"name":"get_weather","description":"Get weather","parameters":{"type":"object","properties":{"city":{"type":"string"}},"required":["city"]}}}]}' \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); c=d["choices"][0]; print("finish:", c["finish_reason"]); print("tool_calls:", json.dumps(c["message"].get("tool_calls"))[:200])'
