# Claude Code PPT 製作對話記錄

> 用途：明天繼續對話時的參考文件，記錄最終決策與內容結構

---

## 專案狀態

| 項目 | 說明 |
|------|------|
| 最終 PPT 產出 | `claude_code_full.pptx`（23 張） |
| 產生腳本 | `make_combined_ppt.py` |
| 執行方式 | `cd D:/project/test_claude_skill && .venv/Scripts/python3 make_combined_ppt.py` |

---

## PPT 整體結構（23 張）

### Part 1 — Why Claude Code 特別強

| # | 頁面 | 說明 |
|---|------|------|
| 1 | Cover | 標題頁 |
| 2 | Agenda | 三區塊：Part 1 Why / Part 2 How / Part 3 Take Away |
| 3 | Overall：4 個核心原因 | 2×2 格子：Agentic Loop / Context Management / Strong Tools / Strong Model |
| 4 | Reason 1：強 Agentic Loop | 不是 Autocomplete，而是 Iterative Problem Solver |
| 5 | Reason 2：強 Context Management | Loop 變長後，品質還能撐住 |
| 6 | Reason 3：強 Tools | 讓 Loop 每一步真正落地 |
| 7 | Reason 4：強 Model | 決定整個系統的推理上限 |
| 8 | 案例帶入 | 折扣碼重複使用 Bug，四步驟接力（Tools→Agentic Loop→Context Mgmt→Model） |

### Part 2 — How It Works 機制深入

| # | 頁面 | 重點 |
|---|------|------|
| 9  | Transition 過渡頁 | 銜接 Why → How |
| 10 | ReAct Loop | 推理→tool_use→tool_result 循環，批次平行，不含 tool_use 才停止 |
| 11 | 工具總覽 1/2（核心工具） | 唯讀探索 / 寫入 / 執行，標示 ★ = auto-allow |
| 12 | 工具總覽 2/2（系統工具） | Meta / 任務管理 / 規劃隔離 / IDE |
| 13 | Read / Grep / Glob | 比較表 + 接力使用範例（Glob→Grep→Read 找折扣碼驗證邏輯） |
| 14 | Edit vs Write | 比較表 + 使用原則 |
| 15 | Bash | **決策表**（何時用 Bash vs 專用工具）+ 執行特性 + 安全考量 |
| 16 | ToolSearch | Pre-loaded 9 個 / Deferred 17 個全列 + NotebookEdit 載入流程範例 |
| 17 | Agent Tool | 5 種 subagent_type 表格（含使用情境範例）+ 關鍵特性 |
| 18 | Skill 系統 | 兩種觸發方式 + allowed-tools vs Agent 硬隔離差異 |
| 19 | Task 任務管理工具 | TaskCreate/Get/List/Output/Stop + CronCreate + 背景任務流程範例 |
| 20 | Hooks | 5 個關鍵事件 + 四種執行類型 2×2（command/prompt/http/agent） |
| 21 | Permission 系統 | 分兩區：**軟性（Claude 訓練習慣）** vs **硬性（framework 規則）** |
| 22 | 資訊來源 | JSONL > 官方文件 > 原始碼，三種驗證方式 |

### Part 3 — Take Away

| # | 頁面 |
|---|------|
| 23 | Takeaways（6 條） |

---

## 關鍵設計決策

### 案例統一用「折扣碼重複使用」
- 選這個例子的原因：純後端、不需要前端知識、邏輯直觀
- 曾考慮過但放棄的例子：upload photo timeout（需懂前端）、軟刪除（術語不熟悉）

### 案例走訪順序：Tools → Agentic Loop → Context Mgmt → Model
- 不是時間順序，而是「由淺到深」
- Model 放最後的原因：「前面三步能 work，都是建立在 model 每一步判斷正確的基礎上」

### Agentic Loop vs ReAct 是兩個不同概念
- **Agentic Loop**：Claude Code 做事的方式（理解→行動→驗證），是工作方法論
- **ReAct**：底層 agent 架構（Reason→tool_use→tool_result→Reason），是技術實作

### Why 頁不提工具細節
- Why 頁只說概念與目的（四個 Reason）
- 工具的具體機制全部留到 Part 2（How）才介紹

### 工具總覽以功能分類，不以載入機制分類
- 改版前：分 Pre-loaded / Deferred
- 改版後：分 唯讀探索 / 寫入 / 執行 / Meta / 任務管理 / 規劃隔離 / IDE
- Pre-loaded vs Deferred 說明移到 ToolSearch 專頁

---

## Permission 系統的理解澄清

這是對話中釐清的重要概念，與簡報內容直接相關：

**軟性限制（Claude 訓練習慣）**
- Claude 在推理時自己判斷：「這件事超出範圍嗎？有非預期狀態嗎？指令夠清楚嗎？」
- 如果有疑慮 → 主動暫停詢問，不發出 tool call
- 無法透過設定改變，因為這是模型行為，不是 framework 規則

**硬性限制（framework 強制執行）**
- Auto-allow：唯讀工具直接放行
- Plan Mode：寫入/執行工具一律禁止
- Settings.json allow/deny：預先核准或封鎖特定命令

---

## 視覺風格規範

### 兩種風格混用
| 區域 | 風格 | 說明 |
|------|------|------|
| Part 1（Why，Slide 3-8） | 白底簡約 | 無 header bar，大字標題，LIGHT 背景框 |
| Part 2（How，Slide 10-22） | 藍色 header bar | `slide_header()` 函式，頂部藍色細條 |
| 過渡頁（Slide 9） | LIGHT 全頁底色 | 銜接兩種風格 |

### 顏色定義
```python
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
INK    = RGBColor(0x1A, 0x22, 0x2E)   # 深墨色，主要文字
MUTED  = RGBColor(0x55, 0x65, 0x7A)   # 灰色，次要說明
BLUE   = RGBColor(0x1D, 0x6F, 0xC8)   # Agentic Loop / 主色
GREEN  = RGBColor(0x05, 0x7A, 0x50)   # Context Management
ORANGE = RGBColor(0xB4, 0x5A, 0x00)   # Strong Tools
PURPLE = RGBColor(0x5B, 0x21, 0xB6)   # Strong Model
RED    = RGBColor(0xAA, 0x18, 0x18)   # 警告/安全/Permission 軟性
TEAL   = RGBColor(0x0E, 0x7A, 0x8E)   # Task 工具
GRAY   = RGBColor(0xE2, 0xE8, 0xF0)   # 分隔線/表頭底色
LIGHT  = RGBColor(0xF8, 0xFA, 0xFC)   # 淡底色框
```

---

## 技術環境

- Python 虛擬環境：`D:/project/test_claude_skill/.venv`
- 安裝套件：`python-pptx`
- 執行：`.venv/Scripts/python3 make_combined_ppt.py`
- 投影片尺寸：13.33 × 7.5 inches（16:9 寬螢幕）

---

## 尚未處理 / 可能繼續的方向

- [ ] 確認所有投影片在 PowerPoint 實際開啟後的排版是否正確（文字截斷？框框超邊界？）
- [ ] Takeaways 是否需要更新以反映新增的 Task / 資訊來源兩頁
- [ ] Agenda 頁的項目編號是否需要同步更新（目前是 01-08，但實際頁數已增加）
- [ ] 是否需要加上頁碼或 section indicator
