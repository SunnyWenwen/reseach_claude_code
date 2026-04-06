# Claude Code 2.1.88 原始碼分析任務清單

## 說明

本清單記錄對 `source-2.1.88/` 中各原始碼檔案的待分析任務。

**原則**：
- 每次分析完一個任務，將結果更新進對應的分析文件（`tools.md`、`permissions.md`、`session.md`、`model.md`、或新建子文件）
- 標注來源：「來源：外流原始碼 2.1.88 `FileName.ts` `functionName()`」
- 若發現與現有文件記錄不符，**以原始碼為準**並更新

---

## 優先級 1：核心機制（最影響研究理解）

### T01 — Agentic Loop 核心邏輯
- **檔案**：`QueryEngine.ts`（1,295 行）
- **目標**：
  - Loop 的實際結構（while/recursive？停止條件在哪？）
  - Tool call 的並行執行邏輯
  - Stop reason 判斷（`end_turn` vs `tool_use`）
  - Max turns 限制是否存在
- **更新至**：`tools.md`（Agentic Loop 章節）

### T02 — System Prompt 組裝機制
- **檔案**：`utils/systemPrompt.ts`（123 行）、`constants/prompts.ts`（914 行）、`constants/systemPromptSections.ts`（68 行）
- **目標**：
  - `dj()` 對應的 readable 函式名稱確認
  - 各 section 的組裝條件（feature flag、工具集合、Output Style）
  - `__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__` 的實際位置
  - `USER_TYPE=ant` 條件的判斷邏輯
- **更新至**：`prompt-schema.md`

### T03 — ToolSearch 實作
- **檔案**：`utils/toolSearch.ts`（756 行）、`utils/toolSchemaCache.ts`（26 行）
- **目標**：
  - ToolSearch 回傳值是什麼（schema 文字？空字串？）
  - deferred tool 如何在 ToolSearch 後變得可用（修改 tools[]？還是別的機制？）
  - toolSchemaCache 的作用
  - 解答「ToolSearch 是否造成 cache miss」的問題
- **更新至**：`tools.md`（ToolSearch 章節）

### T04 — 權限系統核心
- **檔案**：`utils/permissions/permissions.ts`（1,486 行）、`utils/permissions/shellRuleMatching.ts`（228 行）、`utils/permissions/permissionRuleParser.ts`（198 行）
- **目標**：
  - Bash 命令匹配的完整邏輯（prefix 規則、複合命令處理）
  - Permission mode 的切換機制
  - IPC 如何傳遞 permission 結果
- **更新至**：`permissions.md`

---

## 優先級 2：重要機制補充

### T05 — Session JSONL 寫入邏輯
- **檔案**：`utils/sessionStorage.ts`（5,105 行）
- **目標**：
  - JSONL 每個 record type 的寫入時機
  - `system` record 的結構（有沒有 system prompt 欄位？）
  - token usage 怎麼記錄
  - `cache_read_input_tokens` 的計算
- **更新至**：`session.md`

### T06 — Hooks 系統
- **檔案**：`utils/hooks.ts`（5,022 行）
- **目標**：
  - Hook 的觸發時機（PreToolUse / PostToolUse / Stop / SessionStart）
  - Hook executor 的執行邏輯
  - Hook 輸出如何影響後續行為（block、approve、modify）
  - `<user-prompt-submit-hook>` 的處理
- **更新至**：`tools.md`（Hooks 章節）

### T07 — Bash 危險命令分類
- **檔案**：`utils/permissions/bashClassifier.ts`（61 行）、`utils/permissions/dangerousPatterns.ts`（80 行）、`utils/permissions/yoloClassifier.ts`（1,495 行）
- **目標**：
  - 哪些命令被標記為危險
  - compound command（`&&`、`||`、`;`）的處理邏輯確認
  - Yolo mode 的分類邏輯
- **更新至**：`permissions.md`

### T08 — Undercover 模式
- **檔案**：`utils/undercover.ts`（89 行）
- **目標**：
  - Undercover 模式的完整 prompt 原文
  - 觸發條件（什麼情況下注入）
  - Co-Authored-By 移除邏輯
- **更新至**：新建 `source-analysis/undercover.md`

---

## 優先級 3：進階機制

