# Claude Code 機制分析

本文件為索引，各主題詳見對應檔案。

---

## [tools.md](tools.md) — 工具系統

- **Agentic Loop**：工具執行架構（批次 tool call、例外情況）
- **工具分類**：Pre-loaded / Deferred / MCP；依功能：唯讀/寫入/執行/meta 等
- **為何有 Read/Write**：與 Bash 的本質差異（權限粒度、token 限制、diff、寫入限制）
- **ToolSearch**：載入 deferred 工具的機制與效率影響
- **工具與 LLM 關係**：哪些工具內部使用 LLM（Agent/Skill/prompt hook）
- **Skill 系統**：SKILL.md 結構、觸發方式、動態注入；執行模式（注入/腳本/agent/fork）；Priority 順序（Enterprise > Personal > Project > Plugin）
- **Output Styles**：直接替換 system prompt（非附加）；三種內建樣式；自訂樣式 frontmatter；下次新 session 才生效
- **Skill allowed-tools vs Agent 工具權限**：差異與設計原因
- **Agent 工具**：subagent_type 選項、特性、IPC 通訊協議、memory 目錄
- **Hooks**：事件清單（21 種）、command/http/prompt/agent 四種類型及其 schema；JSON 輸出控制欄位；Stop hook 無限迴圈防護（`stop_hook_active`）；ConfigChange 審計；Matcher 機制；快照機制

## [permissions.md](permissions.md) — 權限系統

- **兩個層次**：工具權限（可設定）vs 判斷性確認（不可設定）
- **permissions.allow 格式**：工具、prefix、domain、skill 等規則（tool-level vs param-level）
- **IPC 確認流程**：permission_request/response 結構；確認過程不進 JSONL
- **Bash 匹配邏輯**：prefix/exact/wildcard 三種規則類型；複合命令不匹配 prefix（防越獄設計）；rule content escaping
- **DANGEROUS_BASH_PATTERNS**：直譯器/shell/套件執行器黑名單；ANT-ONLY 追加項（gh/curl/kubectl 等）
- **權限決策完整流程**：`hasPermissionsToUseToolInner()` 9 步驟（deny→ask→checkPermissions→bypass-immune→bypassPermissions→allow rule）
- **Auto Mode 分類器**：TRANSCRIPT_CLASSIFIER（yoloClassifier）兩階段 XML 分類；bashClassifier 為 ANT-ONLY stub；用戶可透過 `settings.autoMode` 自訂規則
- **Permission Modes**：acceptEdits/bypassPermissions/dontAsk/plan/default/auto 六種模式；與 allow 規則的差異
- **規則來源與 Legacy 別名**：8 種 PermissionRuleSource；Task→Agent 等歷史別名自動正規化

## [session.md](session.md) — Session 記錄

- **儲存位置與目錄結構**：subagents/、tool-results/ 何時產生
- **Lazy Materialization**：JSONL 在第一個 user/assistant 訊息才建立；beforehand 進 pendingEntries buffer
- **JSONL 完整 Entry 類型**：transcript（user/assistant/attachment/system）+ metadata（summary/custom-title/pr-link 等）+ 其他（file-history-snapshot/content-replacement/marble-origami-*/queue-operation）
- **Progress 記錄已廢棄**（PR #24099 後不再寫入 JSONL）；舊 JSONL 中的 progress 是遺留記錄
- **TranscriptMessage 額外欄位**：sessionId/version/gitBranch/cwd/userType/entrypoint/slug 等 session-stamp
- **Token Usage**：嵌在 assistant 的 `message.usage`；compact 後被保留訊息的 usage 歸零防止再觸發壓縮
- **Subagent Sidechain**：寫入 {sessionId}/subagents/agent-{id}.jsonl，UUID dedup 跳過 sidechain 防 chain 斷裂
- **toolUseResult 格式**：正常（dict）vs 錯誤（string）
- **大型 tool result**：超過閾值時外部儲存機制
- **Checkpointing**：file editing tool 執行前自動快照；Bash 修改不追蹤；Rewind 五種操作；Summarize vs /compact 差異

## [model.md](model.md) — 模型行為

- **Extended Thinking**：thinking 明文 vs 加密兩種狀態、設定方式
- **System Prompt 結構**：`dj()` 組裝函式；靜態 section 固定順序（Ws6/js6/Es6/Ts6/Xs6/Js6/Vs6）；動態 section（memory/env/language/output_style/mcp）；Output Style 對 system prompt 的影響；feature flags（tengu_sotto_voce 等）；CLAUDE_CODE_SIMPLE 極簡模式

## [prompt-schema.md](prompt-schema.md) — Prompt 與 Schema 原文

- **System Prompt 原文**：`dj()` 組裝函式；各靜態/動態 section 函式完整原文（Ws6/js6/Es6/Ts6/Xs6/Js6/Vs6/ws6/zs6/Ep1）
- **工具 Description 原文**：LLM 實際看到的各工具 description 文字
- **工具 Input Schema**：各工具 tool call 所需參數（Pre-loaded 9 個 + Deferred 7 個）；來源 binary Zod schema

## [source-analysis/undercover.md](source-analysis/undercover.md) — Undercover 模式

- **ANT-ONLY 功能**：外部 build 全部 dead-code-eliminated，外部用戶不受影響
- **啟用條件**：`CLAUDE_CODE_UNDERCOVER=1` 強制開；repo 非內部白名單則自動開；無強制 OFF
- **注入指令原文**：禁止 commit/PR 包含模型代號（Capybara/Tengu）、未發布版本號、內部 repo 名、Co-Authored-By 等

## [ui.md](ui.md) — Claude Code Web UI 行為

- **Conversation Metadata**：branch/PR 對應在 conversation 初始化時固定，整個 session 不可變
- **Create PR vs View PR**：PR 一旦建立即鎖定為「View PR」，即使 PR 已 merge 也不切回；需開新 conversation 才能再次「Create PR」
- **已知限制**：手動建 PR 無法被偵測、branch rename 導致按鈕失效
- 相關 issue：anthropics/claude-code#11176、anthropics/claude-code#30021

## [docs-reference.md](docs-reference.md) — 官方文件索引

- **頁面一覽**：6 頁已讀（how-claude-code-works / overview / memory / common-workflows / best-practices / ide-integrations）
- **各頁重點**：Agentic Loop、Skill 載入、MEMORY.md 限制、Plan Mode、Fan-out pattern、initialPermissionMode 等
