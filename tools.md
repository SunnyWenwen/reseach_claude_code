# Claude Code 工具系統

## Agentic Loop

Claude Code 的工具執行架構基於 Anthropic API 標準 agentic loop：

```mermaid
sequenceDiagram
    participant U as 使用者
    participant C as Claude (LLM)
    participant T as 工具執行層

    U->>C: 輸入訊息
    loop Agentic Loop
        C->>T: tool_use（可批次多個）
        T->>C: tool_result（全部回來才繼續）
        C->>C: LLM 推理
    end
    C->>U: 最終回應
```

### 單次推理的回應結構

一次 LLM 推理可在同一個 `content` 陣列中同時包含 `text` 和 `tool_use`，順序固定：

```json
{
  "content": [
    { "type": "thinking", "signature": "..." },
    { "type": "text", "text": "說明文字..." },
    { "type": "tool_use", "name": "Edit", "input": {...} },
    { "type": "tool_use", "name": "Edit", "input": {...} }
  ]
}
```

所以並非「text **或** tool_use」，而是**一次推理可同時產生 text + 多個 tool_use**。

### 批次 tool call（一次推理可執行多個工具）

```mermaid
sequenceDiagram
    participant C as Claude
    participant T as 工具執行層

    C->>T: Read(fileA)
    C->>T: Read(fileB)
    Note over T: 同一批次，平行執行
    T->>C: fileA 內容
    T->>C: fileB 內容
    Note over C: 一次 LLM 推理處理兩個結果
```

### Loop 終止條件

LLM 推理產生的回應**不含 `tool_use`** 時，loop 結束，控制權回到使用者：

```mermaid
flowchart TD
    A[LLM 推理] --> B{回應含 tool_use?}
    B -- 是 --> C[執行工具]
    C --> D[收集 tool_result]
    D --> A
    B -- 否 --> E[回傳給使用者，停止]
```

### 例外情況

| 情況 | 說明 |
|------|------|
| **批次 tool call** | 多個 tool_use 同批發出 → 全部結果一起回來 → 一次推理 |
| **`disable-model-invocation: true`** | Skill 可設定跳過 LLM 推理，直接執行 |
| **背景 Bash（`run_in_background`）** | 不阻塞，inference 繼續；結果以 `<task-notification>` 非同步通知 |
| **Subagent** | 有自己獨立的 agentic loop，不佔主 agent 的推理次數 |

來源：`6370316b...jsonl`，各 TOOL_CALL 之間的時間間隔（2~3 秒）可觀察到 LLM 推理。

---

## 工具分類

工具分三類：

| 類型 | 說明 | 數量 |
|------|------|------|
| **Pre-loaded（系統預載）** | schema 已在 context，可直接呼叫 | 9 個 |
| **Deferred（延遲載入）** | schema 未載入，需先 ToolSearch；系統以 `<available-deferred-tools>` 標記 | 16 個 |
| **MCP** | 由外部 MCP server 提供（`mcp__{server}__{tool}`）；server 連線時預載，未連線時不存在 | 視設定 |

延遲載入的好處：節省 token（工具 schema 很長）；代價：多一次 ToolSearch round trip。

---

## 完整工具清單

**權限說明：**
- **自動允許**：預設直接執行，不詢問
- ⚠️ **預設詢問**：可透過 `permissions.allow` 設定關閉（詳見 [permissions.md](permissions.md)）

