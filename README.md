# 用 Claude Code 研究 Claude Code

這個專案用 Claude Code 自身作為研究工具，深入分析 Claude Code 的內部機制。
驗證機制的方法有三種：session JSONL(claude code的上下文log)、官方文件、binary 原始碼搜尋，探索機制細節寫在 [`CLAUDE.md`](CLAUDE.md)內。

---

## 前置條件

- [Claude Code](https://claude.ai/code) 已安裝並登入
- Python 3.x

---

## 專案結構

```
.
├── analysis.md          # 索引：所有機制文件的導覽，從這裡開始
├── tools.md             # 工具系統（Agentic Loop、ToolSearch、Skill、Agent、Hooks）
├── permissions.md       # 權限系統（IPC、Bash 匹配邏輯、Permission Modes）
├── session.md           # Session JSONL 格式（記錄類型、progress 子類型、checkpointing）
├── model.md             # 模型行為（Extended Thinking、System Prompt 結構）
├── prompt-schema.md     # System Prompt 與工具 Schema 原文
├── docs-reference.md    # 官方文件已讀頁面索引與重點
└── .claude/
    └── skills/
        └── session-analyze/  # 分析 JSONL session log 的 skill
```

---

## Quick Start

建議在vscode底下操作

安裝好 Claude Code 與 Python 後，在這個目錄啟動 Claude Code，直接問問題即可：

```bash
claude
```

Claude Code 會自動讀取 [`CLAUDE.md`](CLAUDE.md) 的指引，結合現有的機制分析文件、`/session-analyze` skill 與 binary 搜尋腳本來回答問題。

**範例問題：**
- 「Bash 的 allow 規則是怎麼匹配的？」
- 「幫我分析這個 session JSONL」
- 「Pre-loaded 和 Deferred 工具的差異是什麼？」
- 「搜尋 binary，看看 isConcurrencySafe 的邏輯」

> **注意**：[`CLAUDE.md`](CLAUDE.md) 內有寫死的路徑，clone 後請先調整以下兩個段落再開始使用：
> - **`## 專案結構`**：工作目錄、JSONL session 記錄路徑、系統 session 記錄路徑
> - **`## Claude Code 程式碼位置`**：執行檔路徑（`C:\Users\User\...`）、資料與設定路徑

---

## 注意事項

- [`CLAUDE.md`](CLAUDE.md) 是寫給 Claude Code 看的專案指令，定義了機制探索的規則：如何更新分析文件、驗證優先順序、skill 維護規則等。有興趣了解如何引導 Claude Code 做研究的可以參考。
- 若想把某個 session 的上下文貼給 Claude Code 分析：
  1. 到 `CLAUDE.md → ## 專案結構` 中的「系統 session 記錄」路徑，找到想分析的 `.jsonl`
  2. 複製到「JSONL session 記錄」路徑（`Claude_Code_conversation/`）
  3. 在 Claude Code 輸入框用 `@` 標註該檔案，請 Claude Code 分析（Claude Code 會自動結合 `/session-analyze` skill 進行解析）
  4. 分析結果會存放在 `conversation_for_human/`
- 研究過程中發現的機制會自動記錄進分析文件（`tools.md`、`permissions.md` 等），下次提問時 Claude Code 會直接參考這些既有記錄。文件分類方式見 [`analysis.md`](analysis.md)
- [`docs-reference.md`](docs-reference.md) 是爬過一遍官網文件後整理的目錄索引。需要查閱官方文件時，Claude Code 會先看這份索引找到對應頁面，再透過 WebSearch 取得最新內容

