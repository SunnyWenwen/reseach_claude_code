#!/usr/bin/env python3
"""
parse-session.py - Pre-process Claude Code session JSONL for LLM analysis.
Usage: python3 parse-session.py <path-to-session.jsonl>
"""

import json
import os
import sys
from datetime import datetime

# Fix Windows console encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def fmt_time(ts):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%H:%M:%S")
    except Exception:
        return ts

def truncate(text, max_len=200):
    text = str(text).replace("\n", " ").strip()
    return text[:max_len] + "..." if len(text) > max_len else text

def extract_content_text(content):
    if isinstance(content, str):
        return truncate(content)
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(truncate(item.get("text", "")))
                elif item.get("type") == "tool_use":
                    parts.append(f"[tool_use: {item.get('name')}]")
                elif item.get("type") == "tool_result":
                    c = item.get("content", "")
                    if isinstance(c, list):
                        c = " ".join(str(x.get("text","")) for x in c if isinstance(x,dict))
                    parts.append(f"[tool_result: {truncate(str(c), 100)}]")
                elif item.get("type") == "thinking":
                    parts.append(f"[thinking: {truncate(item.get('thinking',''), 100)}]")
        return " | ".join(parts)
    return ""

def main():
    if len(sys.argv) < 2:
        print("Usage: parse-session.py <jsonl-file>")
        sys.exit(1)

    path = sys.argv[1]
    records = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    except FileNotFoundError:
        print(f"Error: File not found: {path}")
        sys.exit(1)

    # --- Session metadata ---
    session_id = ""
    cwd = ""
    version = ""
    model = ""
    start_time = ""
    end_time = ""

    # --- Stats ---
    total_input_tokens = 0
    total_output_tokens = 0
    total_cache_read = 0
    total_cache_creation = 0
    tool_calls = []
    errors = []
    hooks = []
    messages_summary = []
    request_count = 0

    # Track processed message IDs for token dedup (usage counted once per message ID)
    seen_usage_ids = set()
    # Track processed tool_use IDs to avoid duplicate tool call entries
    seen_tool_use_ids = set()

    for rec in records:
        rec_type = rec.get("type")
        ts = rec.get("timestamp", "")
        if not start_time and ts:
            start_time = ts
        if ts:
            end_time = ts

        if not session_id and rec.get("sessionId"):
            session_id = rec.get("sessionId", "")
            cwd = rec.get("cwd", "")
            version = rec.get("version", "")

        # User messages
        if rec_type == "user" and not rec.get("isMeta") and not rec.get("toolUseResult"):
            msg = rec.get("message", {})
            content = msg.get("content", "")
            text = extract_content_text(content)
            if text:
                messages_summary.append(f"[{fmt_time(ts)}] USER: {text}")

        # Meta messages (skill injection)
        elif rec_type == "user" and rec.get("isMeta"):
            msg = rec.get("message", {})
            content = msg.get("content", "")
            text = extract_content_text(content)
            messages_summary.append(f"[{fmt_time(ts)}] META(skill): {truncate(text, 80)}")

        # Assistant messages - process ALL records (same msg ID may appear in multiple records)
        elif rec_type == "assistant":
            msg = rec.get("message", {})
            msg_id = msg.get("id", "")

            if not model and msg.get("model"):
                model = msg.get("model", "")

            # Count tokens only once per unique message ID
            usage = msg.get("usage", {})
            if usage and msg_id and msg_id not in seen_usage_ids:
                seen_usage_ids.add(msg_id)
                request_count += 1
                total_input_tokens += usage.get("input_tokens", 0)
                total_output_tokens += usage.get("output_tokens", 0)
                total_cache_read += usage.get("cache_read_input_tokens", 0)
                total_cache_creation += usage.get("cache_creation_input_tokens", 0)

            content_list = msg.get("content", [])
            for item in content_list:
                if not isinstance(item, dict):
                    continue
                itype = item.get("type")
                if itype == "text":
                    text = truncate(item.get("text", ""))
                    if text:
                        messages_summary.append(f"[{fmt_time(ts)}] ASSISTANT: {text}")
                elif itype == "tool_use":
                    tool_id = item.get("id", "")
                    if tool_id in seen_tool_use_ids:
                        continue
                    seen_tool_use_ids.add(tool_id)
                    tool_name = item.get("name", "")
                    tool_input = truncate(json.dumps(item.get("input", {}), ensure_ascii=False), 150)
                    tool_calls.append({
                        "id": tool_id,
                        "name": tool_name,
                        "input": tool_input,
                        "time": fmt_time(ts),
                    })
                    messages_summary.append(f"[{fmt_time(ts)}] TOOL_CALL: {tool_name}({tool_input})")
                elif itype == "thinking":
                    thinking = item.get("thinking", "")
                    if thinking:
                        display = truncate(thinking, 80)
                    elif item.get("signature"):
                        display = "(encrypted)"
                    else:
                        continue
                    messages_summary.append(f"[{fmt_time(ts)}] THINKING: {display}")

        # Progress / hooks
        elif rec_type == "progress":
            data = rec.get("data", {})
            hook_name = data.get("hookName", "")
            if hook_name:
                hooks.append(f"[{fmt_time(ts)}] {hook_name}")

        # Tool results
        if rec.get("toolUseResult"):
            result = rec.get("toolUseResult", {})
            msg = rec.get("message", {})
            content = msg.get("content", [])
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "tool_result":
                        tool_id_ref = item.get("tool_use_id", "")
                        raw_content = item.get("content", "")
                        if isinstance(raw_content, list):
                            raw_content = " ".join(
                                str(x.get("text","") or x.get("tool_name",""))
                                for x in raw_content if isinstance(x, dict)
                            )
                        result_text = truncate(str(raw_content), 150)
                        is_error = bool(result.get("stderr")) or result.get("is_error", False)
                        prefix = "TOOL_ERROR" if is_error else "TOOL_RESULT"
                        messages_summary.append(f"[{fmt_time(ts)}] {prefix}[{tool_id_ref[:12]}]: {result_text}")
                        if is_error:
                            errors.append(f"{tool_id_ref[:12]}: {result_text}")

    # --- Duration ---
    duration_str = "unknown"
    try:
        t0 = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        t1 = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        secs = int((t1 - t0).total_seconds())
        duration_str = f"{secs}s"
    except Exception:
        pass

    # --- Tool call frequency ---
    tool_freq = {}
    for tc in tool_calls:
        tool_freq[tc["name"]] = tool_freq.get(tc["name"], 0) + 1

    # --- Build output lines ---
    cache_total = total_cache_read + total_cache_creation
    cache_hit_rate = total_cache_read / cache_total * 100 if cache_total > 0 else 0

    lines = []
    lines.append("=" * 60)
    lines.append("  Claude Code Session Analysis")
    lines.append("=" * 60)
    lines.append(f"Session ID : {session_id}")
    lines.append(f"Version    : {version}")
    lines.append(f"Model      : {model}")
    lines.append(f"CWD        : {cwd}")
    lines.append(f"Time Range : {fmt_time(start_time)} ~ {fmt_time(end_time)} ({duration_str})")
    lines.append(f"Requests   : {request_count}")
    lines.append("")
    lines.append("--- Token Usage ---")
    lines.append(f"  Input tokens      : {total_input_tokens:,}")
    lines.append(f"  Output tokens     : {total_output_tokens:,}")
    lines.append(f"  Cache read        : {total_cache_read:,}")
    lines.append(f"  Cache creation    : {total_cache_creation:,}")
    lines.append(f"  Cache hit rate    : {cache_hit_rate:.1f}%")
    lines.append("")
    lines.append("--- Tool Calls ---")
    if tool_freq:
        for name, count in sorted(tool_freq.items(), key=lambda x: -x[1]):
            lines.append(f"  {name:<25}: {count} times")
    else:
        lines.append("  (none)")
    lines.append("")
    if hooks:
        lines.append("--- Hooks Triggered ---")
        for h in hooks:
            lines.append(f"  {h}")
        lines.append("")
    if errors:
        lines.append("--- Errors ---")
        for e in errors:
            lines.append(f"  {e}")
        lines.append("")
    lines.append("--- Message Flow ---")
    for line in messages_summary:
        lines.append(f"  {line}")
    lines.append("")
    lines.append("=" * 60)

    output = "\n".join(lines)

    # --- Print to stdout ---
    print(output)

    # --- Save to conversation_for_human/{session_id}.txt ---
    jsonl_dir = os.path.dirname(os.path.abspath(path))
    # Walk up to find conversation_for_human dir (check jsonl_dir and its parent)
    out_dir = None
    for search_dir in [jsonl_dir, os.path.dirname(jsonl_dir)]:
        candidate = os.path.join(search_dir, "conversation_for_human")
        if os.path.isdir(candidate):
            out_dir = candidate
            break
    if out_dir is None:
        # Create it next to the JSONL file
        out_dir = os.path.join(jsonl_dir, "conversation_for_human")
        os.makedirs(out_dir, exist_ok=True)

    fname = (session_id or os.path.splitext(os.path.basename(path))[0]) + ".txt"
    out_path = os.path.join(out_dir, fname)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output + "\n")
    print(f"\n[Saved to: {out_path}]", file=sys.stderr)

if __name__ == "__main__":
    main()
