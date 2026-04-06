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

## JSONL 寫入機制（`sessionStorage.ts`）

來源：外流原始碼 2.1.88 `utils/sessionStorage.ts`

### Session 檔案的建立時機（Lazy Materialization）

**JSONL 檔案不在 session 開始時立即建立**，而是在第一個 `user` 或 `assistant` 訊息出現時才建立（`materializeSessionFile()`）。

```
session 開始
    ↓
hook progress / attachment 訊息 → 暫存進 pendingEntries（buffer）
    ↓
第一個 user 或 assistant 訊息
    → 建立 {session-id}.jsonl
    → 寫入 pendingEntries（flush buffer）
    → 後續訊息直接 append
```

這個設計**防止只有 metadata 的空 session 檔案**出現。

### TranscriptMessage 額外欄位（寫入時自動附加）

每條 transcript record（user/assistant/attachment/system）在寫入 JSONL 時，`insertMessageChain()` 會附加以下 session-stamp 欄位：

| 欄位 | 說明 |
|------|------|
| `parentUuid` | 鏈中的前一條 transcript 訊息 UUID；compact_boundary 為 null |
| `logicalParentUuid` | compact_boundary 時記錄邏輯父節點（供 --continue 使用） |
| `isSidechain` | true 表示 subagent 的 sidechain 訊息 |
| `agentId` | subagent ID（subagent 的記錄才有） |
| `teamName` / `agentName` | 多 agent 情境 |
| `promptId` | user 訊息才有，記錄該 prompt 的 ID |
| `userType` | 使用者類型（e.g. `external`、`ant`） |
| `entrypoint` | 進入方式（cli / web / vscode 等） |
| `cwd` | 當下工作目錄 |
| `sessionId` | session UUID |
| `version` | Claude Code 版本號 |
| `gitBranch` | 當下 git branch |
| `slug` | session 的人類可讀名稱（如 `noble-wiggling-squid`） |

### Progress 記錄：不進入 JSONL（PR #24099 後）

**重要修正**（來源：sessionStorage.ts 原始碼注釋 lines 133–138）：

> "Progress messages are NOT transcript messages. They are ephemeral UI state and must not be persisted to the JSONL or participate in the parentUuid chain. Including them caused chain forks that orphaned real conversation messages on resume (see #14373, #23537)."

| 版本 | progress 記錄行為 |
|------|------|
| PR #24099 以前 | 寫入 JSONL，有 uuid + parentUuid |
| PR #24099 以後 | **不寫入 JSONL**，純 UI 暫態（`LegacyProgressEntry` 是 type guard，用於讀取舊記錄） |

現有 JSONL 中的 progress 記錄（如 `bash_progress`、`agent_progress`）是**舊 session 的遺留**，新 session 不再寫入。

### 完整 JSONL Entry 類型清單

來源：sessionStorage.ts `appendEntry()` switch（lines 1157–1264）

#### Transcript 訊息（進入 parentUuid chain）

| type | 說明 |
|------|------|
| `user` | 使用者輸入；含 tool_result（`toolUseResult` 欄位） |
| `assistant` | Claude 回應；含 text/tool_use/thinking |
| `attachment` | 附件訊息（file 等） |
| `system` | 系統訊息（session 初始化事件等） |

#### Metadata 記錄（session 層級，不進 chain）

| type | 說明 |
|------|------|
| `summary` | 壓縮摘要 |
| `custom-title` | 使用者自訂 session 標題 |
| `ai-title` | AI 自動生成標題 |
| `last-prompt` | 最近一次使用者輸入（供 --resume picker 顯示） |
| `task-summary` | 任務摘要 |
| `tag` | Session 標籤 |
| `agent-name` | agent 名稱 |
| `agent-color` | agent 顏色 |
| `agent-setting` | agent 設定 |
| `pr-link` | PR 連結（Create PR 後寫入）|
| `mode` | coordinator/normal 模式 |
| `worktree-state` | worktree 狀態 |

#### 其他記錄

| type | 說明 |
|------|------|
| `file-history-snapshot` | 檔案狀態快照（checkpointing） |
| `attribution-snapshot` | Attribution 快照 |
| `content-replacement` | 大型 tool result 外部儲存的替換記錄 |
| `marble-origami-commit` | Context collapse commit（新壓縮機制） |
| `marble-origami-snapshot` | Context collapse snapshot |
| `queue-operation` | 任務隊列操作 |
| `speculation-accept` | 投機執行接受記錄 |
| `compact_boundary` | Context compaction 邊界（`SystemCompactBoundaryMessage`，parentUuid=null） |

### Token Usage 的儲存位置

token usage **不是獨立記錄**，而是直接嵌在 `assistant` 記錄的 `message.usage` 欄位中，數值來自 Anthropic API 回傳：

```json
{
  "type": "assistant",
  "message": {
    "usage": {
      "input_tokens": 1,
      "output_tokens": 116,
      "cache_read_input_tokens": 5576,
      "cache_creation_input_tokens": 604
    }
  }
}
```

**注意**：compact 後，被保留的 assistant 訊息的 usage 會被歸零（`input_tokens: 0` 等），避免 resume 時誤判已壓縮的 context 大小導致立即再次觸發自動壓縮。

### Subagent Sidechain 的儲存路徑

subagent 訊息寫入獨立檔案，**不進主 session 的 JSONL**：

```
{session-id}/subagents/agent-{agentId}.jsonl
```

UUID dedup 跳過 sidechain 記錄：若 sidechain 訊息的 UUID 加入了主 session 的 messageSet，main thread 後續訊息的 parentUuid chain 會斷裂（dangling ref）。

---

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
