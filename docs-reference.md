# Claude Code 官方文件索引

快速查閱官方文件各頁主題，用於驗證機制時定位正確頁面。

> **注意**：文件已從 `docs.anthropic.com` 搬遷至 `code.claude.com`（301 redirect）
> 新 base URL：`https://code.claude.com/docs/en/`

官方索引（llms.txt）：`https://code.claude.com/docs/llms.txt`

---

## 頁面總覽

| slug | 標題 | 機制相關度 |
|------|------|-----------|
| `how-claude-code-works` | How Claude Code works | ★★★ 核心架構 |
| `skills` | Extend Claude with skills | ★★★ Skill 機制 |
| `hooks` | Hooks reference | ★★★ Hook 機制 |
| `hooks-guide` | Automate workflows with hooks | ★★★ Hook 實作 |
| `permissions` | Configure permissions | ★★★ 權限系統 |
| `sub-agents` | Create custom subagents | ★★★ Subagent 機制 |
| `features-overview` | Extend Claude Code | ★★★ 擴充系統總覽 |
| `mcp` | Connect Claude Code to tools via MCP | ★★★ MCP 機制 |
| `plugins` | Create plugins | ★★ Plugin 系統 |
| `plugins-reference` | Plugins reference | ★★ Plugin 技術參考 |
| `interactive-mode` | Interactive mode | ★★★ 互動機制 |
| `keybindings` | Customize keyboard shortcuts | ★ 鍵盤設定 |
| `common-workflows` | Common workflows | ★★ 工作流程 |
| `best-practices` | Best Practices | ★★ 使用建議 |
| `scheduled-tasks` | Run prompts on a schedule | ★★★ 排程機制 |
| `headless` | Run Claude Code programmatically | ★★ SDK/CLI |
| `cli-reference` | CLI reference | ★★ CLI 完整參考 |
| `model-config` | Model configuration | ★★★ 模型設定機制 |
| `memory` | How Claude remembers your project | ★★★ Memory 機制 |
| `settings` | Claude Code settings | ★★★ 設定系統 |
| `quickstart` | Quickstart | ★ 入門 |
| `setup` | Advanced setup | ★ 安裝設定 |
| `desktop` | Use Claude Code Desktop | ★★ Desktop 功能 |
| `claude-code-on-the-web` | Claude Code on the web | ★★ Web 執行機制 |
| `remote-control` | Remote Control | ★★ 遠端連線機制 |
| `checkpointing` | Checkpointing | ★★★ Checkpoint 機制 |
| `security` | Security | ★★ 安全機制 |
| `sandboxing` | Sandboxing | ★★★ Sandbox 機制 |
| `costs` | Manage costs effectively | ★ 成本管理 |
| `agent-teams` | Orchestrate agent teams | ★★★ Agent Team 機制 |
| `fast-mode` | Fast mode | ★★ Fast Mode 機制 |
| `output-styles` | Output styles | ★★★ System Prompt 機制 |
| `monitoring-usage` | Monitoring | ★★ OpenTelemetry |
| `server-managed-settings` | Server-managed settings | ★★ 企業設定分發 |
| `code-review` | Code Review | ★ 自動 PR Review |
| `github-actions` | GitHub Actions | ★ CI 整合 |
| `gitlab-ci-cd` | GitLab CI/CD | ★ CI 整合 |
| `network-config` | Enterprise network config | ★ 網路設定 |
| `third-party-integrations` | Enterprise deployment | ★ 企業部署 |
| `troubleshooting` | Troubleshooting | ★ 故障排除 |
| `terminal-config` | Terminal setup | ★ 終端機設定 |
| `discover-plugins` | Discover plugins | ★ Plugin 市集 |
| `zero-data-retention` | Zero Data Retention | ★ 資料政策 |
| `analytics` | Analytics | ★ 使用分析 |

---

## 各頁摘要

### how-claude-code-works
來源：官方文件（2026-03-13）

- **Agentic Loop 三階段**：Gather Context → Take Action → Verify Results，循環直到任務完成
- **工具五大類**：File operations / Search / Execution / Web / Code intelligence（需插件）
- **Context 管理**：Skill 描述 session 開始時載入，完整內容按需載入；Subagent 擁有完全獨立 context；接近上限時先清除舊 tool output，再 summarize
- **Session 機制**：`--continue` 延用同一 session ID；`--fork-session` 建立新 ID 並保留歷史；同一 session 多終端開啟時訊息交錯但不損壞
- **Checkpoint**：每次檔案編輯前自動快照，Esc×2 可回捲；local-only，不影響 git，無法還原 DB/API 副作用
- **Permission 模式**：default / acceptEdits / plan，Shift+Tab 切換

---

### skills
來源：官方文件（2026-03-13）

- **Skills 是 commands 超集**：`.claude/commands/` 與 `.claude/skills/` 等效，但 skills 支援目錄結構、frontmatter、模型自動偵測
- **Bundled Skills**：`/simplify`（平行三 review agents）、`/batch`（批量平行修改，每項用獨立 git worktree）、`/debug`、`/loop`、`/claude-api` 等
- **Frontmatter 關鍵欄位**：
  - `disable-model-invocation: true`：阻止 Claude 自動觸發，只能手動 invoke，描述不注入 context
  - `user-invocable: false`：從 / 選單隱藏，只有 Claude 可 invoke
  - `context: fork`：在獨立 subagent context 中執行
  - `allowed-tools`：限制 skill 可用工具（軟性，加入 alwaysAllowRules）
  - `model`：指定執行模型
  - `hooks`：限定此 skill 生命週期的 hook