| 工具 | 類型 | 權限 | 作用 |
|------|------|------|------|
| **Read** | 預載 | 自動允許 | 讀取本地檔案內容；支援圖片（base64）、`.ipynb`（解析 cells）、PDF（`pages` 參數，最多 20 頁/次）；25,000 token 上限（超過回 error string，不截斷）；支援 `offset`/`limit` 分段讀取 |
| **Glob** | 預載 | 自動允許 | 用 glob pattern 搜尋檔案路徑 |
| **Grep** | 預載 | 自動允許 | 用 regex 搜尋檔案內容（ripgrep） |
| **ToolSearch** | 預載 | 自動允許 | 載入 deferred 工具（見下方） |
| **TaskGet** | Deferred | 自動允許 | 取得任務詳情 |
| **TaskList** | Deferred | 自動允許 | 列出所有使用者任務 |
| **TaskOutput** | Deferred | 自動允許 | 讀取背景 Bash 任務輸出 |
| **CronList** | Deferred | 自動允許 | 列出所有排程 |
| **Edit** | 預載 | ⚠️ 可設定 | 精確字串替換（old_string → new_string）；old_string 必須唯一，否則報錯；支援 `replace_all`；只傳 diff，token 消耗少；設定：`Edit` |
| **Write** | 預載 | ⚠️ 可設定 | 覆寫整個檔案內容；適合新建檔或完整改寫；token 消耗多；設定：`Write` |
| **Bash** | 預載 | ⚠️ 可設定 | 執行 shell 命令；支援 `run_in_background`（完成後以 `<task-notification>` 通知）；設定：`Bash(command:*)` |
| **Agent** | 預載 | ⚠️ 可設定 | 啟動子 agent（見下方）；設定：`Agent` |
| **Skill** | 預載 | ⚠️ 可設定 | 執行 skill（見下方）；設定：`Skill(skill-name)` |
| **AskUserQuestion** | Deferred | ⚠️ 可設定 | 主動向使用者提問；設定：`AskUserQuestion` |
| **WebFetch** | Deferred | ⚠️ 可設定 | 抓取 URL 內容；設定：`WebFetch(domain:example.com)` |
| **WebSearch** | Deferred | ⚠️ 可設定 | 搜尋網路；設定：`WebSearch` |
| **NotebookEdit** | Deferred | ⚠️ 可設定 | 編輯 Jupyter notebook（`.ipynb` 必須用此工具，Edit 會報錯）；設定：`NotebookEdit` |
| **EnterPlanMode** | Deferred | ⚠️ 可設定 | 進入 Plan 模式；計畫存至 `~/.claude/plans/{slug}.md` |
| **ExitPlanMode** | Deferred | ⚠️ 可設定 | 離開 Plan 模式，提交計畫給使用者審核 |
| **EnterWorktree** | Deferred | ⚠️ 可設定 | 在 `.claude/worktrees/{name}` 建立 git worktree 隔離環境 |
| **TaskCreate** | Deferred | ⚠️ 可設定 | 建立任務（ID 為數字，如 `1`）；設定：`TaskCreate` |
| **TaskUpdate** | Deferred | ⚠️ 可設定 | 更新任務狀態；設定：`TaskUpdate` |
| **TaskStop** | Deferred | ⚠️ 可設定 | 停止**背景 Bash 任務**（ID 為 hash，如 `bz6rlnhqb`）；無法停止 TaskCreate 任務；設定：`TaskStop` |
| **CronCreate** | Deferred | ⚠️ 可設定 | 建立定時排程（session-only，Claude 退出後消失）；設定：`CronCreate` |
| **CronDelete** | Deferred | ⚠️ 可設定 | 刪除排程；設定：`CronDelete` |
| **mcp__ide__getDiagnostics** | MCP | ⚠️ 可設定 | 取得 IDE 診斷資訊（lint/type 錯誤）；設定：`mcp__ide__getDiagnostics` |
| **mcp__ide__executeCode** | MCP | ⚠️ 可設定 | 在 IDE 執行程式碼；設定：`mcp__ide__executeCode` |

來源：`b360f366...jsonl`（完整工具調用測試）

---

## 工具分類（依功能）

除了 Pre-loaded/Deferred/MCP 分類，工具也可依**操作性質**分類：

