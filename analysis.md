# Claude Code 機制分析
<!-- Edit tool test OK -->

## 1. Deferred Tools（延遲載入工具）

Claude Code 的工具預設是 **deferred** 狀態，不會在對話開始時全部載入到 context。

- 好處：節省 token（工具 schema 很長，全部預載會消耗大量 context）
- 代價：使用前需先透過 ToolSearch 載入，多一個 round trip

### 完整工具清單

工具分三類：
- **系統預載（Pre-loaded）**：schema 已在 context 中，可直接呼叫，共 9 個
- **Deferred**：schema 未在 context 中，需先用 ToolSearch 載入（系統以 `<available-deferred-tools>` 標記），共 16 個
- **MCP 工具**：由外部 MCP server 提供，格式為 `mcp__{server}__{tool}`，不在 deferred 列表，視環境而定是否可用

| 工具 | 類型 | 作用 |
|------|------|------|
| **Read** | 預載 | 讀取本地檔案內容 |
| **Edit** | 預載 | 對檔案進行精確字串替換編輯 |
| **Write** | 預載 | 寫入/覆蓋整個檔案 |
| **Bash** | 預載 | 執行 shell 命令（支援 `run_in_background`，完成後以 `<task-notification>` 通知） |
| **Glob** | 預載 | 用 glob pattern 搜尋檔案路徑 |
| **Grep** | 預載 | 用 regex 搜尋檔案內容（ripgrep） |
| **Agent** | 預載 | 啟動子 agent 處理複雜任務（general-purpose / Explore / Plan 等） |
| **ToolSearch** | 預載 | 載入 deferred 工具（元工具）；可一次載入多個：`select:A,B,C` |
| **Skill** | 預載 | 執行 `.claude/skills/` 下定義的 skill |
| **AskUserQuestion** | Deferred | 主動向使用者提問 |
| **WebFetch** | Deferred | 抓取指定 URL 的網頁內容 |
| **WebSearch** | Deferred | 搜尋網路 |
| **NotebookEdit** | Deferred | 編輯 Jupyter notebook（`.ipynb` 檔案必須用此工具，Edit 會報錯） |
| **EnterPlanMode** | Deferred | 進入 Plan 模式；Write 可存計畫至 `~/.claude/plans/{slug}.md` |
| **ExitPlanMode** | Deferred | 離開 Plan 模式，提交計畫讓使用者審核 |
| **EnterWorktree** | Deferred | 在 `.claude/worktrees/{name}` 建立 git worktree 隔離環境 |
| **TaskCreate** | Deferred | 建立使用者任務（ID 為數字，如 `1`） |
| **TaskGet** | Deferred | 取得任務詳情 |
| **TaskList** | Deferred | 列出所有使用者任務 |
| **TaskUpdate** | Deferred | 更新使用者任務狀態 |
| **TaskStop** | Deferred | 停止**背景 Bash 任務**（ID 為 hash，如 `bz6rlnhqb`）；無法停止 TaskCreate 任務 |
| **TaskOutput** | Deferred | 讀取背景 Bash 任務輸出 |
| **CronCreate** | Deferred | 建立定時排程（session-only，Claude 退出後消失） |
| **CronDelete** | Deferred | 刪除排程 |
| **CronList** | Deferred | 列出所有排程 |
| **mcp__ide__getDiagnostics** | MCP | 取得 IDE 診斷資訊（lint/type 錯誤等） |
| **mcp__ide__executeCode** | MCP | 在 IDE 執行程式碼 |

來源：`b360f366...jsonl`（完整工具調用測試）

### 工具載入流程

```
Claude 需要某工具
    ↓
ToolSearch("select:ToolName")   ← 將工具 schema 載入 context
    ↓
直接呼叫 ToolName(...)
```

### 載入後的有效範圍

- 同一 session 內：載入一次後可直接呼叫，不需重複 ToolSearch
- 跨 session：每次新對話都要重新載入，context 不跨 session 保留

---

## 2. ToolSearch

用來發現並載入 deferred 工具的**元工具（工具的工具）**，是唯一預設就存在的工具。

### 兩種查詢模式

| 模式 | 範例 | 說明 |
|------|------|------|
| 直接選取 | `select:Glob` | 知道工具名稱時直接載入 |
| 關鍵字搜尋 | `"list directory"` | 不確定工具名稱時搜尋 |
| 多工具選取 | `select:Read,Edit,Grep` | 一次載入多個工具 |

### 效率問題

每次 ToolSearch 都是一個額外步驟，會：
- 多一次 LLM 推理
- 多消耗 token
- 增加回應時間

---

## 3. Skill 系統

### Skill 是什麼

放在 `.claude/skills/<name>/SKILL.md` 的 Markdown 指令檔，告訴 Claude 如何完成特定任務。

