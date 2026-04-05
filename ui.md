# Claude Code Web UI 行為

## Conversation Metadata（branch/PR 對應關係）

來源：官方 issue anthropics/claude-code#11176

### 機制

Claude Code Web 在 **conversation 初始化時**將 branch/PR 資訊寫入 metadata，整個 session 期間**不可變**：

```
conversation 建立
    ↓
metadata 固定（branch name + PR number）
    ↓
整個 session 期間不更新
```

### Create PR vs View PR 按鈕邏輯

| 狀態 | 按鈕顯示 |
|------|---------|
| conversation 尚未關聯 PR | **Create PR** |
| conversation 已關聯 PR（不論 open/merged/closed） | **View PR** |

一旦 PR 被建立，metadata 鎖定，即使該 PR 已 merge，UI 仍顯示「View PR」，不會切回「Create PR」。

### 已知限制

| 問題 | 說明 |
|------|------|
| PR merge 後無法再開新 PR | metadata 不可更新，View PR 永遠指向舊 PR |
| 手動在 GitHub 建立 PR | conversation 無法偵測，View PR 仍不顯示 |
| branch rename 後 | 按鈕失效（metadata 指向舊 branch name） |

相關 issue：
- [anthropics/claude-code#11176](https://github.com/anthropics/claude-code/issues/11176)：請求增加讓 Claude 能更新 conversation metadata 的 tool（2025 開，目前未解）
- [anthropics/claude-code#30021](https://github.com/anthropics/claude-code/issues/30021)：iOS 上「Create PR」按鈕消失 bug

### 解法

| 情況 | 解法 |
|------|------|
| 同一 session 要開第二個 PR | 去 GitHub 網頁手動開 |
| 需要 Create PR 按鈕 | 開新的 Claude Code conversation |

---

## Create PR 按鈕消失 Bug（iOS）

來源：官方 issue anthropics/claude-code#30021

- **平台**：Claude Code iOS
- **症狀**：push 後 UI 有空容器但按鈕未渲染
- **狀態**：open（62 upvotes）