- **Context 載入時機**：Skill 描述 budget = context window 的 2%（fallback 16,000 字元）；`disable-model-invocation: true` 的 skill 描述不佔 context
- **字串替換變數**：`$ARGUMENTS`、`$ARGUMENTS[N]`（0-based）、`$N`（縮寫）、`${CLAUDE_SESSION_ID}`、`${CLAUDE_SKILL_DIR}`
- **`!command` 預處理**：在送給 Claude 前先執行 shell，將 stdout 替換進去；Claude 只看到結果
- **Priority 順序**：Enterprise > Personal (`~/.claude/skills/`) > Project (`.claude/skills/`) > Plugin（需 `plugin-name:skill-name` namespace）
- **Monorepo 自動發現**：從當前路徑往上搜尋巢狀 `.claude/skills/` 目錄

---

### hooks
來源：官方文件（2026-03-13）

- **完整 Hook 事件（17+個）**：SessionStart、InstructionsLoaded、UserPromptSubmit、PreToolUse、PermissionRequest、PostToolUse、PostToolUseFailure、Notification、SubagentStart、SubagentStop、Stop、TeammateIdle、TaskCompleted、ConfigChange、WorktreeCreate、WorktreeRemove、PreCompact、SessionEnd
- **四種 Hook 類型**：`command`（shell）、`http`（POST URL）、`prompt`（單次 LLM 判斷）、`agent`（多輪 LLM + 工具，最多 50 輪）；並非每個事件支援全部類型
- **Exit Code 語意**：0 = 允許（解析 stdout JSON）；2 = 阻斷（stderr 回傳給 Claude）；其他 = 非阻斷錯誤
- **JSON 輸出控制**：
  - `PreToolUse`：`hookSpecificOutput.permissionDecision`（allow/deny/ask）+ `updatedInput` 修改工具輸入
  - `PostToolUse/Stop/UserPromptSubmit`：頂層 `decision: "block"` + `reason`
  - 通用：`continue: false`（立即停止）、`systemMessage`（注入 context）、`additionalContext`
- **Async Hooks**：`command` 類型加 `"async": true`，背景執行不阻斷 Claude；結束後 systemMessage/additionalContext 在下一 turn 送出；prompt/agent 不支援 async
- **Matcher 機制**：regex 字串，針對不同事件匹配不同欄位（PreToolUse 匹配 tool name，MCP 格式 `mcp__<server>__<tool>`）
- **Hook 快照**：session 啟動時抓取快照；進行中修改不立即生效，需在 `/hooks` 選單審閱後才套用（防惡意修改）
- **`once` 欄位**：只在 skills（非 agents）中可用，設為 true 後該 hook session 中只執行一次
- **`PreCompact` 事件**：compaction 前觸發，matcher 支援 `manual` 和 `auto` 兩種
- **`ConfigChange` 事件**：記錄 settings/skills 修改，可 block（exit 2）阻止非授權修改；policy_settings 不可被 block

---

### hooks-guide
來源：官方文件（2026-03-13）

- **Hook 設定 scope**：user settings / project settings / local settings / managed policy / plugin hooks.json / Skill+Agent frontmatter
- **平行執行與去重**：同一事件所有匹配 hook 平行執行；相同 command/URL 自動去重
- **Stop hook 無限迴圈防護**：必須檢查 `stop_hook_active` 欄位，為 true 時必須 exit 0，否則無窮迴圈
- **Prompt-based hooks**：用 LLM（預設 Haiku）判斷，回傳 `{"ok": true/false, "reason": "..."}`；exit 0 + JSON，不可用 exit 2
- **Agent-based hooks**：產生有 Read/Grep/Glob 工具的 subagent 進行驗證（預設 timeout 60 秒）；適合需讀檔或執行測試才能判斷的場景
- **HTTP hooks**：非 2xx 或連線失敗為非阻斷錯誤（不同於 command 的 exit code）；只能透過 2xx + JSON body 阻斷
- **PostToolUse 限制**：不能復原已執行的操作，只能提供後置反饋

---

### permissions
來源：官方文件（2026-03-13）

- **三層工具類型**：Read-only（不需核准）、Bash commands（永久記憶，per project+command）、File modification（session 結束後重置）
- **規則評估順序**：deny → ask → allow，第一條匹配規則生效；deny 優先於一切
- **Bash 萬用字元**：`Bash(ls *)` 匹配 `ls -la` 但不匹配 `lsof`（空格後的 `*` 有 word boundary）；`Bash(ls*)` 兩者都匹配；shell operator 感知：`Bash(safe-cmd *)` 不允許 `safe-cmd && other-cmd`
- **Read/Edit 路徑語法**：`//path` = filesystem root 絕對路徑；`~/path` = home 目錄；`/path` = project root；`./path` = current dir；注意 `/Users/alice/file` **不是**絕對路徑，需用 `//Users/alice/file`
- **優先序**：Managed（連 CLI 都無法覆蓋）> CLI > Local project > Shared project > User；任一層 deny 不可被覆蓋
- **MCP 規則**：`mcp__puppeteer` 或 `mcp__puppeteer__*` 匹配整個 server；`mcp__puppeteer__navigate` 匹配特定工具
- **Agent 規則**：`Agent(Explore)`、`Agent(my-agent)` 格式，可放 deny 停用特定 subagent
- **Managed-only 設定**：`disableBypassPermissionsMode`、`allowManagedPermissionRulesOnly`、`allowManagedHooksOnly`、`allow_remote_sessions` 等僅在 managed settings 有效
- **Permissions vs Sandboxing**：Permissions 控制工具使用；Sandbox 是 OS 層執行環境隔離（只影響 Bash）；兩者可並用做深度防禦

---

### sub-agents
來源：官方文件（2026-03-13）