| 類型 | 工具 | 說明 |
|------|------|------|
| **唯讀** | Read, Glob, Grep, WebFetch, WebSearch, TaskGet, TaskList, TaskOutput, CronList, mcp__ide__getDiagnostics | 不修改任何狀態 |
| **寫入** | Edit, Write, NotebookEdit | 修改本地檔案 |
| **執行** | Bash | 執行任意 shell 命令 |
| **規劃/隔離** | EnterPlanMode, ExitPlanMode, EnterWorktree, ExitWorktree | 切換操作模式或環境 |
| **任務管理** | TaskCreate, TaskUpdate, TaskStop, CronCreate, CronDelete | 管理背景任務與排程 |
| **互動/meta** | AskUserQuestion, ToolSearch, Skill, Agent | 和使用者/其他工具互動 |
| **IDE** | mcp__ide__getDiagnostics, mcp__ide__executeCode | VS Code/JetBrains 整合 |

來源：binary `2.1.72`，`filePatternTools: ["Read","Write","Edit","Glob","NotebookRead","NotebookEdit"]`（使用不同的匹配邏輯）

---

## 為何有 Read/Write 而不直接用 Bash

Read/Write 不是 Bash 的語法糖，兩者在架構上有本質差異：

| 面向 | Read/Write/Edit | Bash |
|------|-----------------|------|
| **權限粒度** | 預設 Read 自動允許；Write/Edit 分開設定 | 全部走 prefix/exact/wildcard 規則 |
| **匹配邏輯** | `filePatternTools`（路徑型規則） | `bashPrefixTools`（命令型規則） |
| **Token 限制** | Read 上限 25,000 tokens（超過回 error string） | 無強制限制 |
| **Diff 計算** | Write/Edit 自動計算 structuredPatch + gitDiff 顯示給使用者 | 無 |
| **寫入範圍** | 限制在工作目錄 + 子目錄（框架層強制） | 不限制 |
| **特殊格式** | 圖片（base64 視覺理解）、`.ipynb`（解析 cells+outputs）、PDF（頁數分段） | 只有 raw bytes/text |
| **預設權限** | Read 自動允許；Write 需確認 | 全部需確認 |

Read/Write 讓 Claude Code 有「唯讀瀏覽」vs「寫入」的清晰權限界線，而不必所有檔案操作都要走 Bash confirm。

### Write vs Edit

| | Write | Edit |
|--|-------|------|
| **操作方式** | 覆寫整個檔案 | 精確字串替換（old_string → new_string） |
| **適用情境** | 新建檔、完整改寫 | 修改現有檔案的一部分 |
| **唯一性限制** | 無 | old_string 必須在檔案中唯一，否則報錯 |
| **replace_all** | 無 | 有，可替換所有匹配 |
| **token 消耗** | 傳送整個檔案內容（多） | 只傳 diff（少） |
| **diff 顯示** | 有 structuredPatch + gitDiff | 有 |

Edit 是日常主力；Write 用於「整個檔案都要換」或「新建檔案」的情境。

來源：binary `FileReadTool`、`FileWriteTool`；官方安全文件

---

## 工具與 LLM 的關係

大多數工具本身不呼叫 LLM，純粹執行操作：

| 工具 | 是否使用 LLM | 說明 |
|------|------------|------|
| Bash, Read, Write, Edit, Glob, Grep | ✗ | 純執行，無 LLM |
| WebFetch, WebSearch | ✗ | 網路請求，結果直接回傳給主 LLM |
| ToolSearch | ✗ | schema 查找，無 LLM |
| AskUserQuestion | ✗ | 向使用者請求輸入，無 LLM |
| **Agent** | ✓ | 啟動獨立 LLM（可能不同 model，如 Haiku） |
| **Skill** | 視設定 | 預設注入 context 後讓主 LLM 處理；`disable-model-invocation: true` 跳過 LLM |
| **`prompt` 型 Hooks** | ✓ | 用指定 model 評估（預設用輕量快速 model） |

來源：binary `disableModelInvocation`；`disable-model-invocation` frontmatter；Agent 實測（Haiku vs Sonnet）

---

## Skill 的執行機制（上下文注入 vs 邏輯）

Skill 是**上下文注入為主、腳本預處理為輔**的混合模式：

### 執行模式對比

