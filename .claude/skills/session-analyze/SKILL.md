---
name: session-analyze
description: Analyze a Claude Code conversation session JSONL file. Extracts message flow, tool calls, token usage, and errors. Use when the user wants to inspect, debug, or understand a Claude Code session log.
argument-hint: <path-to-session.jsonl>
allowed-tools: Bash(python3 *)
---

# Session Analyze: $ARGUMENTS

## 預處理結果（程式自動解析）

!`python3 "${CLAUDE_SKILL_DIR}/scripts/parse-session.py" "$ARGUMENTS"`

---

## 分析任務

根據上方預處理結果，進行以下分析：

### 1. 對話摘要
簡述這個 session 做了什麼事，使用者的目標是什麼，Claude 如何完成任務。

### 2. 效率分析
- Token 使用是否合理？Cache 命中率如何？
- 工具呼叫次數與順序是否有冗餘（例如多餘的 ToolSearch）？
- 整體耗時是否正常？

### 3. 問題與異常
- 是否有錯誤發生？
- 有無值得注意的行為（例如重複呼叫、不必要的步驟）？

### 4. 改善建議
針對觀察到的問題，提供具體的改善方向。

---

輸出格式：
```
## Session 分析報告

### 對話摘要
...

### 效率分析
- Token: ...
- Cache 命中率: ...
- 工具呼叫: ...

### 問題與異常
- ...

### 改善建議
- ...
```