- **Built-in Subagents**：`Explore`（Haiku，唯讀，quick/medium/very thorough）、`Plan`（繼承主模型，唯讀）、`general-purpose`（繼承模型，全工具）；另有 `Bash`、`statusline-setup`、`claude-code-guide` 等
- **System prompt**：Subagent 只收到自訂 system prompt + 基本環境資訊，**不繼承** Claude Code 完整 system prompt
- **Priority**：CLI `--agents` > `.claude/agents/`（project）> `~/.claude/agents/`（user）> plugin `agents/`
- **Frontmatter 關鍵欄位**：
  - `tools`/`disallowedTools`：工具 allow/deny list
  - `model`：sonnet/opus/haiku/inherit/完整 model ID
  - `skills`：注入完整 skill 內容（非只描述），subagent 不繼承父對話 skills
  - `mcpServers`：inline 定義，subagent 完成後自動斷線
  - `isolation: worktree`：在臨時 git worktree 中執行，無修改時自動清理
  - `background`：強制背景執行
  - `memory`：跨對話持久記憶目錄，自動載入 MEMORY.md 前 200 行
- **前景 vs 背景**：前景阻斷主對話，permission prompt 透傳用戶；背景並行執行，Claude Code 預先取得所有 permission，執行期間 auto-deny 未預批准的請求，無法回答澄清問題
- **Transcript 儲存**：`~/.claude/projects/{project}/{sessionId}/subagents/agent-{agentId}.jsonl`；預設保留 30 天；主對話 compaction 不影響
- **Auto-compaction**：預設約 95% 容量觸發；`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` 可提早觸發；以 `compact_boundary` type 記錄在 transcript 中，含 `preTokens` 欄位
- **巢狀禁止**：Subagent 不能 spawn 其他 subagent；主對話可用 `tools: Agent(worker)` 限制只能 spawn 特定類型

---

### features-overview
來源：官方文件（2026-03-13）

- **六大擴充機制**：CLAUDE.md / Skills / MCP / Subagents / Agent teams / Hooks
- **優先順序衝突**：Skills 依 managed > user > project 覆蓋；MCP server 依 local > project > user 覆蓋；Hooks 全部合併觸發，不覆蓋
- **Context 成本差異**：CLAUDE.md 每次請求全量載入；MCP tool 定義每次請求；Skills 僅描述每次請求（完整內容按需）；Hooks 完全不佔 context
- **`disable-model-invocation: true`**：skill 描述不注入 context，context 成本為零，只能手動 invoke
- **Agent teams（實驗性）**：預設關閉，需 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`；成員可直接傳訊，共享任務清單自我協調
- **Plugin 打包**：將 skills/hooks/subagents/MCP servers 打包成可分發單元；skills 自動加 namespace（`/plugin-name:skill-name`）
- **CLAUDE.md 建議**：保持在 500 行以下，細項規則拆分到 `.claude/rules/` 並透過 `paths` frontmatter 限定載入時機

---

### mcp
來源：官方文件（2026-03-13）

- **三種 transport**：Streamable HTTP（推薦）、SSE（已棄用）、stdio（本地程序）
- **三種作用域**：local（預設，僅當前專案，存 `~/.claude.json`）、project（`.mcp.json` 可 commit）、user（跨專案）；優先序 local > project > user
- **MCP Tool Search**：MCP tool 描述超過 context 10% 時自動啟用，改為按需動態載入；`ENABLE_TOOL_SEARCH` 環境變數控制；需 Sonnet 4+ 或 Opus 4+（Haiku 不支援）
- **`.mcp.json` 環境變數展開**：`${VAR}` 與 `${VAR:-default}` 語法，套用於 command/args/env/url/headers
- **OAuth 2.0**：`--callback-port` 固定回呼 port；不支援動態 client registration 的 server 需額外提供 `--client-id/--client-secret`
- **Managed MCP**：管理員可部署 `managed-mcp.json`；`allowedMcpServers`/`deniedMcpServers` 白/黑名單，支援按名稱/指令（完全比對）/URL 萬用字元
- **Claude Code as MCP Server**：`claude mcp serve`（stdio 模式）
- **MCP tool 輸出限制**：預設 25,000 tokens；`MAX_MCP_OUTPUT_TOKENS` 調整
- **動態工具更新**：支援 MCP `list_changed` 通知，server 可動態更新可用工具無需斷線

---

### plugins
來源：官方文件（2026-03-13）

- **Plugin 識別**：包含 `.claude-plugin/plugin.json` 的目錄（Standalone 設定不需此 manifest）
- **目錄結構規則**：`commands/`、`agents/`、`skills/`、`hooks/` 必須放在 plugin **根目錄**，不可放在 `.claude-plugin/` 內
- **開發時載入**：`--plugin-dir` flag；同名本地 plugin 優先於已安裝的 marketplace plugin
- **LSP 整合**：`.lsp.json` 設定 Language Server，給 Claude 即時程式碼智慧（診斷、定義跳轉）
- **安裝**：複製到 cache（`~/.claude/plugins/cache`），不能引用 plugin 目錄外路徑；symlink 在複製時會被跟隨
- **`/reload-plugins`**：不重啟的情況下熱載入變更（LSP 設定除外）
- **版本控制**：版本號無 bump 則 cache 不更新，用戶看不到變更

---

### plugins-reference
來源：官方文件（2026-03-13）

- **完整 Hook 事件清單**（包含新增）：PreToolUse、PostToolUse、PostToolUseFailure、PermissionRequest、UserPromptSubmit、Notification、Stop、SubagentStart、SubagentStop、SessionStart、SessionEnd、TeammateIdle、TaskCompleted、PreCompact、ConfigChange、WorktreeCreate、WorktreeRemove
- **Hook 三種類型**：`command`、`prompt`（LLM 評估）、`agent`（有工具的驗證 agent）
- **安裝作用域**：user（預設）、project、local、managed（唯讀）
- **CLI 指令**：`claude plugin install/uninstall/enable/disable/update`；`uninstall` 別名 `remove`/`rm`
- **LSP 設定欄位**：command（必填）、extensionToLanguage（必填）、transport（stdio/socket）、restartOnCrash、maxRestarts 等

---

### interactive-mode
來源：官方文件（2026-03-13）

- **`Ctrl+B`**：將 Bash 指令移到背景執行（tmux 需按兩次）；有唯一 ID，輸出緩衝，Claude 可用 `TaskOutput` tool 取回
- **`Esc+Esc`**：Rewind/Summarize，還原程式碼與對話至先前狀態
- **`/btw`**：overlay 快速問答，不汙染主對話，Claude 處理中也可執行；回應只讀不可追問；無工具存取；成本極低（複用 prompt cache）
- **`! <command>`**：直接執行 shell 並將輸出加入對話；Tab 補全（基於當前專案的 `!` 歷史）
- **Task list**：追蹤複雜多步驟工作，`Ctrl+T` 切換；最多 10 個；跨 compaction 持續存在；`CLAUDE_CODE_TASK_LIST_ID` 可跨 session 共享
- **Prompt suggestions**：session 開啟時從 git 歷史選取範例；後續根據對話自動生成；Tab 接受；`CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION=false` 關閉
- **PR review 狀態**：顯示在 footer（綠/黃/紅），每 60 秒更新，需 gh CLI
- **Vim 模式**：完整 normal/insert mode，text objects（`iw`/`aw`/`i"` 等）
- **重要指令**：`/diff`（互動式 diff）、`/context`（context 用量視覺化）、`/fork`（建立對話分支）、`/security-review`（分析當前分支安全漏洞）