| 模式 | 條件 | 說明 |
|------|------|------|
| **注入模式**（預設） | 無 `disable-model-invocation` | SKILL.md 內容注入為 `isMeta: true` 訊息，主 LLM 負責決策 |
| **腳本模式** | `disable-model-invocation: true` | `!`-prefixed 命令執行後注入，**不呼叫 LLM**（純腳本） |
| **Agent 模式** | frontmatter 含 `agent` 欄位 | skill 路由到指定 subagent_type 執行 |
| **Fork 模式** | `context: fork` | 建立獨立 fork context（不共享主 session 歷史） |

### `!` 前綴命令的作用

SKILL.md 中的 `!` 命令在**注入前**執行，輸出替換原本行：

```markdown
## 預處理輸出
!`python3 "${CLAUDE_SKILL_DIR}/scripts/parse.py" "$ARGUMENTS"`
```

→ CLI 展開時執行 python 腳本，將輸出插入 context，LLM 才看到已壓縮的資料。

這讓 Skill 既能靠 LLM 做決策，也能用腳本做大量資料預處理（避免 LLM 直接處理 raw JSONL）。

來源：binary `CLAUDE_SKILL_DIR`、`disable-model-invocation`、`context: fork`

---

## Skill `allowed-tools` vs Agent 的工具權限

| | Skill `allowed-tools` | Agent `tools` 參數 |
|--|----------------------|-------------------|
| **執行環境** | 主 session（同 context） | 獨立 subagent（獨立 context） |
| **隔離程度** | 限制但共享主 session 狀態 | 完全隔離 |
| **設定位置** | SKILL.md frontmatter | Agent tool 呼叫參數 / `--agents` CLI flag |
| **繼承** | 若未設定，預設繼承主 session 所有工具 | 若未設定，預設繼承全部工具 |
| **作用** | skill 執行期間 Claude 只能用這些工具 | subagent 整個生命週期只有這些工具 |

**為何 Skill 需要 allowed-tools？**

Skill 在主 session 執行，主 Claude 有全部工具。若不限制，skill 執行中 Claude 可能用到 skill 設計者不預期的工具。`allowed-tools` 讓 skill 成為**有邊界的操作集**，例如 session-analyze 只允許 Bash + Read，確保它不會意外呼叫 Agent 或 Write。

來源：binary `allowed-tools`、`allowedTools` frontmatter 解析

---

## ToolSearch

**元工具（工具的工具）**，唯一預設就存在的 deferred 工具載入器。

### 查詢模式

| 模式 | 範例 | 說明 |
|------|------|------|
| 直接選取 | `select:Glob` | 知道工具名稱時直接載入 |
| 多工具選取 | `select:Read,Edit,Grep` | 一次載入多個 |
| 關鍵字搜尋 | `"list directory"` | 不確定工具名稱時搜尋 |

### 工具載入流程

```
Claude 需要某工具
    ↓
ToolSearch("select:ToolName")   ← 將工具 schema 載入 context
    ↓
直接呼叫 ToolName(...)
```

### 有效範圍

- **同一 session**：載入一次後可直接呼叫，不需重複 ToolSearch
- **跨 session**：每次新對話都要重新載入，context 不跨 session 保留

### 效率影響

每次 ToolSearch = 多一次 tool call + 多一次 LLM 推理（約 2~3 秒）。預載工具省去此步驟。

---

## Skill 系統

### Skill 是什麼

放在 `.claude/skills/<name>/SKILL.md` 的 Markdown 指令檔，告訴 Claude 如何完成特定任務。

### 觸發方式

| 方式 | 觸發者 | 機制 |
|------|--------|------|
| `/skill-name` | 使用者輸入 | CLI 在框架層讀取 SKILL.md，展開為 `isMeta: true` 訊息注入 context；Claude 不需呼叫 Skill 工具 |
| `Skill` tool | Claude 主動 | Claude 先 ToolSearch 載入 Skill 工具，再呼叫執行 |

### 執行流程（以 `/session-analyze` 為例）

```
/session-analyze file.jsonl       ← 使用者輸入
    ↓
CLI 展開 SKILL.md 為 meta 訊息   ← 框架處理（不進 LLM）
    ↓
Claude 看到指令，決定要用 Bash
    ↓
Bash(python3 parse-session.py ...) ← 執行
```

