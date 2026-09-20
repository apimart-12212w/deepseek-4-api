# DeepSeek 4 API (deepseek-v4-pro / deepseek-v4-flash)

<!-- conv-kit:v1 -->

<p align="center">
  <img src="assets/badges/price.svg" alt="observed unit price"> <img src="assets/badges/billing.svg" alt="billing model"> <img src="assets/badges/compat.svg" alt="OpenAI-compatible endpoint">
</p>

> **$1.03 / $3.09 per million tokens** (input / output, effective) — one OpenAI-compatible endpoint at `https://api.apimart.ai/v1`, no monthly plan required. *(observed 2026-09-17)*

**[Get an API key](https://go.apimart.ai/k-a3035b)** · **[Live pricing](https://go.apimart.ai/k-81357f)** · **[Model page](https://go.apimart.ai/k-afdde2)** · [⚡ 60-second quickstart](#quickstart)

**Why teams call DeepSeek 4 Pro (`deepseek-v4-pro`) through APIMart**

- **One key, entire catalog.** The same `https://api.apimart.ai/v1` base URL and `Authorization` header reach DeepSeek 4 Pro (`deepseek-v4-pro`) and 300+ other image, video and language models — switch the `model` field, not your client.
- **$1 minimum, pay as you go.** No subscription and no prepaid plan to size up front: top up from $1 and spend it on calls. There is no free quota to burn through first, so the price in this table is the price you pay.
- **The charge comes back in the response.** Every call reports the amount billed (`cost` / `credits_cost`), so a spend number is read per call instead of guessed at month end.
- **Drop-in OpenAI shape.** `POST /v1/chat/completions` with the same request body your client already sends; only `base_url` and `model` change.

<!-- /conv-kit:v1 -->

DeepSeek 4 on APIMart splits into `deepseek-v4-pro` and `deepseek-v4-flash`: same OpenAI-compatible chat endpoint, per-million-token pricing, and the cheapest cached-input rates in this series.

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

<!-- conv-kit:v1:scale -->
### What that costs at scale

| Spend | Cost |
| --- | --- |
| 1M input tokens | $1.03 |
| 10M input tokens | $10.30 |
| 1M input + 250K output (mixed, at the effective output rate) | see the pricing table above |

Linear at the observed per-unit rate, no volume discount assumed. Snapshot 2026-09-17; re-check the live table before committing a budget.
<!-- /conv-kit:v1:scale -->


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

<!-- conv-kit:v1:fix -->
## First-call troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `401` / `invalid api key` | key missing, truncated, or a stray newline pasted into the header | Re-copy it from the console; the header is `Authorization: Bearer $APIMART_API_KEY` |
| balance / credit error | the account has no balance | Top up from $1 in the console — there is no free quota to fall back on |
| `429` | concurrent requests on one key | Back off, then retry the same request with the same `Idempotency-Key` |
| `400` / model not found | wrong route for the id: the per-unit alias needs its `version`, the official id must not send one | Copy the exact `model` value from the route table above |
| task ends `failed` | prompt rejected by the filter, or a reference image URL expired | Re-submit with a **new** `Idempotency-Key` and re-host the reference image |
| result URL stops working | result links expire | Download the file as soon as the task reports `completed` |
<!-- /conv-kit:v1:fix -->

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

<!-- conv-kit:v1:cta -->
---

**Start with $1.** [Get an API key](https://go.apimart.ai/k-a3035b) → [check live pricing](https://go.apimart.ai/k-81357f) → [open DeepSeek 4 Pro (`deepseek-v4-pro`) in the model library](https://go.apimart.ai/k-afdde2). The first call is three steps: submit, poll `task_id`, read the charged amount off the response.
<!-- /conv-kit:v1:cta -->

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
