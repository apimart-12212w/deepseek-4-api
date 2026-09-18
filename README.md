# DeepSeek 4 API (deepseek-v4-pro / deepseek-v4-flash)

DeepSeek 4 on APIMart splits into `deepseek-v4-pro` and `deepseek-v4-flash`: same OpenAI-compatible chat endpoint, per-million-token pricing, and the cheapest cached-input rates in this series.

**Attributed entry points:** [Browse the model catalog](https://go.apimart.ai/k-afdde2) · [Current pricing](https://go.apimart.ai/k-81357f) · [Get an API key](https://go.apimart.ai/k-a3035b)

## Model ids

| Model id | Tier | Typical use |
| --- | --- | --- |
| `deepseek-v4-pro` | highest quality | hard prompts, long-form reasoning |
| `deepseek-v4-flash` | fast/cheap tier | high-volume extraction, classification, routing |

Endpoint: `POST https://api.apimart.ai/v1/chat/completions` (OpenAI-compatible). **Streaming is the default** — pass
`stream: false` when you want one JSON object back.

## Pricing (per million tokens)

<!-- pricing:token:start -->
| Token direction | List price / 1M | Effective price / 1M |
| --- | --- | --- |
| **deepseek-v4-flash** | | |
| cached_input | $0.0857 | $0.0686 |
| input | $0.4286 | $0.3429 |
| output | $1.29 | $1.03 |
| **deepseek-v4-pro** | | |
| cached_input | $0.2571 | $0.2057 |
| input | $1.29 | $1.03 |
| output | $3.86 | $3.09 |
<!-- pricing:token:end -->

The effective column is what you pay after the default group discount; [`data/model.json`](data/model.json) is refreshed
daily by CI, and the `usage` block in every response tells you exactly which tokens were billed.

## Verified capabilities

| Capability | Verified behaviour |
| --- | --- |
| Non-streaming chat | `stream: false` returns `usage` with prompt/completion token counts |
| Streaming | SSE by default; stop at `[DONE]` |
| Reasoning tokens | the response reports reasoning tokens separately in the usage details |
| Two tiers | `-pro` for quality, `-flash` for volume at roughly a third of the price |

## Quickstart

```bash
curl -sS https://api.apimart.ai/v1/chat/completions \
  -H "Authorization: Bearer $APIMART_API_KEY" -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4-pro","stream":false,"messages":[{"role":"user","content":"Name three retry rules."}]}'
```

```python
import os, requests

BASE = "https://api.apimart.ai/v1"
HEADERS = {"Authorization": f"Bearer {os.environ['APIMART_API_KEY']}", "Content-Type": "application/json"}

payload = requests.post(f"{BASE}/chat/completions", headers=HEADERS, timeout=120, json={
    "model": "deepseek-v4-pro", "stream": False,
    "messages": [{"role": "user", "content": "Name three retry rules."}],
}).json()
print(payload["choices"][0]["message"]["content"])
print(payload["usage"])
```

Streaming, tool calling and JSON mode examples are in [`examples/`](examples) (`t_curl.sh`, `python_chat.py`).

## Real call outputs

These rows are actual completions recorded from this route, with the token usage the API returned and the cost computed
from the effective rates above.

| Prompt | Response excerpt | Tokens (in/out) | Reported cost |
| --- | --- | --- | --- |
| `Explain when cached input pricing beats a lower output price, with a one-line formula.` | Cached input pricing means you pay a premium for a pre‑computed, instantly available piece of data (the cached input) instead of paying a lower price for a freshly generated result (the output). The higher price is worth… | 21 / 2793 | $0.0086 |
| `Write a 15-line Python function that routes a batch job to the cheapest model from a dict ` | ```python def route_batch(model_prices: dict[str, tuple[float, float]], input_tokens: int, output_tokens: int) -> str:     """     Routes a batch job to the cheapest model.          Args:         model_prices: dict mappi… | 41 / 1161 | $0.0036 |

Full transcripts (including longer answers) are in [`data/samples.json`](data/samples.json).

## FAQ

**What are the DeepSeek 4 model ids?**

`deepseek-v4-pro` and `deepseek-v4-flash`. Earlier generations (`deepseek-v3.2`, `deepseek-r1`) remain available on the same endpoint.

**Which tier should I use?**

Start with `deepseek-v4-flash` for high-volume extraction, classification and routing, and move a task to `deepseek-v4-pro` only when the cheaper tier's output fails your acceptance checks.

**Why is cached input so much cheaper?**

Repeated prefixes (a long system prompt, a document header) can hit the cache; the cached-input rate is roughly a fifth of fresh input, which is the main lever for a long-context workload.

**Does it support tool calling?**

The chat endpoint accepts `tools` with JSON-schema functions like the other routes in this series; verify with your own schema before relying on it.

## Related searches

- `deepseek 4 api`
- `deepseek 4 api pricing`
- `deepseek api key`
- `cheap llm api`
- `llm api pricing comparison`
- `openai compatible api`
- `cached input pricing`

## Attributed links (how this repository is measured)

| Purpose | Attributed link | Target |
| --- | --- | --- |
| Browse the model catalog | <https://go.apimart.ai/k-afdde2> | `apimart.ai/model` |
| Current pricing page | <https://go.apimart.ai/k-81357f> | `apimart.ai/pricing` |
| Get an API key | <https://go.apimart.ai/k-a3035b> | `apimart.ai/keys` |

Outbound APIMart links are minted through the promo link API; hand-made tracking parameters are rejected by
`tools/check_links.py` in CI.

## Disclosure

DeepSeek 4 is a third-party model served through APIMart; this repository publishes model ids, measured prices and
real call outputs, and does not claim official status. Model names, prices and documentation belong to their respective
owners. Endpoint reference: [https://docs.apimart.ai/en/api-reference/texts/general/chat-completions](https://docs.apimart.ai/en/api-reference/texts/general/chat-completions).

## Repository map

```text
README.md             model ids, token pricing, verified capabilities, real outputs
data/model.json       token rates for every tier (CI-refreshed)
data/samples.json     recorded completions with usage and computed cost
tools/snapshot.py     refresh pricing from the public payload
tools/check_links.py  attribution guard
examples/             curl and Python clients (streaming, tools, JSON mode)
.github/workflows/    daily price refresh + validation
```

## License

MIT — see [LICENSE](LICENSE).