### SKILL.md frontmatter

```yaml
---
name: skill-name
description: 何時觸發此 skill 的說明
argument-hint: <arg1> [arg2]
allowed-tools: Bash(python3 *), Read, Glob
disable-model-invocation: true   # 可選：停用 LLM 呼叫
context: fork                    # 可選
agent: Explore                   # 可選：指定執行的 agent 類型
---
```

### 動態內容注入（`!` 前綴）

SKILL.md 中可用 `!` 前綴在展開時執行命令並注入結果：

```markdown
- **PR Diff**: !`gh pr diff $ARGUMENTS[0]`
```

### 腳本預處理模式

對話內容可能很長，建議先用腳本壓縮再給 LLM 分析：

```markdown
!`python3 "${CLAUDE_SKILL_DIR}/scripts/parse.py" "$ARGUMENTS"`
```

---

## Agent 工具

### subagent_type 選項（共 5 種）

| subagent_type | 可用工具 | 說明 |
|---------------|----------|------|
| `general-purpose` | 全部（`*`） | 通用型，適合複雜多步驟任務 |
| `statusline-setup` | Read、Edit | 專門設定 Claude Code 狀態列 |
| `Explore` | 除 Agent、ExitPlanMode、Edit、Write、NotebookEdit | 快速探索 codebase；支援 quick / medium / very thorough 三種深度 |
| `Plan` | 除 Agent、ExitPlanMode、Edit、Write、NotebookEdit | 軟體架構規劃，回傳實作計畫 |
| `claude-code-guide` | Glob、Grep、Read、WebFetch、WebSearch | 回答 Claude Code / SDK / API 問題；支援 `resume` 繼續前次 agent |

### Subagent 特性

| 特性 | 說明 |
|------|------|
| **獨立 context** | 每個 subagent 有自己的 context window，不共享主 agent 對話歷史 |
| **工具隔離** | 每種 subagent_type 有各自的工具白名單 |
| **agentId** | 呼叫後回傳 agentId（如 `aabcf4bda0b27ca01`，`a` 前綴 = `local_agent`），可用 `resume` 參數繼續 |
| **結果回傳** | 完成後以 TOOL_RESULT 回傳（含 `totalDurationMs`、`totalTokens`、`totalToolUseCount`） |
| **不同 model** | Subagent 可能使用不同 model；實測 Explore 使用 `claude-haiku-4-5-20251001`，主 agent 為 `claude-sonnet-4-6` |
| **不產生獨立 JSONL** | Subagent 活動全部以 `agent_progress` progress 記錄在主 session JSONL |

來源：`00bbda8a...jsonl`（實測 Explore subagent）

### Agent 類型代號（來源：binary）

```js
{ local_bash:"b", local_agent:"a", remote_agent:"r", in_process_teammate:"t" }
```

### Console UI 呈現

`agent_progress` 在 console 以縮排樹狀即時呈現：

```
Explore(List files in project)
  ⎿  Prompt: 列出...
  ⎿  Bash(find /d/project/test_claude_skill ...)
  ⎿  Read(/d/project/test_claude_skill/CLAUDE.md)
  ⎿  Response: 完美。現在...
```

`⎿` 表示 subagent 子操作；主 LLM 只拿到最後的 Response 內容。

### agent_progress 記錄結構

```json
{
  "type": "progress",
  "data": {
    "type": "agent_progress",
    "agentId": "aabcf4bda0b27ca01",
    "message": {
      "type": "assistant",
      "message": { "model": "claude-haiku-4-5-20251001", "content": [...] }
    }
  },
  "toolUseID": "agent_msg_...",
  "parentToolUseID": "toolu_011re..."
}
```

### Agent toolUseResult 結構

```json
{
  "status": "completed",
  "agentId": "aabcf4bda0b27ca01",
  "content": [{ "type": "text", "text": "..." }],
  "totalDurationMs": 16247,
  "totalTokens": 23272,
  "totalToolUseCount": 5,
  "usage": { ... }
}
```

### Agent 間通訊協議（IPC message types）