---

### keybindings
來源：官方文件（2026-03-13）

- 設定檔：`~/.claude/keybindings.json`；無需重啟，自動偵測生效（需 v2.1.18+）
- **Context 系統**：每個 binding 指定 context（Global/Chat/Autocomplete/Confirmation/Transcript/Task 等）
- **Action 格式**：`namespace:action`（如 `chat:submit`）；設為 `null` 可解除預設綁定
- **Chord 序列**：空格分隔多個按鍵（如 `ctrl+k ctrl+s`）
- **保留快捷鍵**：`Ctrl+C`（中斷）、`Ctrl+D`（退出）不可重綁
- **Vim 模式獨立**：vim 處理文字輸入層，keybindings 處理元件層；大多數 `Ctrl+key` 穿透 vim 到達 keybinding 系統
- `/doctor` 可診斷語法錯誤、無效 context、保留快捷鍵衝突、重複綁定

---

### common-workflows
來源：官方文件（2026-03-13）

- **Plan Mode**：`--permission-mode plan` 或 Shift+Tab；唯讀 + `AskUserQuestion`；`Ctrl+G` 在編輯器直接修改計畫
- **Subagent 系統**：`/agents` 瀏覽/建立；放在 `.claude/agents/` 供團隊共用；`isolation: worktree` 讓各 subagent 在獨立 worktree 平行執行
- **Git Worktree**：`claude --worktree <name>` 在 `<repo>/.claude/worktrees/<name>` 建立隔離目錄，branch 名為 `worktree-<name>`
- **Session 管理**：`--continue`/`--resume`；`/rename` 命名；`--from-pr <num>` 接續 PR 連結的 session；picker 支援 P（預覽）/R（重命名）/B（過濾 branch）
- **Extended Thinking**：`Option+T`/`Alt+T` 切換；`ultrathink` 關鍵字強制 high effort；`MAX_THINKING_TOKENS=0` 完全停用；Opus 4.6 adaptive，其他固定最多 31,999 tokens
- **`@` 引用**：`@path` 引用檔案/目錄，自動載入沿途 CLAUDE.md；`@server:resource` 引用 MCP 資源
- **Hooks 通知**：`/hooks` 設定 Notification 事件，支援 `permission_prompt`/`idle_prompt`/`auth_success`/`elicitation_dialog` matcher

---

### best-practices
來源：官方文件（2026-03-13）

- **Context window 是最核心資源**：整個對話共用；context 越滿效能越差；應主動用 `/clear` 重置
- **給驗證機制是最高 leverage 操作**：測試/截圖/預期輸出讓 Claude 自我校正
- **四階段工作流程**：Plan Mode 探索 → Plan Mode 規劃（Ctrl+G 編輯）→ Normal Mode 實作 → 提交 PR
- **CLAUDE.md 維護**：包含 Bash 指令、差異化規則、測試方式；排除 Claude 已知的語言慣例；太長導致規則被忽略；支援 `@path` import
- **Compaction 控制**：`/compact <instructions>` 手動壓縮並指定保留重點；CLAUDE.md 可寫 compaction 指令
- **Fan-out 批次**：`for file in ...; do claude -p "..." --allowedTools "..."; done` 平行呼叫
- **常見失敗模式**：kitchen sink session、反覆糾錯超過兩次不清 context、CLAUDE.md 過長、無驗證機制

---

### scheduled-tasks
來源：官方文件（2026-03-13）

- 需 v2.1.72+；任務為 session-scoped（關閉終端即消失）
- **`/loop` 指令**：核心入口；支援 `/loop 5m check...`、`/loop check... every 2h`、或不指定（預設 10 分鐘）
- **底層工具**：`CronCreate`（標準 5 欄位 cron 表達式）、`CronList`、`CronDelete`；每 session 最多 50 個任務
- **排程器**：每秒檢查，低優先度入列，在 Claude 完成當前 turn 後才執行；時間解讀為本地時區
- **Jitter 機制**：週期任務最多延遲 10%（上限 15 分鐘）；單次任務整點/半點前後 90 秒內有抖動；由 task ID 決定（確定性）
- **3 天自動過期**：週期任務建立後 3 天自動過期（最後執行一次後自刪）；持久排程改用 Desktop scheduled tasks 或 GitHub Actions
- **無法 catch-up**：busy 期間的觸發點只補一次
- `CLAUDE_CODE_DISABLE_CRON=1` 完全停用排程器

---

### headless
來源：官方文件（2026-03-13）

