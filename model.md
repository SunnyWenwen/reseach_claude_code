# Claude Code 模型行為

## Extended Thinking（THINKING 機制）

### 什麼是 THINKING

Claude 在回應前的內部推理過程，以 `thinking` 類型的 content block 記錄於 JSONL：

```json
{
  "type": "thinking",
  "thinking": "...",
  "signature": "EpYCCkYI..."
}
```

- `thinking`：推理文字內容（加密模式下為空字串）
- `signature`：加密簽名，驗證 thinking 真實性，防止偽造

### 兩種狀態

| 狀態 | `thinking` 欄位 | `signature` 欄位 | 對應模式 |
|------|----------------|----------------|---------|
| 明文 | 有內容 | 有 | 舊版 `enabled` |
| 加密 | 空字串 `""` | 有（且較長） | 新版 `adaptive`（預設） |

來源：`5713c20a...jsonl`（明文）vs `6370316b...jsonl`（加密）；binary 分析確認

### Thinking 模式（來源：binary `2.1.72`）

| type | 說明 |
|------|------|
| `disabled` | 關閉 thinking |
| `enabled` | 舊版，已棄用，thinking 明文回傳 |
| `adaptive` | 新版預設，server-side 處理，thinking 加密 |

Beta flags：
- `interleaved-thinking-2025-05-14`（舊版）
- `adaptive-thinking-2026-01-28`（新版，目前使用）

### 設定方式

**`alwaysThinkingEnabled`**（存於 `settings.json`）：

| 值 | 行為 |
|----|------|
| 缺席或 `true` | thinking 自動啟用（預設） |
| `false` | thinking 停用 |

也可在 Claude Code UI Settings 對話框切換（label: `Thinking mode`）。

**`showThinkingSummaries`**：控制是否在 transcript view（`ctrl+o`）顯示 thinking 摘要，預設 `false`。

詳見 [`prompt-schema.md`](prompt-schema.md)。