| 訊息類型 | 說明 |
|---------|------|
| `task_assignment` | 主 → sub：派任務 |
| `idle_notification` | sub → 主：閒置（含 summary、completedTaskId） |
| `agent_progress` | sub → 主：執行進度 |
| `permission_request` | sub → 主：請求操作許可 |
| `permission_response` | 主 → sub：回覆許可 |
| `shutdown_request/approved/rejected` | 關閉協商 |
| `teammate_terminated` | teammate 結束通知 |
| `team_permission_update` | 團隊權限同步 |
| `mode_set_request` | 切換操作模式 |
| `plan_approval_request/response` | Plan 模式計畫審核 |

### Agent Memory 目錄

| 範圍 | 路徑 | 特性 |
|------|------|------|
| project | `.claude/agent-memory/` | 版控共享 |
| user | `~/.claude/agent-memory/` | 跨專案 |
| local | `.claude/agent-memory-local/` | 不進版控 |

### Teammate 生成模式

| `teammateMode` | 說明 |
|----------------|------|
| `tmux` | 用 tmux 開新視窗執行 |
| `in-process` | 同進程內執行 |
| `auto` | 自動選擇 |

---

## Hooks

Claude Code 支援在特定事件觸發時自動執行 shell 命令或 LLM prompt。

### 支援的事件（來源：binary `2.1.72`）

| 事件 | 說明 |
|------|------|
| `PreToolUse` | 工具呼叫前 |
| `PostToolUse` | 工具呼叫成功後 |
| `PostToolUseFailure` | 工具呼叫失敗後 |
| `UserPromptSubmit` | 使用者送出訊息時 |
| `Notification` | 收到通知時 |
| `SessionStart` / `SessionEnd` | session 開始/結束 |
| `Stop` | Claude 停止回應時 |
| `SubagentStart` / `SubagentStop` | subagent 啟動/停止 |
| `PreCompact` | context 壓縮前 |
| `PermissionRequest` | 權限確認請求時 |
| `Setup` | 初始化時 |
| `TeammateIdle` | teammate 閒置時 |
| `TaskCompleted` | 任務完成時 |
| `Elicitation` / `ElicitationResult` | 資訊蒐集事件 |
| `ConfigChange` | 設定變更時 |
| `WorktreeCreate` / `WorktreeRemove` | worktree 建立/移除 |
| `InstructionsLoaded` | 指令載入時 |

### Hook 類型（來源：binary schema）

**`command` 類型**（執行 shell 命令）

| 欄位 | 必填 | 說明 |
|------|------|------|
| `type` | ✓ | `"command"` |
| `command` | ✓ | 要執行的 shell 命令 |
| `timeout` | | 逾時秒數 |
| `statusMessage` | | spinner 顯示的自訂訊息 |
| `once` | | `true` 表示執行一次後自動移除 |
| `async` | | `true` 表示背景執行，不阻塞 |
| `asyncRewake` | | `true` 表示背景執行，但 exit code 2 時喚醒 model（blocking error），隱含 async |

**`prompt` 類型**（讓 LLM 評估）

| 欄位 | 必填 | 說明 |
|------|------|------|
| `type` | ✓ | `"prompt"` |
| `prompt` | ✓ | 提示文字（可用 `$ARGUMENTS` 取得 hook 輸入 JSON） |
| `timeout` | | 逾時秒數 |
| `model` | | 指定 model（如 `"claude-sonnet-4-6"`），預設用小型快速 model |
| `statusMessage` | | spinner 顯示的自訂訊息 |
| `once` | | `true` 表示執行一次後自動移除 |

### Hook 在 JSONL 中的記錄

Hook 執行結果以 `progress` 記錄注入 session JSONL：

```json
{
  "type": "progress",
  "data": {
    "type": "hook_progress",
    "hookName": "PostToolUse:Read"
  }
}
```

`hookName` 格式為 `{事件}:{工具名稱}`（如 `PostToolUse:Read`）。

來源：`6370316b...jsonl`；hook schema 來自 binary `2.1.72`
