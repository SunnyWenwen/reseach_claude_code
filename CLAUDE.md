# CLAUDE.md

## Claude Code 機制知識庫

當對話中討論到任何 Claude Code 的機制（包括但不限於：工具載入、ToolSearch、Skill 系統、Session JSONL 格式、Hooks、context 管理等），請執行以下步驟：

1. 讀取 `analysis.md`，確認該機制是否已有記錄
2. 若未記錄或記錄不完整，將新內容更新進 `analysis.md`
3. 更新時維持現有的文件結構與格式風格

## 以實際記錄為準

所有關於 Claude Code 機制的描述，**必須以真實的 session JSONL 內容為依據**，不得僅憑推測或理論描述。

- 若有對應的 JSONL 檔案，優先使用 `/session-analyze <path>` 驗證實際行為
- 發現描述與 JSONL 記錄不符時，以 JSONL 記錄為準並更新 `analysis.md`
- 在 `analysis.md` 中記錄機制時，盡量附上觀察來源（例如：「來源：`5713c20a...jsonl`」）
- JSONL 無法解釋的機制，可嘗試去 Claude Code 原始碼中尋找對應邏輯（見下方「Claude Code 程式碼位置」）

## 專案結構

- 工作目錄：`D:\project\test_claude_skill`
- JSONL session 記錄：`D:\project\test_claude_skill\Claude_Code_conversation\`（手動從系統 session 記錄複製，非即時，查最新 session 請直接去系統 session 記錄）
- 系統 session 記錄：`C:\Users\User\.claude\projects\d--project-test-claude-skill\`（最新、最準）
- 機制分析文件：`D:\project\test_claude_skill\analysis.md`

## Claude Code 程式碼位置

Claude Code 是單一 Windows 執行檔（Node.js 打包），內嵌 minified JS bundle，**沒有加密**，可用 `grep`/`strings` 搜尋原始碼邏輯。

- 執行檔：`C:\Users\User\.local\share\claude\versions\{version}`（例如 `2.1.72`，約 237MB）
- 資料與設定：`C:\Users\User\.claude\`（session 記錄、settings 等）
- **不可修改**上述任何檔案，避免損壞 Claude Code 本身

## session-analyze skill 維護規則

使用 `/session-analyze` 分析 JSONL 時，若發現輸出中有**未被處理的記錄類型或欄位**（例如新的 `progress` 子類型、未知的 record type、或顯示異常的欄位），須同步更新：

1. `.claude/skills/session-analyze/scripts/parse-session.py`：加入對應的解析邏輯
2. `analysis.md`：補充該記錄類型的機制說明與來源