- **`-p` flag**：原「headless mode」，底層為 Agent SDK；非互動執行後退出
- **結構化輸出**：`--output-format json` 含 result/session_id/metadata；`--json-schema` 強制輸出符合 JSON Schema 的結構（放在 `structured_output` 欄位）
- **串流輸出**：`--output-format stream-json --verbose --include-partial-messages`；每行獨立 JSON 物件；可用 `jq` 過濾 text_delta
- **`--allowedTools` prefix matching**：`Bash(git diff *)` 允許所有以 `git diff` 開頭的命令（注意空格語意）
- **System prompt**：`--append-system-prompt`（附加，最安全）；`--system-prompt`（完全取代）
- **`-p` 模式限制**：Skill 指令（如 `/commit`）不可用，需改用自然語言

---

### cli-reference
來源：官方文件（2026-03-13）

- **核心命令**：`claude`、`claude -p`、`claude -c`/`-r`、`claude update`、`claude auth`、`claude agents`、`claude mcp`、`claude remote-control`
- **工具控制**：`--allowedTools`（不問直接執行）、`--disallowedTools`（移除）、`--tools`（限清單，`""` 停用全部，`"default"` 全開）
- **System prompt flags**：`--system-prompt`/`--system-prompt-file`（互斥）、`--append-system-prompt`/`--append-system-prompt-file`（可疊加）
- **Session flags**：`--fork-session`（resume 時建新 ID）、`--from-pr <num>`、`--session-id <uuid>`、`--no-session-persistence`
- **執行控制**：`--max-turns`（超過 error 退出）、`--max-budget-usd`、`--fallback-model`（過載自動切換，僅 print mode）、`--dangerously-skip-permissions`
- **`--agents` flag**：JSON 物件定義動態 subagent；欄位：description（必填）、prompt（必填）、tools、model（sonnet/opus/haiku/inherit/full ID）、skills、mcpServers、maxTurns
- **其他**：`--add-dir`（額外工作目錄）、`--strict-mcp-config`（只用指定 MCP）、`--teleport`（web session 搬到本地）、`--teammate-mode auto/in-process/tmux`

---

### model-config
來源：官方文件（2026-03-13）

- **Model Aliases**：`default`（依帳號類型）、`sonnet`、`opus`、`haiku`、`sonnet[1m]`（1M context）、`opusplan`（plan 用 opus，execution 自動切 sonnet）
- **設定優先序**：`/model` > `--model` > `ANTHROPIC_MODEL` > settings `model` 欄位
- **Effort Level（Adaptive Reasoning）**：low/medium/high；僅 Opus 4.6 和 Sonnet 4.6；Opus 4.6 對 Max/Team 預設 medium；`CLAUDE_CODE_EFFORT_LEVEL` 環境變數；`CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` 回退固定 token budget
- **1M Context Window**：`/model sonnet[1m]` 或 `--model claude-sonnet-4-6[1m]`；超過 200K 按 long-context pricing 計費；`CLAUDE_CODE_DISABLE_1M_CONTEXT=1` 停用
- **`availableModels`**：在 managed settings 中限制使用者可選模型
- **`modelOverrides`**：將 Anthropic model ID 對應到 Bedrock ARN 等 provider 特定字串
- **Prompt Caching 控制**：`DISABLE_PROMPT_CACHING=1` 全停；`DISABLE_PROMPT_CACHING_HAIKU/SONNET/OPUS` 針對特定家族停用
- **第三方部署建議**：強烈建議 pin 版本號避免 alias 解析失敗

---

### memory
來源：官方文件（2026-03-13）

- **兩種記憶**：CLAUDE.md（你寫的指令）+ Auto memory（Claude 自動記錄，需 v2.1.59+）
- **CLAUDE.md 多層作用域**：Managed Policy（無法排除）、Project（`./CLAUDE.md`）、User（`~/.claude/CLAUDE.md`）
- **`@path` import**：支援相對/絕對路徑，最多遞迴 5 層，首次遇到外部 import 需用戶批准
- **`.claude/rules/`**：放多個 `.md` 規則檔，frontmatter `paths` 欄位實現路徑限定載入，減少 context 消耗
- **Auto memory 儲存**：`~/.claude/projects/<project>/memory/`，以 git repo 為單位共享；MEMORY.md 為入口，每次 session 只載入前 200 行，詳細內容分散到各 topic 檔案按需讀取
- **`claudeMdExcludes`**：glob 排除特定 CLAUDE.md（Managed policy 不可排除）
- **`/compact` 後 CLAUDE.md 保留**：Claude 重新從磁碟讀取；消失的指令代表只存在於對話中
- **`/memory` 指令**：列出當前載入的所有 CLAUDE.md、切換 Auto memory 開關

---

### settings
來源：官方文件（2026-03-13）

- **5 層優先順序**（高到低）：Managed > CLI > Local (`.claude/settings.local.json`) > Project (`.claude/settings.json`) > User (`~/.claude/settings.json`)
- **Managed settings 部署方式**：Anthropic admin console（伺服器端）、macOS MDM plist、Windows 登錄機碼（HKLM/HKCU）、特定路徑 `managed-settings.json`
- **Array vs Object 設定**：Array 類型跨層合併（concatenated/deduplicated）；Object 類型高優先層整體覆蓋
- **Sandbox 設定**：`allowWrite`/`denyWrite`/`denyRead`/`allowedDomains`/`allowUnixSockets`；路徑前綴 `//` = 絕對路徑，`~/` = home
- **`allowManagedHooksOnly`**：限制只允許 managed hooks；`allowedHttpHookUrls` 白名單
- **MCP 設定位置**：User 層 `~/.claude.json`；Project 層 `.mcp.json`；Managed 層 `managed-mcp.json`
- **環境變數**：超過 50 個，包含 `BASH_DEFAULT_TIMEOUT_MS`、`BASH_MAX_OUTPUT_LENGTH`、`CLAUDE_CODE_SIMPLE`、`CLAUDE_CODE_DISABLE_AUTO_MEMORY` 等
- **`/status` 指令**：查看各設定的實際來源層級
- **`attribution`**：自訂 git commit 的署名文字

