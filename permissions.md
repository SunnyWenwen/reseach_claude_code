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

## Auto Mode 分類器（TRANSCRIPT_CLASSIFIER / Yolo Classifier）

來源：外流原始碼 2.1.88 `utils/permissions/yoloClassifier.ts`、`utils/permissions/bashClassifier.ts`

### bashClassifier.ts：ANT-ONLY 功能，外部版本為 stub

```ts
// Stub for external builds - classifier permissions feature is ANT-ONLY
export function isClassifierPermissionsEnabled(): boolean {
  return false
}
```

`BASH_CLASSIFIER` feature 在外部版本中完全禁用，所有函式回傳 disabled/空值。外部用戶不會觸發此分類器。

### yoloClassifier.ts：Auto Mode 的核心分類器

功能：在 `auto` 模式下，當工具呼叫需要確認時，用獨立的 API 呼叫（side query）判斷是否允許執行。

**架構（兩階段 XML 分類器）**：

```
transcriptHistory + action → buildYoloSystemPrompt() → sideQuery（獨立 API 呼叫）
    ↓
Stage 1（fast）: max_tokens=256, stop_sequences
    → shouldBlock? yes → done
    → no → Stage 2（thinking）: 用 extended thinking 深入分析
    → 最終 shouldBlock: boolean
```

- System prompt 從 `.txt` 文字檔載入（`auto_mode_system_prompt.txt` + `permissions_external.txt` / `permissions_anthropic.txt`）
- 使用 `cache_control` 在 action block 上設定快取，stage 1/2 共享 prefix → stage 2 可命中 cache
- 空輸入（`toCompact()` 回傳 `''`）直接允許，不呼叫 API

**使用者可自訂分類器規則**（`settings.autoMode`）：

```json
{
  "autoMode": {
    "allow": ["npm test", "git push"],
    "soft_deny": ["curl -X DELETE"],
    "environment": ["This is a CI environment", "Only read-only operations are expected"]
  }
}
```

| 欄位 | 說明 |
|------|------|
| `allow` | 自動允許的命令描述（白名單） |
| `soft_deny` | 偏向拒絕但可被 context 覆蓋（軟性黑名單） |
| `environment` | 提供環境背景，影響分類器判斷 |

查看預設規則：`claude auto-mode defaults`

---

## Bash 工具的權限匹配邏輯

來源：外流原始碼 2.1.88 `utils/permissions/shellRuleMatching.ts`（已交叉確認 binary 2.1.72 逆向結論）

### ruleContent 的三種類型（`parsePermissionRule()`）

| 格式 | 類型 | 說明 |
|------|------|------|
| `git:*` | `prefix`（legacy） | 以 `:*` 結尾，提取前綴做前綴比對；向後相容語法 |
| `git status` | `exact` | 完全相符，無萬用字元 |
| `git *` | `wildcard` | 含未跳脫的 `*`，轉為 regex 比對 |

判斷順序：`prefix`（`:*` 結尾）→ `wildcard`（含 `*`）→ `exact`（其餘）

### prefix 規則的匹配條件

`Bash(git:*)` → 提取 prefix = `git`，命令符合以下任一即通過：

```
command === "git"
command.startsWith("git ")
command === "xargs git"
command.startsWith("xargs git ")
```

### wildcard 規則的匹配邏輯（`matchWildcardPattern()`）

- `*` 轉成 regex `.*`（含 dotAll，可跨行）
- `\*` → literal `*`，`\\` → literal `\`
- 特殊：`git *`（尾端 ` *` 且唯一萬用字元）→ trailing space+args 設為 optional，即 `git *` 同時匹配 `git` 和 `git add`

```
Bash(git *)  ← 匹配 "git"、"git add"、"git commit -m 'msg'"
Bash(npm * install)  ← 不做 optional 處理（多個萬用字元）
```

### 複合命令永遠不匹配 prefix 規則（安全設計）

來源：binary 2.1.72 逆向確認（minified `iCA()`）

```js
// 含 &&, ||, ;, | 的複合命令直接跳過 prefix 規則
case "prefix":
  if (isCompoundCommand(command)) return false;
