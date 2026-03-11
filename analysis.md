# Claude Code 機制分析

本文件為索引，各主題詳見對應檔案。

---

## [tools.md](tools.md) — 工具系統

- **Agentic Loop**：工具執行架構（批次 tool call、例外情況）
- **工具分類**：Pre-loaded / Deferred / MCP，及各工具的權限設定
- **ToolSearch**：載入 deferred 工具的機制與效率影響
- **Skill 系統**：SKILL.md 結構、觸發方式、動態注入
- **Agent 工具**：subagent_type 選項、特性、IPC 通訊協議、memory 目錄
- **Hooks**：事件清單（21 種）、command/prompt 兩種類型及其 schema

## [permissions.md](permissions.md) — 權限系統

- **兩個層次**：工具權限（可設定）vs 判斷性確認（不可設定）
- **permissions.allow 格式**：工具、prefix、domain、skill 等規則
- **IPC 確認流程**：permission_request/response 結構；確認過程不進 JSONL
- **Bash 匹配邏輯**：prefix/exact/wildcard 三種規則類型；複合命令不匹配 prefix（防越獄設計）

## [session.md](session.md) — Session 記錄

- **儲存位置與目錄結構**：subagents/、tool-results/ 何時產生
- **JSONL 記錄類型**：user、assistant、progress、system、file-history-snapshot
- **progress 子類型**：hook_progress、bash_progress、agent_progress
- **toolUseResult 格式**：正常（dict）vs 錯誤（string）
- **大型 tool result**：超過閾值時外部儲存機制

## [model.md](model.md) — 模型行為

- **Extended Thinking**：thinking 明文 vs 加密兩種狀態、設定方式
