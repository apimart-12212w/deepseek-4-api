#!/usr/bin/env python3
"""Refresh DeepSeek 4 token pricing from the public pricing payload.

    python tools/snapshot.py                # live fetch
    python tools/snapshot.py --from-file p.html
    python tools/snapshot.py --check        # exit 1 when something moved
"""
from __future__ import annotations

import argparse, json, pathlib, re, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "model.json"
README = ROOT / "README.md"
PAGE = "https://apimart.ai/en/pricing"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36")
TARGETS = [t for t in ("deepseek-v4-pro", "deepseek-v4-flash") if t]


def fetch() -> str:
    cp = subprocess.run(["curl", "-sL", "-m", "45", "-H", f"User-Agent: {UA}", PAGE], capture_output=True, text=True)
    if not cp.stdout:
        raise SystemExit("failed to fetch the pricing page")
    return cp.stdout


def rsc_blob(html: str) -> str:
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)', html)
    return "".join(c.encode().decode("unicode_escape", errors="ignore") for c in chunks)


def records(text: str) -> dict:
    out, i = {}, 0
    while True:
        i = text.find('{"id":"', i)
        if i < 0:
            return out
        depth, j = 0, i
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        try:
            rec = json.loads(text[i:j + 1])
        except Exception:
            i = j + 1
            continue
        if rec.get("id") in TARGETS:
            out[rec["id"]] = rec
        i = j + 1


def money(v) -> str:
    if v in (None, ""):
        return "—"
    v = float(v)
    if v == 0:
        return "free"
    if v < 1:
        return f"${v:.4f}".rstrip("0").rstrip(".")
    return f"${v:,.2f}"


def rates_of(rec: dict) -> tuple[dict, dict]:
    pricing = rec.get("pricing") or {}
    return pricing.get("rates") or {}, pricing.get("effective_rates") or pricing.get("rates") or {}


def render(found: dict) -> str:
    rows = ["| Token direction | List price / 1M | Effective price / 1M |", "| --- | --- | --- |"]
    for model_id, rec in found.items():
        if len(found) > 1:
            rows.append(f"| **{model_id}** | | |")
        listed, effective = rates_of(rec)
        for key in sorted(set(listed) | set(effective)):
            rows.append(f"| {key} | {money(listed.get(key))} | {money(effective.get(key))} |")
    return "\n".join(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description="Refresh DeepSeek 4 pricing")
    ap.add_argument("--from-file")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    html = pathlib.Path(args.from_file).read_text(errors="ignore") if args.from_file else fetch()
    found = records(rsc_blob(html))
    if not found:
        raise SystemExit("no target model found in the pricing payload")

    payload = {"models": {mid: {"list": rates_of(rec)[0], "effective": rates_of(rec)[1]} for mid, rec in found.items()},
               "source": PAGE, "extracted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    new_json = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    old_json = DATA.read_text() if DATA.exists() else ""
    if args.check:
        print("changed" if new_json != old_json else "unchanged")
        sys.exit(1 if new_json != old_json else 0)

    DATA.write_text(new_json)
    readme = README.read_text()
    start, end = "<!-- pricing:token:start -->", "<!-- pricing:token:end -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pattern.search(readme):
        raise SystemExit("pricing:token markers missing in README")
    README.write_text(pattern.sub(f"{start}\n{render(found)}\n{end}", readme))
    print("pricing refreshed for", ", ".join(found))


if __name__ == "__main__":
    main()
