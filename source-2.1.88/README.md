# Claude Code 2.1.88 Source Code（精選）

## 來源

2026/03/31 Anthropic 意外將 source map 打包進 `@anthropic-ai/claude-code@2.1.88`，暴露完整 TypeScript 原始碼（51.2 萬行，約 1,884 個檔案）。

本資料夾僅存放與機制研究最相關的**精選檔案**，非完整原始碼。

- 原始倉庫：[xorespesp/claude-code](https://github.com/xorespesp/claude-code)（2,006 TS/TSX 檔案）
- 整合分析：[Leonxlnx/claude-code-system-prompts](https://github.com/Leonxlnx/claude-code-system-prompts)

## 已下載檔案（26,012 行）

| 檔案 | 行數 | 主題 |
|------|------|------|
| `QueryEngine.ts` | 1,295 | **核心 Agentic Loop 引擎** |
| `query.ts` | 1,729 | Query 處理邏輯 |
| `main.tsx` | 4,690 | 初始化、feature flags、MCP、設定 |
| `Tool.ts` | 792 | Tool 基礎類別定義 |
| `tools.ts` | 389 | Tool 集合與載入 |
| `Task.ts` | 125 | Task 結構定義 |
| `tasks.ts` | 39 | Task 工具函式 |
| `history.ts` | 464 | 對話歷史管理 |
| `context.ts` | 189 | Context 管理 |
| `assistant/index.ts` | 14 | Assistant 入口 |
| `constants/prompts.ts` | 914 | **Prompt 常數（各 section 原文）** |
| `constants/systemPromptSections.ts` | 68 | **System prompt section 名稱定義** |
| `constants/tools.ts` | 112 | 工具名稱常數 |
| `utils/systemPrompt.ts` | 123 | **System prompt 組裝邏輯（dj()）** |
| `utils/toolSearch.ts` | 756 | **ToolSearch 完整實作** |
| `utils/hooks.ts` | 5,022 | **Hooks 系統（Hook executor）** |
| `utils/toolSchemaCache.ts` | 26 | Tool schema cache 機制 |
| `utils/sessionStorage.ts` | 5,105 | **Session JSONL 讀寫邏輯** |
| `utils/sessionStart.ts` | 232 | Session 啟動流程 |
| `utils/sessionState.ts` | 150 | Session 狀態管理 |
| `utils/undercover.ts` | 89 | Undercover 模式（隱藏功能） |
| `utils/permissions/permissions.ts` | 1,486 | **權限系統核心** |
| `utils/permissions/bashClassifier.ts` | 61 | Bash 命令分類器 |
| `utils/permissions/shellRuleMatching.ts` | 228 | **Shell 規則匹配邏輯** |
| `utils/permissions/permissionRuleParser.ts` | 198 | 規則解析器 |
| `utils/permissions/PermissionMode.ts` | 141 | Permission mode 定義 |
| `utils/permissions/dangerousPatterns.ts` | 80 | 危險命令模式 |
| `utils/permissions/yoloClassifier.ts` | 1,495 | Yolo mode 分類器 |

## 尚未下載的重要檔案

（需要時再去 [xorespesp/claude-code](https://github.com/xorespesp/claude-code) 取得）

- `utils/memory/` — Memory 系統
- `utils/skills/` — Skill 系統實作
- `utils/mcp/` — MCP 整合
- `utils/settings/` — 設定系統
- `components/` — Terminal UI（Ink）
- `utils/git.ts` — Git 操作
