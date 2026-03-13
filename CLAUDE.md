# CLAUDE.md

## 專案說明

本專案專門研究 Claude Code 的內部機制與行為，所有工作圍繞著理解、記錄、驗證 Claude Code 的運作方式。

## Claude Code 機制知識庫

當對話中討論到任何 Claude Code 的機制（包括但不限於：工具載入、ToolSearch、Skill 系統、Session JSONL 格式、Hooks、context 管理等），請執行以下步驟：

1. 讀取 `analysis.md`（索引），找到對應的子檔案
2. 讀取對應子檔，確認該機制是否已有記錄
3. 若未記錄或記錄不完整，將新內容更新進對應子檔
4. 更新時維持現有的文件結構與格式風格

機制分析文件：
- `analysis.md`：索引
- `tools.md`：工具系統（Agentic Loop、ToolSearch、Skill、Agent、Hooks）
- `permissions.md`：權限系統（IPC、Bash 匹配邏輯）
- `session.md`：Session JSONL 格式
- `model.md`：模型行為（Extended Thinking）

## 機制驗證方法

驗證 Claude Code 機制時，依以下優先順序使用三種方式，並在文件中標註來源：

### 1. 真實 session JSONL（最優先）

實際執行的行為記錄，最可信。

- 優先使用 `/session-analyze <path>` 解析 JSONL
- 發現描述與 JSONL 記錄不符時，**以 JSONL 為準**並更新對應子檔
- 記錄時附上來源（例如：「來源：`ef82a45d...jsonl`」）

### 2. 官方文件（次優先）

用於確認設計意圖與公開行為，快速查閱見 [`docs-reference.md`](docs-reference.md)。

- 官方文件索引：`https://code.claude.com/docs/llms.txt`（base URL：`https://code.claude.com/docs/en/`）
- 記錄時附上頁面名稱（例如：「來源：官方文件 `how-claude-code-works`」）

### 3. Claude Code 原始碼（找不到或太細的機制才用）

可在 237MB 執行檔中搜尋 minified JS bundle（無加密）。

- 執行檔位置：`C:\Users\User\.local\share\claude\versions\{version}`
- 搜尋方式：Python regex 或 `strings` + grep（見「Claude Code 程式碼位置」）
- 記錄時附上函式名稱或特徵字串（例如：「來源：binary `Nc

 函式`」）

## 專案結構

- 工作目錄：`D:\project\test_claude_skill`
- JSONL session 記錄：`D:\project\test_claude_skill\Claude_Code_conversation\`（手動從系統 session 記錄複製，非即時，查最新 session 請直接去系統 session 記錄）
- 系統 session 記錄：`C:\Users\User\.claude\projects\d--project-test-claude-skill\`（最新、最準）
- 機制分析文件：`D:\project\test_claude_skill\analysis.md`（索引）及同目錄下的 `tools.md`、`permissions.md`、`session.md`、`model.md`

## Claude Code 程式碼位置

Claude Code 是單一 Windows 執行檔（Node.js 打包），內嵌 minified JS bundle，**沒有加密**，可用 `grep`/`strings` 搜尋原始碼邏輯。

- 執行檔：`C:\Users\User\.local\share\claude\versions\{version}`（例如 `2.1.72`，約 237MB）
- 資料與設定：`C:\Users\User\.claude\`（session 記錄、settings 等）
- **不可修改**上述任何檔案，避免損壞 Claude Code 本身

## session-analyze skill 維護規則

使用 `/session-analyze` 分析 JSONL 時，若發現輸出中有**未被處理的記錄類型或欄位**（例如新的 `progress` 子類型、未知的 record type、或顯示異常的欄位），須同步更新：

1. `.claude/skills/session-analyze/scripts/parse-session.py`：加入對應的解析邏輯
2. 對應子檔（通常是 `session.md`）：補充該記錄類型的機制說明與來源
