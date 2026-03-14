# PPT 製作進度交接

## 基本資訊

- **檔案**：`agent_architecture.pptx`（同目錄下）
- **腳本**：`make_ppt.py`（同目錄下，修改內容後跑 `python3 make_ppt.py` 重新產出）
- **Branch**：`claude/review-project-3kUxh`
- **總頁數**：13 張

---

## 已完成的內容

### 投影片結構

| # | 標題 | 說明 |
|---|------|------|
| 1 | 封面 | Claude Code Internal Mechanism Deep Dive，作者 Hsiang-Wen |
| 2 | Agenda | 6 大主題 |
| 3 | ReAct Loop | 基本運作方式、批次 tool call、終止條件 |
| 4 | 工具總覽 (1/2) | Pre-loaded 9 個工具，每個附一句說明 + 權限標示 |
| 5 | 工具總覽 (2/2) | Deferred 16 個 + MCP 2 個，每個附一句說明 |
| 6 | Claude Code 怎麼寫 Code | 探索→修改→驗證流程，每步工具的設計優勢（why it's top agent） |
| 7 | Pre-loaded vs Deferred vs MCP | 三種載入方式對比 + ToolSearch 說明 |
| 8 | Read / Edit / Write vs Bash | 差異對比表（7 個面向） |
| 9 | Skill 系統 | 兩種觸發方式、allowed-tools 軟性限制 vs Agent 硬性隔離 |
| 10 | Agent Tool | 5 種 subagent_type 列表 + 關鍵特性 |
| 11 | Hooks | 21 種事件 + command / prompt 兩種 hook 類型 |
| 12 | Permission 系統 | 兩個層次 + Bash 匹配邏輯 + 5 種 Permission Modes |
| 13 | Takeaways | 6 點核心結論 |

### 視覺風格

- 白底、藍色頂部細條作為 accent
- 工具名稱依功能色碼：唯讀藍、寫入綠、執行橘、規劃紫、任務紅、互動灰、MCP 青
- 無複雜裝飾，條列式為主，表格用細灰線分隔

---

## 討論中確認的設計決策

1. **工具總覽拆兩頁**：原本是依功能分群的一頁，後來改為「Pre-loaded（附說明）」＋「Deferred+MCP（附說明）」兩頁，每個工具一句介紹
2. **作者**：Hsiang-Wen
3. **語言**：中文內容，英文工具名稱保留原文

---

## 可能的後續動作

- 調整任何投影片的文字或版面
- 新增更多技術細節（例如 session JSONL 格式、model 行為）
- 修改視覺風格（字型、配色）
- 匯出為 PDF

---

## 修改方式

```bash
# 修改 make_ppt.py 後重新產出
python3 make_ppt.py

# commit & push
git add agent_architecture.pptx make_ppt.py
git commit -m "..."
git push -u origin claude/review-project-3kUxh
```
