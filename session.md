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

---

## Session 啟動機制（T11）

來源：外流原始碼 2.1.88 `utils/sessionStart.ts`（232 行）、`utils/sessionState.ts`（150 行）

### Session 啟動 Hook 流程（sessionStart.ts）

`processSessionStartHooks(source, options)` 在以下時機觸發：

| `source` | 觸發時機 |
|---------|---------|
| `'startup'` | 首次啟動 |
| `'resume'` | `/resume` 恢復 session |
| `'clear'` | `/clear` 清除對話 |
| `'compact'` | `/compact` 後 |

執行流程：
1. `--bare` 模式：直接跳過所有 hook，返回空陣列
2. `shouldAllowManagedHooksOnly()` 為 true：跳過 plugin hooks（只執行 managed hooks）
3. `loadPluginHooks()`：確保 plugin hooks 已載入（memoized，重複呼叫無額外開銷）
4. `executeSessionStartHooks()`：執行 SessionStart hooks，收集 `hookMessages`, `additionalContexts`, `watchPaths`, `pendingInitialUserMessage`
5. 更新 file watchers（`updateWatchPaths()`）
6. 若有 `additionalContexts`：建立 `hook_additional_context` attachment message

**side channel `pendingInitialUserMessage`**：SessionStart hook 可回傳 `initialUserMessage`，透過 module-level 變數傳遞（避免修改函式返回類型）；由 `takeInitialUserMessage()` 消費一次。

### Session 狀態機（sessionState.ts）

```ts
type SessionState = 'idle' | 'running' | 'requires_action'
```

| 狀態 | 說明 |
|------|------|
| `'idle'` | 無進行中任務 |
| `'running'` | 模型推理或工具執行中 |
| `'requires_action'` | 等待使用者確認（如權限請求） |

**`RequiresActionDetails`**（`requires_action` 時攜帶）：
```ts
{
  tool_name: string
  action_description: string  // e.g. "Editing src/foo.ts"
  tool_use_id: string
  request_id: string
  input?: Record<string, unknown>  // frontend 可從此讀取問題選項/plan 內容
}
```

**`SessionExternalMetadata`**（同步到外部 session metadata）：
```ts
{
  permission_mode?: string | null
  is_ultraplan_mode?: boolean | null
  model?: string | null
  pending_action?: RequiresActionDetails | null
  post_turn_summary?: unknown
  task_summary?: string | null  // 長 turn 的中途進度摘要
}
```

**狀態轉換觸發**：
- `notifySessionStateChanged(state, details?)`: 更新狀態 + 通知 listener + 同步 `pending_action` 至 external_metadata（RFC 7396 null on exit）+ idle 時清除 `task_summary`
- `CLAUDE_CODE_EMIT_SESSION_STATE_EVENTS` env var：啟用後向 SDK event stream 發射 `system:session_state_changed` 事件（供 scmuxd/VS Code 等非 CCR 消費者）
- `notifyPermissionModeChanged(mode)`: Permission mode 變更的唯一通道；CCR external_metadata PUT + SDK status stream 都透過此單點

---

## 用戶輸入歷史（T13）

來源：外流原始碼 2.1.88 `history.ts`（464 行）

**注意**：`history.ts` 管理的是 **用戶輸入 prompt 的 shell-like 歷史**（up-arrow recall、ctrl+r search），**不是** conversation JSONL（那是 `sessionStorage.ts`）。

### 儲存位置

`~/.claude/history.jsonl`（跨所有 project 共用的全局文件）

### 資料結構

`LogEntry`：
```ts
{
  display: string                              // 顯示文字
  pastedContents: Record<number, StoredPastedContent>  // 貼上內容
  timestamp: number                            // Unix timestamp（用於 skip-set dedup）
  project: string                              // project root 路徑
  sessionId?: string                           // session ID
}
```

`StoredPastedContent`：
- 小內容（≤ 1024 chars）：`content` 欄位 inline 儲存
- 大內容（> 1024 chars）：計算 hash，`contentHash` 欄位參照 paste store（非同步 fire-and-forget 寫入）
- 圖片：**不儲存**（addToPromptHistory 時跳過）

### 歷史讀取

- `getHistory()`: up-arrow recall；**當前 session 優先，再其他 session**（並發 session 不交錯），最多 100 筆
- `getTimestampedHistory()`: ctrl+r picker；按 display 去重，最多 100 筆，lazy resolve paste content
- `makeHistoryReader()`: 底層 async generator，先 pending buffer 再讀磁碟（reverse order）

### 特殊行為

- `removeLastFromHistory()`: Esc interrupt 復原時撤銷最後一筆；fast path pop pending buffer，若已 flush 則加入 `skippedTimestamps` set
- `CLAUDE_CODE_SKIP_PROMPT_HISTORY` env var：跳過歷史記錄（Tungsten tool 開啟的 tmux 子 session 使用）
- `registerCleanup()`：確保 pending entries 在程序結束前 flush 到磁碟