### 觸發方式

| 方式 | 觸發者 | 機制 |
|------|--------|------|
| `/skill-name` | 使用者輸入 | CLI 直接讀取 SKILL.md 展開為 `isMeta: true` 訊息注入 context |
| `Skill` tool | Claude 主動 | Claude 先 ToolSearch 載入 Skill 工具，再呼叫執行某 skill |

### 關鍵差異

使用者直接輸入 `/skill-name` 時，**CLI 在框架層面展開**，Claude 收到的已是展開後的指令內容，**不需要呼叫 Skill 工具**。

### Skill 與 ToolSearch 的關係

```
/session-analyze file.jsonl       ← 使用者輸入
    ↓
CLI 展開 SKILL.md 為 meta 訊息   ← 框架處理
    ↓
Claude 看到指令，決定要用 Bash
    ↓
ToolSearch("select:Bash")         ← 載入工具
    ↓
Bash(python3 parse-session.py ...) ← 執行
```

Skill 告訴 Claude **要做什麼**，ToolSearch 讓 Claude **有能力去做**。

### SKILL.md 前置設定（frontmatter）

```yaml
---
name: skill-name
description: 何時觸發此 skill 的說明
argument-hint: <arg1> [arg2]
allowed-tools: Bash(python3 *), Read, Glob
disable-model-invocation: true   # 可選
context: fork                    # 可選
agent: Explore                   # 可選
---
```

### 動態內容注入（`!` 前綴）

SKILL.md 中可用 `!` 前綴在展開時自動執行命令並注入結果：

```markdown
- **PR Diff**: !`gh pr diff $ARGUMENTS[0]`
```

### 腳本預處理模式

對話內容可能很長，建議在 skill 中先用腳本壓縮資料再給 LLM 分析：

```markdown
!`python3 "${CLAUDE_SKILL_DIR}/scripts/parse.py" "$ARGUMENTS"`
```

---

## 4. Session JSONL 格式

Claude Code 將每次對話儲存為 JSONL 檔，每行一個 JSON 物件。

### 記錄類型

| type | 說明 |
|------|------|
| `file-history-snapshot` | 檔案狀態快照（長 session 可出現多次，6370316b 有 65 條） |
| `user` | 使用者訊息（含 `isMeta: true` 的 skill 注入，也含 tool_result） |
| `assistant` | Claude 回應（含 tool_use、thinking、text） |
| `progress` | 背景進度事件，不進入 LLM context（見下方） |
| `system` | 系統事件，如 turn_duration（見下方） |

### progress 記錄子類型

`progress` 記錄的 `data.type` 欄位說明：

| data.type | 說明 | 關鍵欄位 |
|-----------|------|---------|
| `hook_progress` | Hook 執行事件 | `hookName`（如 `PostToolUse:Read`） |
| `bash_progress` | Bash 命令執行中輸出 | `output`/`fullOutput`、`elapsed` |

來源：`6370316b...jsonl`（含兩種 progress 類型）

### system 記錄

`system` 記錄目前已知的子類型：

| subtype | 說明 | 關鍵欄位 |
|---------|------|---------|
| `turn_duration` | 記錄一個 turn 的耗時 | `durationMs`、`slug` |

`slug` 是 session 的人類可讀名稱（例如 `noble-wiggling-squid`），由 Claude Code 自動生成。

來源：`6370316b...jsonl`

### toolUseResult 的兩種格式

`toolUseResult` 欄位通常為 dict，但在錯誤情況下（如 Read 超過 token 上限）會變成純字串：

```json
// 正常情況（dict）
"toolUseResult": { "stdout": "...", "stderr": "", "exitCode": 0 }

// 錯誤情況（string）
"toolUseResult": "Error: File content (86071 tokens) exceeds maximum allowed tokens (25000)..."
```

來源：`6370316b...jsonl`（Read 工具超過 25000 token 限制時觸發）

### 同一 message ID 可能出現在多條記錄

同一個 assistant message 可能拆成兩條記錄（例如第一條含 thinking，第二條含 tool_use），解析時需以 `tool_use_id` 去重，而非 `message_id`。

### Token 統計欄位

```json
"usage": {
  "input_tokens": 1,
  "output_tokens": 116,
  "cache_read_input_tokens": 5576,
  "cache_creation_input_tokens": 604
}
```

---

## 5. Agent Architecture

### 架構概覽

```
使用者 ←→ mainThreadAgent（主對話 Claude）
               ↓ 可 spawn
          Teammates / Subagents
```

### Agent 類型（來源：binary 分析）

| 代號 | 類型 | 說明 |
|------|------|------|
| `a` | `local_agent` | 本機子 agent，在 worktree 或隔離環境執行 |
| `b` | `local_bash` | 本機 bash 執行環境 |
| `r` | `remote_agent` | 遠端 agent（SSH 等）|
| `t` | `in_process_teammate` | 同進程內的 teammate |