### T09 — Query 處理流程
- **檔案**：`query.ts`（1,729 行）
- **目標**：
  - query.ts 與 QueryEngine.ts 的分工
  - Streaming 處理邏輯
  - Extended Thinking 的啟用條件
  - Cache control 的設定位置（`scope: "global"` 在哪設？）
- **更新至**：`model.md`

### T10 — Tool 定義與載入
- **檔案**：`Tool.ts`（792 行）、`tools.ts`（389 行）、`constants/tools.ts`（112 行）
- **目標**：
  - Pre-loaded vs deferred tool 的區分方式（flag？array？）
  - Tool description 與 schema 的儲存結構
  - Tool 執行結果如何回傳給 API
- **更新至**：`tools.md`

### T11 — Session 啟動與狀態
- **檔案**：`utils/sessionStart.ts`（232 行）、`utils/sessionState.ts`（150 行）
- **目標**：
  - Session 初始化流程
  - 哪些狀態在 session 間保持
  - Subagent session 的初始化差異
- **更新至**：`session.md`

### T12 — Main 入口與 Feature Flags
- **檔案**：`main.tsx`（4,690 行）
- **目標**：
  - Feature flag 的載入機制（`L$()` 函式對應）
  - `tengu_sotto_voce`、`tengu_bergotte_lantern` 等 flag 的判斷邏輯
  - MCP server 初始化流程
  - KAIROS 相關代碼（autonomous daemon mode）
- **更新至**：`model.md`、`tools.md`

---

## 優先級 4：補充分析（原始碼覆蓋缺口）

### T13 — 對話歷史管理
- **檔案**：`history.ts`（464 行）
- **目標**：
  - 對話歷史的資料結構
  - 訊息如何被截斷或壓縮（與 compact 機制的關係）
  - context window 管理邏輯
- **更新至**：`session.md`

### T14 — Context 結構
- **檔案**：`context.ts`（189 行）
- **目標**：
  - `ToolUseContext` 的完整欄位
  - `getAppState()` / `setAppState()` 的用途
  - Context 在 subagent 和 main thread 之間如何傳遞
- **更新至**：`tools.md`（Tool 系統章節）

### T15 — Task 類型定義
- **檔案**：`Task.ts`（125 行）、`tasks.ts`（39 行）
- **目標**：
  - Task 與 Agent 的關係（是否同義？）
  - Task 的狀態機
  - 與 AgentTool 的銜接方式
- **更新至**：`tools.md`（Agent 工具章節）

### T16 — Permission Mode 定義
- **檔案**：`utils/permissions/PermissionMode.ts`（141 行）
- **目標**：
  - 完整的 permission mode 類型定義
  - mode 之間的轉換規則
  - `isBypassPermissionsModeAvailable` 等 flag 的判斷邏輯
- **更新至**：`permissions.md`

---

## 分析記錄

| 任務 | 狀態 | 分析者 | 完成日期 | 輸出文件 |
|------|------|--------|---------|---------|
| T01 | ✅ 完成 | Claude | 2026-04-05 | `tools.md` |
| T02 | ✅ 完成 | Claude | 2026-04-05 | `prompt-schema.md` |
| T03 | ✅ 完成 | Claude | 2026-04-05 | `tools.md` |
| T04 | ✅ 完成 | Claude | 2026-04-05 | `permissions.md` |
| T05 | ✅ 完成 | Claude | 2026-04-06 | `session.md` |
| T06 | ✅ 完成 | Claude | 2026-04-06 | `tools.md` |
| T07 | ✅ 完成 | Claude | 2026-04-06 | `permissions.md` |
| T08 | ✅ 完成 | Claude | 2026-04-06 | `source-analysis/undercover.md` |
| T09 | ✅ 完成 | Claude | 2026-04-06 | `model.md` |
| T10 | ⬜ 待分析 | — | — | — |
| T11 | ⬜ 待分析 | — | — | — |
| T12 | ⬜ 待分析 | — | — | — |
| T13 | ⬜ 待分析 | — | — | — |
| T14 | ⬜ 待分析 | — | — | — |
| T15 | ⬜ 待分析 | — | — | — |
| T16 | ⬜ 待分析 | — | — | — |