```

**這是防越獄的刻意設計**：

```bash
# 設定：Bash(git:*)
git status && rm -rf /important-dir   # 前綴合法，後半危險 → 強制詢問
```

強制複合命令永遠需要額外確認，確保 prefix 規則只授權「單一操作」。

### rule content 的 escaping

規則格式為 `ToolName(content)`，若 content 本身含括號需跳脫：

```
Bash(python -c "print\(1\)")  ← 匹配含括號的命令
```

`escapeRuleContent()` / `unescapeRuleContent()` 負責往返轉換（先跳脫 `\` 再跳脫 `()`）。

### 仍會被詢問的情況（即使已設定 allow 規則）

1. **複合命令**：`ls ... && echo ... && ls ...`（`&&`/`||`/`;`/`|` 串接）
2. **解決方法**：改用 `"Bash"` 允許所有 Bash 指令，或接受上述限制

---

## 危險命令模式（DANGEROUS_BASH_PATTERNS）

來源：外流原始碼 2.1.88 `utils/permissions/dangerousPatterns.ts`

這些 pattern 被用於 `isDangerousBashPermission()` 判斷：當 allow 規則的前綴是這些直譯器/shell/工具時，在 `auto` 模式入口時會被剝除（因為允許這些前綴等於允許任意程式碼執行）。

### DANGEROUS_BASH_PATTERNS（所有用戶）

**直譯器：** `python`, `python3`, `python2`, `node`, `deno`, `tsx`, `ruby`, `perl`, `php`, `lua`

**套件執行器：** `npx`, `bunx`, `npm run`, `yarn run`, `pnpm run`, `bun run`

**Shells：** `bash`, `sh`, `zsh`, `fish`

**特殊：** `eval`, `exec`, `env`, `xargs`, `sudo`, `ssh`

### ANT-ONLY 追加（`USER_TYPE === 'ant'`）

```
fa run, coo（cluster code launcher）,
gh, gh api,
curl, wget,
git,
kubectl, aws, gcloud, gsutil
```

> **設計說明（原始碼注釋）**：這些是 Anthropic 內部依據 sandbox dotfile 數據判定的「empirical-risk」命令，並非普適的「此工具不安全」聲明，外部用戶不受影響。

---

## 權限決策完整流程（`hasPermissionsToUseToolInner`）

來源：外流原始碼 2.1.88 `utils/permissions/permissions.ts` `hasPermissionsToUseToolInner()`（lines 1158–1319）

### Inner 函式（步驟 1–3）

```
1a. denyRules 整工具比對 → deny（立即）
1b. askRules 整工具比對 → ask（除非 sandbox auto-allow）
1c. tool.checkPermissions(input) → 工具自身的 content-level 判斷
      （例：BashTool 在這裡比對 prefix/wildcard/exact 規則）