---

### quickstart
來源：官方文件（2026-03-13）

- 安裝：Native Install（自動更新）、Homebrew/WinGet（不自動更新）；Windows 需先安裝 Git for Windows
- 認證方式：Claude Pro/Max/Teams/Enterprise、Console API key、Bedrock/Vertex/Foundry
- `/init`：自動分析程式碼庫並生成起始 CLAUDE.md
- 關鍵 CLI：`claude "task"`、`claude -p "query"`、`claude -c`、`claude -r`

---

### setup
來源：官方文件（2026-03-13）

- **系統需求**：macOS 13+、Windows 10 1809+、Ubuntu 20.04+、Alpine 3.19+；4GB RAM
- **Windows**：用 Git Bash 執行指令；`CLAUDE_CODE_GIT_BASH_PATH` 自訂路徑；WSL1 不支援 sandbox
- **更新頻道**：`latest`（立即，預設）或 `stable`（約延遲一週）；`autoUpdatesChannel` 設定
- **Binary 完整性驗證**：SHA256 checksum 發布於 `storage.googleapis.com/claude-code-dist-*/releases/{VERSION}/manifest.json`；macOS 由 Apple 公證
- npm 安裝已被標記為 **deprecated**

---

### desktop
來源：官方文件（2026-03-13）

- **四種 Permission Mode**：Ask / Auto accept edits / Plan / Bypass（需在 Settings 開啟）
- **Parallel sessions**：用 Git worktrees 自動隔離，儲存於 `<project>/.claude/worktrees/`
- **Preview 功能**：啟動 dev server 並在內嵌瀏覽器自動驗證修改（截圖/DOM/點擊）；設定存於 `.claude/launch.json`；`autoVerify` 預設開啟
- **PR 監控**：Auto-fix（失敗自動修復）、Auto-merge（全通過後 squash merge），需 GitHub CLI
- **Scheduled tasks**：存於 `~/.claude/scheduled-tasks/<name>/SKILL.md`；每個任務有固定延遲偏移（最多 10 分鐘）；電腦休眠時跳過，喚醒後最多補執行一次
- **Remote 環境**：Anthropic 雲端執行，關閉 app 後仍持續；`/desktop` 指令從 CLI 切換至 Desktop
- 不支援：Bedrock/Vertex/Foundry、Linux

---

### claude-code-on-the-web
來源：官方文件（2026-03-13）

- 在 Anthropic 管理的隔離 VM 執行，每個 session 獨立 VM（不同於 Remote Control 的本地執行）
- **`/teleport`**：將 web session 拉回本地終端機（需乾淨 working directory、相同 repo、相同帳號）
- **Setup scripts**：Claude Code 啟動前以 root 執行的 Bash 腳本，只在建立新 session 時執行（Resume 跳過）；不同於 SessionStart hooks（每次 session 都執行）
- **網路模式**：Limited（白名單域名，預設）/ No internet / Full internet；所有出站流量經安全 proxy
- **GitHub proxy**：git 操作使用 scoped credential，限制 push 只能操作當前分支
- **Session 搬移**：`claude --remote "task"` 建立新 web session
- 僅支援 GitHub；不支援 ZDR 的組織

---

### remote-control
來源：官方文件（2026-03-13）

- **本地執行，遠端介面**：程式碼在本地機器執行，透過 claude.ai/code 或 Claude mobile app 作為介面
- **啟動方式**：`claude remote-control`（新 session）或現有 session 中 `/remote-control`/`/rc`（帶入歷史）
- **連線機制**：只發出**出站 HTTPS 請求**，不開放入站 port；透過 Anthropic API streaming 路由，使用多個短暫 scoped credential
- **即時同步**：所有連線裝置間同步，可同時從多裝置發送訊息
- **自動重連**：休眠/網路中斷後自動重連；超過約 10 分鐘無連線則 session 逾時
- **每個 instance 一個 remote session**
- `/mobile` 指令顯示 Claude iOS/Android app 下載 QR code

---

### checkpointing
來源：官方文件（2026-03-13）

- **自動快照**：每次檔案編輯前自動建立；每個用戶 prompt 一個 checkpoint；跨 session 持久化，預設 30 天後清理
- **Rewind 選單**（Esc×2 或 `/rewind`）：顯示 prompt 歷史清單，五種操作：
  1. **Restore code and conversation**：同時復原
  2. **Restore conversation**：只復原對話，保留程式碼
  3. **Restore code**：只復原程式碼，保留對話
  4. **Summarize from here**：壓縮指定點之後的對話（釋放 context）
  5. **Never mind**：取消
- **Summarize from here vs /compact**：前者針對性壓縮後段，保留早期完整 context；後者壓縮整個對話
- **重要限制**：Bash 指令造成的修改（rm/mv/cp 等）**不被追蹤**，無法 rewind；只追蹤 Claude 的 file editing tools
- 定位為「session 層級快速復原」，不取代 Git

---

### security
來源：官方文件（2026-03-13）

- 預設唯讀架構，寫入/執行須明確授權
- 寫入範圍限制在啟動目錄及子目錄，無法修改上層目錄
- 防 Prompt Injection：指令黑名單（預設封鎖 `curl`/`wget`）、輸入消毒、context-aware 分析
- Web fetch 使用獨立 context window，避免惡意提示污染主對話
- 可疑 Bash 指令即便已白名單仍須手動審查（Fail-closed）
- **Windows 警告**：不要啟用 WebDAV（可能繞過網路請求權限系統）
- 安全漏洞透過 HackerOne 私下回報

---

