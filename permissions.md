# Claude Code 權限系統

## 權限的兩個層次

Claude Code 有兩種不同性質的「確認」機制：

| 層次 | 控制方式 | 可否關閉 |
|------|---------|---------|
| **工具權限**（permission system） | `permissions.allow` / `permissions.deny` | 可透過設定關閉 |
| **判斷性確認**（Claude 自行判斷） | 無法設定，由 Claude 根據操作風險決定 | 不可關閉 |

判斷性確認的典型情境：操作超出請求範圍、發現非預期狀態、請求模糊需釐清。

---

## permissions.allow 設定格式

設定於 `settings.local.json`（專案）或 `~/.claude/settings.json`（全域）：

```json
{
  "permissions": {
    "allow": [
      "Edit",
      "Bash(git:*)",
      "WebFetch(domain:docs.anthropic.com)",
      "Skill(session-analyze)"
    ],
    "deny": [
      "Bash(rm -rf:*)"
    ]
  }
}
```

### 規則格式

| 格式 | 範例 | 說明 |
|------|------|------|
| 工具名稱 | `"Edit"` | 允許該工具的所有呼叫 |
| 工具 + 參數限制 | `"Bash(git:*)"` | 允許以 `git` 開頭的 Bash 命令 |
| 工具 + domain 限制 | `"WebFetch(domain:example.com)"` | 允許特定 domain 的 WebFetch |
| 工具 + skill 限制 | `"Skill(session-analyze)"` | 允許特定 skill |

---

## 權限確認的內部通訊（IPC）

權限確認對話框**不走 JSONL**，而是透過進程間通訊（IPC）：

```
Claude 呼叫工具
    ↓
發送 permission_request（IPC）← 不進 JSONL
    ↓
使用者在 UI 確認或拒絕        ← 不進 JSONL
    ↓
收到 permission_response（IPC）← 不進 JSONL
    ↓
TOOL_RESULT 寫入 JSONL         ← 只有這步留下記錄
```

JSONL 無法還原「是否曾詢問過確認」。

來源：`ef82a45d...jsonl`（確認 JSONL 無記錄）

### permission_request 結構（Claude → UI）

```json
{
  "type": "permission_request",
  "request_id": "...",
  "agent_id": "...",
  "tool_name": "Edit",
  "tool_use_id": "...",
  "description": "...",
  "input": { ...工具參數... },
  "permission_suggestions": []
}
```

`permission_suggestions`：UI 顯示的建議 allow 規則選項（Claude Code 根據工具和參數自動生成）。

### permission_response 結構（UI → Claude）

```json
// 允許
{
  "type": "permission_response",
  "request_id": "...",
  "subtype": "success",
  "response": {
    "updated_input": {...},
    "permission_updates": [...]
  }
}

// 拒絕
{
  "type": "permission_response",
  "request_id": "...",
  "subtype": "error",
  "error": "Permission denied"
}
```

| 欄位 | 說明 |
|------|------|
| `updated_input` | 使用者可在確認前修改工具的輸入參數 |
| `permission_updates` | 允許後寫回 `settings.json` 的規則 |

來源：`6370316b...jsonl` tool-results（Claude Code JS bundle 逆向）

---

## Bash 工具的權限匹配邏輯

來源：Claude Code 執行檔逆向（`2.1.72`，函數 `Nc$`、`IKL`、`aVH`）

### ruleContent 的三種類型（函數 `IKL`）

| 格式 | 類型 | 說明 |
|------|------|------|
| `git:*` | `prefix`（legacy） | 命令以 `git` 開頭 |
| `git status` | `exact` | 完全相符 |
| `git *` | `wildcard` | glob/wildcard 匹配 |

### prefix 規則的匹配條件

`Bash(git:*)` → 提取 prefix = `git`，命令符合以下任一即通過：

```
command === "git"
command.startsWith("git ")
command === "xargs git"
command.startsWith("xargs git ")
```

### 複合命令永遠不匹配 prefix 規則（安全設計）

```js
// 判斷是否為複合命令（含 &&, ||, ;, |）
K.set(command, iCA(command).length > 1)

case "prefix":
  if (K.get(w)) return false;  // 複合命令直接跳過
```

**這是防越獄的刻意設計**：若複合命令也能匹配 prefix 規則，攻擊者可在合法命令後接危險操作：

```bash
# 設定：Bash(git:*)
git status && rm -rf /important-dir   # 前綴合法，後半危險
```

強制複合命令永遠需要額外確認，確保 prefix 規則只授權「單一操作」。

### Windows 路徑的注意事項

`bI()` 用 bash tokenizer 解析命令，遇到 Windows 反斜線路徑（如 `ls 'C:\Users\...'`）可能解析失敗，觸發不同的判斷路徑。

### 仍會被詢問的情況（即使已設定 allow 規則）

1. **複合命令**：`ls ... && echo ... && ls ...`（`&&`/`||`/`;`/`|` 串接）
2. **Windows 路徑**：可能因 tokenizer 解析失敗
3. **解決方法**：改用 `"Bash"` 允許所有 Bash 指令，或接受上述限制

---

## Permission Modes（全域操作模式）

與 `permissions.allow` 規則不同，Permission Mode 是**整體操作模式**，影響所有工具的行為。

來源：binary `2.1.72`，`EXTERNAL_PERMISSION_MODES` / `INTERNAL_PERMISSION_MODES`

### 模式清單

| Mode | 對外暴露 | 說明 |
|------|---------|------|
| `default` | ✓ | 預設模式，需要確認的都會詢問 |
| `acceptEdits` | ✓ | **Accept Edits 模式**：自動接受所有檔案編輯（Edit/Write/NotebookEdit），但 Bash 等副作用指令仍需確認 |
| `bypassPermissions` | ✓ | 跳過所有工具權限確認（危險） |
| `dontAsk` | ✓ | 自動**拒絕**所有未預先允許的操作（不詢問，直接 deny）；與 `bypassPermissions`（跳過所有確認，直接 allow）相反 |
| `plan` | ✓ | Plan 模式（僅規劃，限制實際執行） |
| `auto` | 內部 | 自動模式（`claude -p` 等非互動場合） |

### acceptEdits vs permissions.allow 的差異

| | `acceptEdits` 模式 | `permissions.allow` 規則 |
|--|------------------|------------------------|
| 作用範圍 | 全域，影響所有 session | 特定工具/命令 |
| 設定粒度 | 粗（檔案操作 vs 副作用） | 細（可到單一命令） |
| 持久性 | 可設為 session 預設或隨時切換 | 寫入 settings.json 持久 |
| Bash 指令 | 仍需確認 | 可單獨允許特定命令 |

### 設定方式

- CLI 啟動時：`claude --permission-mode acceptEdits`
- 互動中：UI 模式切換按鈕（status bar 符號 `⏵⏵`）

---

## 官方安全機制補充

來源：官方文件 https://code.claude.com/docs/en/security.md

### 額外保護

| 機制 | 說明 |
|------|------|
| **寫入範圍限制** | Claude 只能寫入啟動時的工作目錄及其子目錄；可讀取範圍之外的檔案，但不能修改 |
| **命令黑名單** | `curl`、`wget` 等高風險命令預設封鎖 |
| **注入偵測** | 即使命令已在 allowlist，疑似 injection 的 Bash 命令仍強制詢問 |
| **Fail-closed** | 無匹配規則的命令一律需要確認（不預設允許） |
| `/sandbox` | 啟用沙箱模式：檔案系統 + 網路隔離 |