```js
// binary 原始定義
nv1 = { local_bash:"b", local_agent:"a", remote_agent:"r", in_process_teammate:"t" }
```

### Agent 間通訊協議

agents 透過訊息傳遞溝通：

| 訊息類型 | 方向 | 說明 |
|---------|------|------|
| `task_assignment` | 主 → sub | 派任務 |
| `task_progress` | sub → 主 | 回報進度 |
| `task_status` | 雙向 | 狀態更新 |
| `task_notification` | sub → 主 | 任務通知 |
| `idle_notification` | sub → 主 | 閒置（含 summary、completedTaskId）|
| `agent_progress` | sub → 主 | 執行進度 |
| `permission_request` | sub → 主 | 請求操作許可 |
| `permission_response` | 主 → sub | 回覆許可 |
| `shutdown_request` | 任意 | 要求關閉 |
| `shutdown_approved/rejected` | 任意 | 關閉確認 |
| `teammate_terminated` | 系統 | teammate 結束通知 |

### Agent Memory 目錄

每個 agent 有三種範圍的獨立記憶體：

| 範圍 | 路徑 | 特性 |
|------|------|------|
| project | `.claude/agent-memory/` | 版控共享 |
| user | `~/.claude/agent-memory/` | 跨專案 |
| local | `.claude/agent-memory-local/` | 不進版控 |

### Teammate 生成模式

`teammateMode` 設定值：

| 值 | 說明 |
|----|------|
| `tmux` | 用 tmux 開新視窗執行 |
| `in-process` | 同進程內執行 |
| `auto` | 自動選擇 |

---

## 6. Hooks

Claude Code 支援在特定事件後自動執行 shell 命令（PostToolUse 等），結果會以 `progress` 記錄注入 session JSONL。

---

## 7. Tool Call 與 LLM 推理的關係

每個 tool call 結果（TOOL_RESULT）後，都會觸發一次 LLM 推理，再決定下一步動作。

```
TOOL_CALL: ToolSearch({"query": "select:Glob"})
    ↓
TOOL_RESULT: Glob 已就緒
    ↓
LLM 推理（決定下一步）         ← 一次 LLM round trip
    ↓
TOOL_CALL: Glob({"pattern": "**/*"})
    ↓
TOOL_RESULT: 檔案列表
    ↓
LLM 推理（決定下一步）         ← 又一次 LLM round trip
    ↓
...
```

ToolSearch 多一步 = 多一次 tool call + 多一次 LLM 推理。

來源：`6370316b...jsonl`，可從各 TOOL_CALL 之間的時間間隔（2~3 秒）觀察到 LLM 推理的存在。

---

## 8. Extended Thinking（THINKING 機制）

### 什麼是 THINKING

Claude 在回應前的內部推理過程，以 `thinking` 類型的 content block 記錄於 JSONL。

```json
{
  "type": "thinking",
  "thinking": "...",
  "signature": "EpYCCkYI..."
}
```

- `thinking`：推理文字內容
- `signature`：加密簽名，用於驗證 thinking 真實性，防止偽造

### 兩種狀態

| 狀態 | `thinking` 欄位 | `signature` 欄位 | 說明 |
|------|----------------|----------------|------|
| 明文 | 有內容 | 有 | 舊版 `type=enabled` 模式 |
| 加密 | 空字串 `""` | 有（且較長）| 新版 `adaptive` 模式 |

兩種狀態都有 `signature`，差別只在 `thinking` 是否為空。

來源：`5713c20a...jsonl`（明文）vs `6370316b...jsonl`（加密），透過 binary 分析確認。

### Thinking 模式（來源：binary 分析）

Claude Code 使用三種 thinkingConfig type：

| type | 說明 |
|------|------|
| `disabled` | 關閉 thinking |
| `enabled` | 舊版，已棄用，thinking 內容明文回傳 |
| `adaptive` | 新版預設，server-side 處理，thinking 加密不回傳明文 |

Beta flags：
- `interleaved-thinking-2025-05-14`（舊版）
- `adaptive-thinking-2026-01-28`（新版，目前使用）

### 設定方式

**設定鍵：`alwaysThinkingEnabled`**（存於 `settings.json`）

```json
{ "alwaysThinkingEnabled": false }
```

| 值 | 行為 |
|----|------|
| 缺席或 `true` | thinking 自動啟用（預設）|
| `false` | thinking 停用 |

也可在 Claude Code UI Settings 對話框中切換（label: `Thinking mode`）。

**相關設定：**
```json
{ "showThinkingSummaries": true }
```
控制是否在 transcript view（`ctrl+o`）顯示 thinking 摘要，預設 `false`。
