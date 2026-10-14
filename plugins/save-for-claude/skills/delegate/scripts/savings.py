#!/usr/bin/env python3
"""记录执行器的 token 用量，并换算成 Claude 订阅的等价额度。

用法：
  savings.py record <codex|grok> <任务名> <输出文件>
  savings.py report
"""
import glob
import json
import os
import sys
from datetime import datetime, timezone

HOME = os.path.expanduser("~/.claude/save-for-claude")
LEDGER = os.path.join(HOME, "ledger.jsonl")

# 美元 / 百万 token：输入、缓存读取、输出。缓存写入按输入价的 1.25 倍（5 分钟）或 2 倍（1 小时）计。
PRICES = {
    "claude-fable-5-1": (10.0, 0.25, 50.0),
    "claude-opus-5-5": (4.0, 0.20, 20.0),
    "claude-sonnet-5-5": (2.0, 0.20, 10.0),
    "claude-haiku-5-5": (0.10, 0.01, 0.50),
}
DEFAULT_MODEL = "claude-opus-5-5"
LABELS = {
    "claude-fable-5-1": "Claude Fable 5.1",
    "claude-opus-5-5": "Claude Opus 5.5",
    "claude-sonnet-5-5": "Claude Sonnet 5.5",
    "claude-haiku-5-5": "Claude Haiku 5.5",
}


def codex_usage(path):
    usage = {"input": 0, "cache_read": 0, "output": 0}
    for line in open(path, encoding="utf-8"):
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") != "turn.completed":
            continue
        u = event["usage"]
        usage["input"] += u["input_tokens"] - u.get("cached_input_tokens", 0)
        usage["cache_read"] += u.get("cached_input_tokens", 0)
        usage["output"] += u["output_tokens"]
    return usage


def grok_usage(path):
    u = json.load(open(path, encoding="utf-8"))["usage"]
    return {
        "input": u["input_tokens"],
        "cache_read": u.get("cache_read_input_tokens", 0),
        "output": u["output_tokens"],
    }


def record(executor, task, path):
    usage = {"codex": codex_usage, "grok": grok_usage}[executor](path)
    os.makedirs(HOME, exist_ok=True)
    entry = {
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session": os.environ.get("CLAUDE_CODE_SESSION_ID"),
        "executor": executor,
        "task": task,
        **usage,
    }
    with open(LEDGER, "a", encoding="utf-8") as ledger:
        ledger.write(json.dumps(entry, ensure_ascii=False) + "\n")
    total = sum(usage.values())
    print(f"已记录 {executor} · {task}：{total:,} token")


def claude_usage(session):
    """读取 Claude Code 会话记录，返回所用模型和按模型价格折算的美元成本。"""
    paths = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{session}.jsonl"))
    if not paths:
        return DEFAULT_MODEL, None
    messages, model = {}, DEFAULT_MODEL
    for line in open(paths[0], encoding="utf-8"):
        try:
            event = json.loads(line)
        except ValueError:
            continue
        message = event.get("message") or {}
        if event.get("type") == "assistant" and message.get("usage") and message.get("id"):
            messages[message["id"]] = message["usage"]
            if message.get("model") in PRICES:
                model = message["model"]
    price_in, price_cache, price_out = PRICES[model]
    cost = 0.0
    for u in messages.values():
        creation = u.get("cache_creation") or {}
        write_5m = creation.get("ephemeral_5m_input_tokens", 0)
        write_1h = creation.get("ephemeral_1h_input_tokens", 0)
        if not creation:
            write_5m = u.get("cache_creation_input_tokens", 0)
        cost += (
            u.get("input_tokens", 0) * price_in
            + u.get("cache_read_input_tokens", 0) * price_cache
            + write_5m * price_in * 1.25
            + write_1h * price_in * 2
            + u.get("output_tokens", 0) * price_out
        ) / 1e6
    return model, cost


def equivalent(entries, model):
    price_in, price_cache, price_out = PRICES[model]
    return sum(
        (e["input"] * price_in + e["cache_read"] * price_cache + e["output"] * price_out) / 1e6
        for e in entries
    )


def report():
    entries = []
    if os.path.exists(LEDGER):
        entries = [json.loads(line) for line in open(LEDGER, encoding="utf-8") if line.strip()]
    session = os.environ.get("CLAUDE_CODE_SESSION_ID")
    current = [e for e in entries if e["session"] == session]
    model, claude_cost = claude_usage(session) if session else (DEFAULT_MODEL, None)
    label = LABELS[model]

    if not current:
        print("本会话还没有派单记录。")
    else:
        counts = {}
        for e in current:
            counts[e["executor"]] = counts.get(e["executor"], 0) + 1
        runs = "、".join(f"{name} {n} 次" for name, n in counts.items())
        tokens = sum(e["input"] + e["cache_read"] + e["output"] for e in current)
        saved = equivalent(current, model)
        print(f"本会话派单：{runs}，执行器共消耗 {tokens:,} token")
        print(f"折合 {label}：约 ${saved:.2f}")
        if claude_cost:
            share = saved / (saved + claude_cost)
            print(f"本会话 Claude 自身消耗：约 ${claude_cost:.2f}")
            print(f"若全部由 Claude 完成约 ${saved + claude_cost:.2f}，派单省下约 {share:.0%} 的额度")

    if entries:
        print(f"累计已省：约 ${equivalent(entries, model):.2f}（{len(entries)} 次派单，按 {label} 折算）")


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "record":
        record(sys.argv[2], sys.argv[3], sys.argv[4])
    elif len(sys.argv) == 2 and sys.argv[1] == "report":
        report()
    else:
        sys.exit(__doc__)
