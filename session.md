# Claude Code Session 記錄

## Session 儲存位置

| 路徑 | 說明 |
|------|------|
| `C:\Users\User\.claude\projects\d--project-test-claude-skill\` | 系統 session 記錄（即時、最準） |
| `D:\project\test_claude_skill\Claude_Code_conversation\` | 手動複製的備份（非即時） |

路徑 slug（`d--project-test-claude-skill`）由工作目錄路徑轉換而來。

---

## Session 目錄結構

```
d--project-test-claude-skill/
├── {session-id}.jsonl         ← session 對話記錄
├── {session-id}/              ← 有附屬資料時才存在
│   ├── subagents/             ← session 中有使用 Agent 工具時
│   │   ├── agent-{id}.jsonl   ← subagent 的對話記錄
│   │   └── agent-{id}.meta.json  ← { "agentType": "Explore" }
│   └── tool-results/          ← 有大型 tool result 時
│       └── {id}.txt           ← 超過大小閾值的 tool result 內容
└── memory/                    ← Claude auto memory 目錄
    └── MEMORY.md
```

### 大型 tool result 外部儲存

當 tool result 超過大小閾值時，內容不直接寫入 JSONL，而是存為 `tool-results/{id}.txt`。

已觀察到觸發情況：
- Bash 命令讀取大型檔案（如 Claude Code JS bundle，64k+ tokens）
- session-analyze skill 分析大型 session（92KB 輸出）

---

## JSONL 記錄類型

每行一個 JSON 物件，`type` 欄位決定記錄種類：

| type | 說明 |
|------|------|
| `user` | 使用者訊息；含 `isMeta: true` 的 skill 注入；也含 tool_result（`toolUseResult` 欄位） |
| `assistant` | Claude 回應；content 可含 `text`、`tool_use`、`thinking` |
| `progress` | 背景進度事件，**不進入 LLM context**（見下方） |
| `system` | 系統事件（見下方） |
| `file-history-snapshot` | 檔案狀態快照（長 session 可出現多次） |
| `compact_boundary` | Context compaction（自動或手動）發生時的邊界記錄；含 `preTokens` 欄位（壓縮前的 token 數）；來源：官方文件 `sub-agents` |

### 同一 message 可能拆成多條記錄

同一個 assistant message 可能分為兩條記錄（第一條含 thinking，第二條含 tool_use）。解析時需以 `tool_use_id` 去重，而非 `message_id`。

---

## progress 記錄子類型

`progress` 記錄的 `data.type` 欄位：

| data.type | 說明 | 關鍵欄位 |
|-----------|------|---------|
| `hook_progress` | Hook 執行事件 | `hookName`（格式：`PostToolUse:Read`） |
| `bash_progress` | Bash 命令執行中的即時輸出 | `output`/`fullOutput`、`elapsed` |
| `agent_progress` | Subagent 每一步操作回報 | `agentId`、`message`（含 tool_use/tool_result）、`parentToolUseID` |

來源：`6370316b...jsonl`（hook/bash）、`00bbda8a...jsonl`（agent_progress）

---

## system 記錄子類型

| subtype | 說明 | 關鍵欄位 |
|---------|------|---------|
| `turn_duration` | 記錄一個 turn 的耗時 | `durationMs`、`slug` |

`slug` 是 session 的人類可讀名稱（如 `noble-wiggling-squid`），由 Claude Code 自動生成。

---

## toolUseResult 格式

`toolUseResult` 欄位有兩種格式：

```json
// 正常（dict）
"toolUseResult": { "stdout": "...", "stderr": "", "exitCode": 0 }

// 錯誤（string）
"toolUseResult": "Error: File content (86071 tokens) exceeds maximum allowed tokens (25000)..."
```

Read 工具超過 25000 token 限制時回傳純字串。

來源：`6370316b...jsonl`

---

## Token 統計欄位

assistant 記錄的 `usage` 欄位：

```json
"usage": {
  "input_tokens": 1,
  "output_tokens": 116,
  "cache_read_input_tokens": 5576,
  "cache_creation_input_tokens": 604
}
```

同一 `message_id` 可能出現在多條記錄，統計時需以 `message_id` 去重，否則會重複計算。

---

## Checkpointing

來源：官方文件 `checkpointing`（2026-03-13）

### 觸發時機與儲存

- 每次 Claude 呼叫 **file editing tools**（Edit / Write / NotebookEdit）前自動建立快照
- 每個使用者 prompt 建立一個 checkpoint
- 跨 session 持久化，預設 30 天後隨 session 清理

**重要限制**：Bash 指令造成的檔案異動（`rm`、`mv`、`cp`、重導向等）**不被追蹤**，無法透過 checkpoint 還原。Checkpoint 只能還原 Claude 的 file editing tools 所做的修改。

### Rewind 操作（Esc×2 或 `/rewind`）

開啟 prompt 歷史清單，提供五種操作：

| 操作 | 說明 |
|------|------|
| **Restore code and conversation** | 同時還原程式碼與對話 |
| **Restore conversation** | 只還原對話，保留目前程式碼 |
| **Restore code** | 只還原程式碼，保留目前對話 |
| **Summarize from here** | 壓縮指定點之後的對話，釋放 context 空間 |
| **Never mind** | 取消 |

還原後，所選 prompt 的原始內容會自動填入輸入框供重新送出或編輯。

### Summarize from here vs /compact

| | Summarize from here | /compact |
|--|---------------------|----------|
| **壓縮範圍** | 只壓縮指定點之後的對話 | 壓縮整個對話 |
| **早期 context** | 完整保留 | 全部壓縮 |
| **原始訊息** | 仍保留在 transcript，Claude 可參照 | 同上 |

### 定位

Checkpoint 是「session 層級的快速復原」，不取代 Git（Git 作為永久版本歷史）。若要在保留原 session 的情況下嘗試不同方向，應使用 **fork**（`claude --continue --fork-session`）而非 Summarize。
