#!/usr/bin/env python3
"""subject-domain-test: run one dilemma under three framings.

用法 / Usage:
  python run.py --dry-run
  python run.py --base-url https://api.example.com/v1 --model your-model --out results/your-model.json

只用标准库。任意 OpenAI 兼容接口（/chat/completions）都能跑。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))


def load_dilemmas(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_prompt(item: dict, framing: str, instructions: str) -> str:
    return (
        f"{instructions}\n\n"
        f"情形：{item['situation']}\n\n"
        f"A：{item['options']['A']}\n"
        f"B：{item['options']['B']}\n\n"
        f"{framing}"
    )


def parse_side(text: str) -> str:
    """First line should be A or B. Fall back to the first standalone A/B token."""
    first = (text or "").strip().splitlines()[0] if (text or "").strip() else ""
    m = re.match(r"^[^A-Za-z]*([AB])\b", first)
    if m:
        return m.group(1)
    m = re.search(r"\b([AB])\b", text or "")
    return m.group(1) if m else "?"


def chat(base_url: str, api_key: str, model: str, prompt: str,
         temperature: float, timeout: int = 60) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dilemmas", default=os.path.join(HERE, "dilemmas.json"))
    ap.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    ap.add_argument("--model", default=os.environ.get("MODEL", ""))
    ap.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", ""))
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--out", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default="", help="逗号分隔的题目 id，例如 d01,d13")
    args = ap.parse_args()

    data = load_dilemmas(args.dilemmas)
    instructions = data["instructions"]
    framings = data["framings"]
    only = [x.strip() for x in args.only.split(",") if x.strip()]
    items = [it for it in data["items"] if not only or it["id"] in only]

    if args.dry_run:
        for it in items:
            print("=" * 60)
            print(f"{it['id']}  {it['title']}  [{it['kind']}]")
            for key in ("neutral", "majority", "individual"):
                print(f"--- {key} ---")
                print(build_prompt(it, framings[key], instructions))
        print(f"\n共 {len(items)} 道题 × 3 个框架 = {len(items) * 3} 次调用。")
        return 0

    if not args.model:
        print("缺少 --model", file=sys.stderr)
        return 2
    if not args.api_key:
        print("缺少 --api-key 或环境变量 OPENAI_API_KEY", file=sys.stderr)
        return 2

    out_path = args.out or os.path.join(
        HERE, "results", f"{re.sub(r'[^A-Za-z0-9._-]', '_', args.model)}.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    result = {
        "model": args.model,
        "base_url": args.base_url,
        "temperature": args.temperature,
        "started_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "instructions": instructions,
        "items": [],
    }

    for it in items:
        entry = {"id": it["id"], "kind": it["kind"], "title": it["title"], "answers": {}, "side": {}}
        for key in ("neutral", "majority", "individual"):
            prompt = build_prompt(it, framings[key], instructions)
            last_err = None
            for attempt in range(2):
                try:
                    text = chat(args.base_url, args.api_key, args.model, prompt, args.temperature)
                    break
                except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, KeyError) as e:
                    last_err = e
                    time.sleep(2 * (attempt + 1))
            else:
                text = f"[error] {last_err}"
            entry["answers"][key] = text
            entry["side"][key] = parse_side(text)
            time.sleep(0.5)
        entry["judgement"] = None
        result["items"].append(entry)
        print(f"{it['id']} {it['title']}: " +
              " ".join(f"{k}={v}" for k, v in entry["side"].items()))

    result["finished_at"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n写入 {out_path}")
    print("下一步：按 judge.md 逐题填 judgement（consistent / shifted / flipped / by-design / excluded）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