### sandboxing
來源：官方文件（2026-03-13）

- **OS 級原語**：macOS 用 Seatbelt，Linux/WSL2 用 bubblewrap；WSL1 不支援
- **寫入範圍**：預設限當前目錄及子目錄；讀取可存取整台電腦（部分路徑除外）
- **網路隔離**：外部 Proxy 控制，允許的 Domain 清單，新 Domain 觸發授權提示
- **兩種沙箱模式**：Auto-allow（沙箱內指令自動允許，逾越才走授權）vs Regular permissions
- **路徑前綴**：`//` = 絕對路徑；`~/` = home；`/` = 相對設定檔目錄；`./` = 相對路徑
- **多層設定合併**：`allowWrite`/`denyWrite`/`denyRead` 跨 settings 層級合併（不互相覆蓋）
- **逃生機制**：`dangerouslyDisableSandbox` 參數可退出，仍須用戶授權；`allowUnsandboxedCommands: false` 停用此機制
- **開源**：sandbox runtime 開源於 npm：`@anthropic-ai/sandbox-runtime`

---

### costs
來源：官方文件（2026-03-13）

- 平均 $6/開發者/天；90% 用戶不超過 $12/天；Sonnet 4.6 約 $100-200/開發者/月
- Agent Teams 各 teammate 約消耗標準 session 的 7 倍 token
- Extended Thinking 預設啟用（31,999 token 上限），可透過 `MAX_THINKING_TOKENS` 調低
- Hooks 可前處理資料（如過濾 log 只留錯誤行），大幅降低 token 量
- 背景任務（對話摘要、`/cost` 等）每 session 約 $0.04 以下

---

### agent-teams
來源：官方文件（2026-03-13）

- **啟用**：`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`（預設停用），需 v2.1.32+
- **架構**：Team lead + Teammates（獨立 Claude Code 實例）+ 共享 Task List + Mailbox 訊息系統
- **與 Subagents 差異**：Subagents 只回報給 lead；Teammates 可互相直接通訊、共享任務清單、自主領取任務
- **任務領取**：用檔案鎖（file locking）防止 race condition
- **顯示模式**：In-process（Shift+Down 切換）vs Split panes（需 tmux 或 iTerm2）
- **Teammate 繼承**：繼承 lead 的權限設定，但不繼承對話歷史
- **Plan Approval 機制**：Teammate 在唯讀計畫模式工作，直到 lead 審核通過
- **`TeammateIdle`/`TaskCompleted` hooks**：exit code 2 可阻擋並回饋
- **已知限制**：無法 resume in-process teammates、不支援巢狀 teams、每 session 只能一個 team

---

### fast-mode
來源：官方文件（2026-03-13）

- 僅適用於 Opus 4.6，速度 2.5x，但每 token 成本更高（非不同模型）
- 需 v2.1.36+；僅支援 Anthropic Console API（不支援 Bedrock/Vertex/Foundry）
- `/fast` 切換，或 settings 設定 `"fastMode": true`；啟用時顯示 `↯` 圖示
- **中途啟用注意**：按 fast mode 費率計費整個對話的 uncached context，建議 session 開頭啟用
- 達到 rate limit 時自動 fallback 到標準 Opus 4.6，`↯` 圖示變灰，冷卻後自動重啟
- `fastModePerSessionOptIn: true`：讓每次 session 需重新開啟
- `CLAUDE_CODE_DISABLE_FAST_MODE=1` 完全禁用

---

### output-styles
來源：官方文件（2026-03-13）

- **直接修改 system prompt**（不同於 CLAUDE.md 作為用戶訊息附加）
- **三種內建樣式**：Default（標準）、Explanatory（在任務間插入教學 "Insights"）、Learning（加入 `TODO(human)` 讓使用者親手寫程式碼）
- 所有樣式都移除「簡潔輸出」指令
- `/config > Output style` 選取；儲存至 `.claude/settings.local.json`
- 因在 session 開始時寫入 system prompt，**更改在下次新 session 才生效**（維持 prompt caching）
- **自訂樣式**：Markdown 檔案含 frontmatter，放在 `~/.claude/output-styles/`（user）或 `.claude/output-styles/`（project）；frontmatter 欄位：`name`、`description`、`keep-coding-instructions`

---

### monitoring-usage
來源：官方文件（2026-03-13）

- 透過 OpenTelemetry（OTel）輸出 telemetry；`CLAUDE_CODE_ENABLE_TELEMETRY=1`
- **Metrics exporter**：`otlp`、`prometheus`、`console`；**Logs exporter**：`otlp`、`console`
- **OTLP 傳輸協定**：grpc / http/json / http/protobuf；可為 metrics/logs 分別設定 endpoint
- **提供的 Metrics**：session 數、修改行數、PR 數、commit 數、費用（USD）、token 用量（含 cache）、Code Edit 決策、active time
- **Events**：`user_prompt`、`tool_result`、`api_request`、`api_error`、`tool_decision`
- **`prompt.id`（UUID v4）**：關聯單次 prompt 所觸發的所有 event；不包含在 metrics（避免無限增長的 series）
- **隱私控制**：預設不記錄 prompt 內容（只記長度）；`OTEL_LOG_USER_PROMPTS=1` 才啟用
- **動態 header**：`otelHeadersHelper` 設定腳本路徑，預設每 29 分鐘重新整理（適合短期 token）
- **Cardinality 控制**：可停用 `session.id`/`user.account_uuid`/`app.version` 等 dimension

---

### server-managed-settings
來源：官方文件（2026-03-13）

- 僅 Teams/Enterprise（v2.1.38+ for Teams）；從 Claude.ai admin console 設定
- **非同步拉取**：session 開啟時拉取，每小時輪詢；快取在網路失敗時仍生效
- **優先級最高**：高於所有其他設定層（含 CLI 參數）
- 特定設定（Shell 指令/自訂環境變數/Hook）需用戶在安全對話框明確核准；`-p` mode 跳過對話框
- 不支援：Bedrock/Vertex/Foundry/自訂 `ANTHROPIC_BASE_URL`
- **Beta 限制**：所有用戶套用相同設定（不支援群組）；MCP server 設定無法透過此分發