1d. 工具回傳 deny → deny
1e. tool.requiresUserInteraction() && 'ask' → ask（強制人工確認）
1f. content-specific ask rule → ask（繞不過，即使 bypassPermissions）
1g. safetyCheck（.git/ .claude/ .vscode/ shell configs）→ ask（繞不過）
2a. bypassPermissions 模式 → allow
2b. allowRules 整工具比對 → allow
3.  passthrough → ask（預設）
```

### Outer 函式（後處理，`hasPermissionsToUseTool`）

Inner 回傳 `ask` 後，outer 再做以下處理：

| 條件 | 結果 |
|------|------|
| mode = `dontAsk` | `ask` → `deny`（直接拒絕，不詢問） |
| mode = `auto` 且 feature `TRANSCRIPT_CLASSIFIER` 啟用 | 進入 **auto mode 分類器流程** |
| mode = `plan` 且 `autoModeActive` | 同上 |
| shouldAvoidPermissionPrompts（headless）| 執行 PermissionRequest hook，hook 無回應 → `deny` |

### Auto Mode 分類器流程（`TRANSCRIPT_CLASSIFIER`）

在 `ask` 結果進入 auto mode 時，有三條分支（按優先順序）：

```
Fast-path 1：acceptEdits 模式下會允許（非 Agent/REPL 工具）→ allow，不呼叫分類器
Fast-path 2：工具在 safe tool allowlist → allow，不呼叫分類器
Classifier：呼叫 classifyYoloAction()（yoloClassifier）→ shouldBlock=false → allow / shouldBlock=true → deny
```

分類器例外：
- `classifierResult.transcriptTooLong` → 回退到人工確認（headless 則 AbortError）
- `classifierResult.unavailable`（API error）→ `tengu_iron_gate_closed` flag 控制 fail-closed vs 允許

---

## 規則來源（PermissionRuleSource）

來源：外流原始碼 2.1.88 `utils/permissions/permissions.ts`（line 109–114）

| 來源 | 說明 |
|------|------|
| `localSettings` | 專案本地 `.claude/settings.local.json` |
| `projectSettings` | 專案 `.claude/settings.json`（提交至 repo） |
| `userSettings` | 全域 `~/.claude/settings.json` |
| `flagSettings` | Feature flag 注入的規則 |
| `policySettings` | 組織/企業政策規則 |
| `cliArg` | CLI 啟動參數 `--allow-permissions` 等 |
| `command` | 對話中動態添加（`/permissions` 指令） |
| `session` | 單次 session 臨時規則 |

優先順序：deny 規則在 allow 規則之前檢查（步驟 1a > 步驟 2b）。

---

## 工具名稱的歷史別名（Legacy Tool Name Aliases）

來源：外流原始碼 2.1.88 `utils/permissions/permissionRuleParser.ts`

| 舊名稱 | 現名稱 | 說明 |
|------|------|------|
| `Task` | `Agent` | Agent 工具 |
| `KillShell` | `TaskStop` | 停止工具執行 |
| `AgentOutputTool` | `TaskOutput` | Agent 輸出工具 |
| `BashOutputTool` | `TaskOutput` | 同上 |
| `Brief` | （KAIROS feature flag 決定） | 內部 KAIROS 模式 |

permission rules 中的舊名稱會自動正規化為現名稱（`normalizeLegacyToolName()`）。

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

---

## Permission Mode 完整定義（T16）

來源：外流原始碼 2.1.88 `utils/permissions/PermissionMode.ts`（141 行）

### 完整 Mode 清單

| mode | title | symbol | color | external | 說明 |
|------|-------|--------|-------|----------|------|
| `default` | Default | — | text | `default` | 預設，每個操作依規則決定是否詢問 |
| `plan` | Plan Mode | （PAUSE_ICON） | planMode | `plan` | 規劃模式，不執行破壞性操作 |
| `acceptEdits` | Accept edits | ⏵⏵ | autoAccept | `acceptEdits` | 自動接受檔案編輯，不詢問 |
| `bypassPermissions` | Bypass Permissions | ⏵⏵ | error | `bypassPermissions` | 繞過所有權限檢查（危險） |
| `dontAsk` | Don't Ask | ⏵⏵ | error | `dontAsk` | 不詢問，全部自動執行（危險） |
| `auto` | Auto mode | ⏵⏵ | warning | `default` | **ANT-ONLY**；TRANSCRIPT_CLASSIFIER feature-gated；外部對應 `default` |
| `bubble` | — | — | — | （排除） | **ANT-ONLY**；未在 PERMISSION_MODE_CONFIG 中，僅在 `isExternalPermissionMode()` 中提及 |

### External vs Internal Modes

`ExternalPermissionMode` = 外部可見模式（排除 `auto` 和 `bubble`）：

```ts
export function isExternalPermissionMode(mode: PermissionMode): mode is ExternalPermissionMode {
  if (process.env.USER_TYPE !== 'ant') return true  // 外部用戶全部都是 external mode
  return mode !== 'auto' && mode !== 'bubble'
}
```

`toExternalPermissionMode(mode)`: 將 internal mode 映射到 external（`auto` → `default`）。

### Zod Schema

```ts
export const permissionModeSchema = lazySchema(() => z.enum(PERMISSION_MODES))
export const externalPermissionModeSchema = lazySchema(() => z.enum(EXTERNAL_PERMISSION_MODES))
```

Lazy schema 避免循環 import 問題。

### 工具函式

| 函式 | 說明 |
|------|------|
| `permissionModeFromString(str)` | 解析字串，未知值退回 `default` |
| `permissionModeTitle(mode)` | 完整標題（如 "Plan Mode"） |
| `permissionModeShortTitle(mode)` | 短標題（如 "Plan"） |
| `permissionModeSymbol(mode)` | UI 符號（如 "⏵⏵"） |
| `getModeColor(mode)` | UI 顏色鍵 |
| `isDefaultMode(mode)` | mode 是 `default` 或 `undefined` |
