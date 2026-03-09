---
name: review-pr
description: Review a GitHub pull request for code quality, security, and best practices. Use when the user asks to review a PR, check a pull request, or audit code changes.
argument-hint: <pr-number> [focus-area]
disable-model-invocation: true
allowed-tools: Bash(gh *), Read, Grep, Glob
context: fork
agent: Explore
---

# PR Review: #$ARGUMENTS[0]

## 動態 PR 資訊（執行前自動注入）

- **PR Diff**: !`gh pr diff $ARGUMENTS[0]`
- **PR 基本資訊**: !`gh pr view $ARGUMENTS[0]`
- **變更檔案列表**: !`gh pr diff $ARGUMENTS[0] --name-only`
- **現有 Review 留言**: !`gh pr view $ARGUMENTS[0] --comments`

## 任務

審查 PR #$ARGUMENTS[0]，聚焦重點：**$ARGUMENTS[1]**（若未指定則全面審查）

執行以下步驟：

### 步驟 1：理解變更範圍
- 閱讀 PR 描述和變更摘要
- 確認此 PR 解決的問題或新增的功能

### 步驟 2：對照審查清單
參考 [checklist.md](checklist.md) 進行逐項檢查。
依照清單分類，逐一評估變更內容。

### 步驟 3：深度分析
對每個變更的檔案：
1. 閱讀完整修改內容
2. 使用 Grep 搜尋是否有相關測試覆蓋
3. 確認是否遵循專案現有的命名與架構慣例

### 步驟 4：產生報告
執行格式化腳本輸出結構化報告：
```bash
bash ${CLAUDE_SKILL_DIR}/scripts/generate-report.sh "$ARGUMENTS[0]" "${CLAUDE_SESSION_ID}"
```

### 步驟 5：輸出審查結果
按以下格式輸出：

```
## PR #$ARGUMENTS[0] 審查報告

### 整體評估
[APPROVE / REQUEST_CHANGES / COMMENT]

### 發現問題
- 🔴 嚴重：...
- 🟡 警告：...
- 🟢 建議：...

### 優點
- ...

### 總結
...
```

## 附加資源

- 完整審查清單：參閱 [checklist.md](checklist.md)
- 報告腳本說明：參閱 [scripts/generate-report.sh](scripts/generate-report.sh)