---

### code-review
來源：官方文件（2026-03-13）

- 多個專門化 agent 並行分析 PR diff + 周邊程式碼，再驗證過濾誤報，以 inline comment 貼在具體程式碼行
- **嚴重度**：🔴 Normal / 🟡 Nit / 🟣 Pre-existing（非本 PR 引入）
- 觸發：PR 建立後一次、每次 push、或 `@claude review` 留言
- **自訂**：`CLAUDE.md`（通用指引，新增違規為 nit 等級）+ `REVIEW.md`（僅限審查規則，可跳過特定目錄）
- 費用：平均 $15-25/次，不計入方案配額
- 不支援：啟用 ZDR 的 organization

---

### github-actions
來源：官方文件（2026-03-13）

- 在 PR/Issue 留言中 `@claude` 觸發；`/install-github-app` 快速安裝
- 核心參數：`prompt`、`claude_args`（CLI 參數直通）、`trigger_phrase`、`use_bedrock`/`use_vertex`
- 支援 AWS Bedrock OIDC 認證（IAM role，無靜態 key）；Bedrock 模型 ID 含地區前綴（`us.anthropic.claude-sonnet-4-6`）
- 支援 Google Vertex AI Workload Identity Federation

---

### network-config
來源：官方文件（2026-03-13）

- **HTTP/HTTPS proxy**：`HTTPS_PROXY`/`HTTP_PROXY`；不支援 SOCKS
- **自訂 CA 憑證**：`NODE_EXTRA_CA_CERTS=/path/to/ca.pem`（企業自簽/TLS inspection 必備）
- **mTLS 客戶端憑證**：`CLAUDE_CODE_CLIENT_CERT`/`CLAUDE_CODE_CLIENT_KEY`/`CLAUDE_CODE_CLIENT_KEY_PASSPHRASE`
- **必須對外開放**：`api.anthropic.com`、`claude.ai`、`platform.claude.com`

---

### third-party-integrations
來源：官方文件（2026-03-13）

- **五種部署選項**：Claude for Teams/Enterprise / Anthropic Console / Amazon Bedrock / Google Vertex AI / Microsoft Foundry
- **LLM Gateway vs Proxy**：Proxy 走 `HTTPS_PROXY`；Gateway 走 `ANTHROPIC_BASE_URL`
- `CLAUDE_CODE_SKIP_BEDROCK_AUTH=1`/`CLAUDE_CODE_SKIP_VERTEX_AUTH=1`：由 Gateway 代為處理認證
- 系統層級 CLAUDE.md（如 macOS `/Library/Application Support/ClaudeCode/CLAUDE.md`）實現全組織標準化
- `/status` 指令驗證 proxy/gateway 設定

---

### troubleshooting
來源：官方文件（2026-03-13）

- `/doctor` 指令：診斷安裝狀態/版本/settings JSON 格式/MCP 設定/keybinding/context 使用量
- 安裝目錄：macOS/Linux `~/.local/bin/claude`；Windows `%USERPROFILE%\.local\bin\claude.exe`
- TLS 錯誤：`NODE_EXTRA_CA_CERTS` 設定企業 CA
- Alpine musl 問題：需裝 `libgcc libstdc++ ripgrep` + `USE_BUILTIN_RIPGREP=0`
- Search/`@file`/skills 失效：安裝系統 `ripgrep` + `USE_BUILTIN_RIPGREP=0`

---

### terminal-config
來源：官方文件（2026-03-13）

- Shift+Enter 換行：iTerm2/WezTerm/Ghostty/Kitty 原生支援；`/terminal-setup` 自動設定 VS Code/Alacritty/Zed/Warp
- 通知：Kitty/Ghostty 原生；iTerm2 需在 Settings 啟用
- 大量輸入避免直接 paste（VS Code 終端機截斷），改用寫入檔案再讓 Claude 讀取

---

### discover-plugins
來源：官方文件（2026-03-13）

- **Marketplace 兩步驟**：`add`（登錄 catalog）→ `install`（安裝），類似 app store
- 官方 marketplace（`claude-plugins-official`）預設啟用
- **Code Intelligence 插件（LSP）**：每次 Claude 編輯後觸發 language server 診斷；支援 Python/TypeScript/Rust/Go/Java 等 11 種語言
- **安裝作用域**：User（跨所有專案）/ Project（可共享給協作者）/ Local
- `extraKnownMarketplaces` 設定：組織管理員統一發布團隊 marketplace

---

### zero-data-retention
來源：官方文件（2026-03-13）

- 僅適用於 Claude for Enterprise，啟用後 prompt/response 在回傳後不被 Anthropic 儲存
- **不在 ZDR 範圍**：claude.ai 聊天、Analytics 中繼資料、管理資料
- **啟用後停用的功能**：Claude Code on the Web、Desktop Remote sessions、`/feedback`
- Bedrock/Vertex/Foundry 需參照各平台自身資料保留政策

---

### analytics
來源：官方文件（2026-03-13）

- Teams/Enterprise：`claude.ai/analytics/claude-code`；API/Console：`platform.claude.com/claude-code`
- **指標**：接受程式碼行數、建議接受率、DAU、PR 數、PR 貢獻者排行榜
- **PR 歸因邏輯**：分析已合併 PR 的 diff，比對 Claude Code session 輸出；信心高者計入；被大幅改寫（差異 >20%）不歸因；lock files/generated code/build artifacts 自動排除
- **歸因時間窗口**：PR 合併日前 21 天至後 2 天的 session
- 被歸因的 PR 自動標記 `claude-code-assisted` label
