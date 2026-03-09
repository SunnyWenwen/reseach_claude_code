---
name: file-report
description: Scan a directory and produce a structured file report showing counts, types, and sizes. Use when the user asks to analyze a folder or summarize project files.
argument-hint: [directory-path]
allowed-tools: Glob, Grep, Bash(find *), Bash(du *), Bash(wc *)
---

# File Report

目標目錄：**$ARGUMENTS**（若未指定則使用當前目錄 `.`）

執行以下步驟產生報告：

## 步驟 1：列出所有檔案
使用工具列出目標目錄下所有檔案（包含子目錄）。

## 步驟 2：統計資訊
- 總檔案數
- 依副檔名分類計數
- 各檔案大小

## 步驟 3：輸出報告
以下列格式輸出：

```
============================
  File Report: <目錄>
============================
總檔案數：N
總大小：X KB

依類型分類：
  .md    : N 個
  .sh    : N 個
  ...（其他）

最大的 3 個檔案：
  1. path/to/file (X KB)
  2. ...

============================
```
