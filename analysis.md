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
- **Bash 匹配邏輯**：prefix/exact/wildcard 三種規則類型；複合命令不匹配 prefix（防越獄設計）
- **Permission Modes**：acceptEdits/bypassPermissions/dontAsk/plan/default/auto 六種模式；與 allow 規則的差異
- **官方安全機制**：寫入範圍限制、命令黑名單、injection 偵測、fail-closed

## [session.md](session.md) — Session 記錄

- **儲存位置與目錄結構**：subagents/、tool-results/ 何時產生
- **JSONL 記錄類型**：user、assistant、progress、system、file-history-snapshot、compact_boundary
- **progress 子類型**：hook_progress、bash_progress、agent_progress
- **toolUseResult 格式**：正常（dict）vs 錯誤（string）
- **大型 tool result**：超過閾值時外部儲存機制
- **Checkpointing**：file editing tool 執行前自動快照；Bash 修改不追蹤；Rewind 五種操作；Summarize vs /compact 差異

## [model.md](model.md) — 模型行為

- **Extended Thinking**：thinking 明文 vs 加密兩種狀態、設定方式

## [docs-reference.md](docs-reference.md) — 官方文件索引

- **頁面一覽**：6 頁已讀（how-claude-code-works / overview / memory / common-workflows / best-practices / ide-integrations）
- **各頁重點**：Agentic Loop、Skill 載入、MEMORY.md 限制、Plan Mode、Fan-out pattern、initialPermissionMode 等
