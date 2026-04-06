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

---

## Feature Flags 與 Main 入口（T12）

來源：外流原始碼 2.1.88 `main.tsx`（4,690 行）

### 兩種 Feature Flag 機制

| 機制 | 用途 | 函式 |
|------|------|------|
| `feature()` from `bun:bundle` | **編譯期** dead code elimination；`true`/`false` 常量折疊 | `feature('KAIROS')`, `feature('BG_SESSIONS')` 等 |
| `getFeatureValue_CACHED_MAY_BE_STALE()` | **執行期** 動態 flag，從 GrowthBook 讀取快取值 | `getFeatureValue_CACHED_MAY_BE_STALE('tengu_otk_slot_v1', false)` 等 |

**GrowthBook 初始化**（main.tsx:2020）：
```ts
// 特殊情況才立即初始化（ant + 指定 model 但非 default + 無 env override）
await initializeGrowthBook()
// 其他情況：auth 變更後刷新
refreshGrowthBookAfterAuthChange()
```

`L$()` 函式未出現在 main.tsx — 該函式可能在 binary 版本中，外流原始碼中 feature flag 的主要入口是 `getFeatureValue_CACHED_MAY_BE_STALE()`。

### tengu_* 動態 Flag 清單（main.tsx 中）

| flag | 預設值 | 說明 |
|------|--------|------|
| `tengu_cicada_nap_ms` | 0 | 啟動 prefetch 節流時間（ms） |
| `tengu_miraculo_the_bard` | false | Fast mode prefetch kill switch |
| `tengu_remote_backend` | false | 遠端 TUI backend 開關 |
| `tengu_kairos` | false | KAIROS/assistant mode GrowthBook 開關 |
| `tengu_otk_slot_v1` | false | max_output_tokens 8k→64k escalation（query.ts） |

**注意**：`tengu_sotto_voce` 和 `tengu_bergotte_lantern` 未出現在 main.tsx（可能在 systemPrompt.ts 或其他檔案）。

### initialPermissionMode（啟動時 Permission Mode）

```ts
// CLI arg → 初始化
const { mode: permissionMode, notification } = initialPermissionModeFromCLI({
  permissionModeCli,      // --permission-mode <mode>
  dangerouslySkipPermissions,  // --dangerously-skip-permissions
})
setSessionBypassPermissionsMode(permissionMode === 'bypassPermissions')
```

Auto mode 啟用條件（feature gate: `TRANSCRIPT_CLASSIFIER`）：
- `--enable-auto-mode` CLI flag
- `--permission-mode auto`
- `isDefaultPermissionModeAuto()` 為 true

### KAIROS（Autonomous Assistant Mode）

KAIROS 是 Claude Code 的**自主助理模式**（autonomous daemon/assistant mode），ANT-ONLY（`feature('KAIROS')` compile-time gate）。

**啟用流程**（main.tsx:1056-1095）：
1. `--assistant` CLI flag → `markAssistantForced()`
2. 檢查 trust dialog 已接受（`checkHasTrustDialogAccepted()`）
3. `isKairosEnabled()` GrowthBook 動態 check
4. 啟用後：`--brief` 模式、`setKairosActive(true)`、`initializeAssistantTeam()`

相關模組（compile-time conditional import）：
- `./assistant/index.js` — KAIROS 主模組
- `./assistant/gate.js` — KAIROS 啟用判斷

`BG_SESSIONS` feature flag（main.tsx:1122）：背景 session 功能，與 KAIROS 相關聯；`--agent` CLI 指定時設置 `CLAUDE_CODE_AGENT` env var。

## Query 處理流程（T09）

來源：外流原始碼 2.1.88 `query.ts`（1,729 行）、`QueryEngine.ts`

### query.ts vs QueryEngine.ts 分工

| 層次 | 負責範圍 |
|------|---------|
| `QueryEngine` class（QueryEngine.ts） | Session 生命週期管理；system prompt 組裝；ThinkingConfig 初始化；呼叫 `query()` |
| `query()` function（query.ts:219） | 薄包裝器，呼叫 `queryLoop()`；處理 consumed command UUID 生命週期 |
| `queryLoop()` function（query.ts:241） | 實際的 `while(true)` 無限迴圈，包含所有 per-iteration 處理邏輯 |

`QueryEngine` 初始化 `ThinkingConfig`（QueryEngine.ts:278）：
```ts
const initialThinkingConfig: ThinkingConfig = thinkingConfig
  ? thinkingConfig
  : shouldEnableThinkingByDefault() !== false
    ? { type: 'adaptive' }
    : { type: 'disabled' }
```

### Per-Iteration 處理 Pipeline（每輪 API 呼叫前）

按執行順序：

1. **`startSkillDiscoveryPrefetch`**：背景預取 skill（非阻塞，streaming 期間完成）
2. **`applyToolResultBudget`**：強制 per-message tool result 大小限制（超過閾值外部儲存）
3. **`snipModule.snipCompactIfNeeded`**（feature gate: `HISTORY_SNIP`）：截斷歷史訊息
4. **`deps.microcompact`**（feature gate: `CACHED_MICROCOMPACT`）：微壓縮
5. **`contextCollapse.applyCollapsesIfNeeded`**（feature gate: `CONTEXT_COLLAPSE`）：上下文折疊
6. **`deps.autocompact`**：自動壓縮（超過 token 閾值時）
7. **`deps.callModel({...})`**：實際 API 呼叫

### Streaming 處理邏輯

```
for await (const message of deps.callModel({ messages, systemPrompt, thinkingConfig, tools, ... }))
```

- **tool_use backfill**：對 tool_use block 的 input 做 clone（`backfillObservableInput`），避免影響 prompt caching（byte mismatch）
- **錯誤 withholding**：以下錯誤在 streaming 時暫時不 yield，等待 recovery：
  - prompt-too-long（413）：先嘗試 contextCollapse drain，再 reactiveCompact
  - media size error：只嘗試 reactiveCompact（collapse 不能移除圖片）
  - max_output_tokens：先嘗試 8k→64k escalation（`tengu_otk_slot_v1` flag），再多輪 recovery（最多 3 次）
- **Streaming fallback**：`streamingFallbackOccured` 時，tombstone 所有 orphaned assistant messages，建立全新 `StreamingToolExecutor` 重試
- **Model fallback**：`FallbackTriggeredError` 時切換到 `fallbackModel`；thinking signatures 為 model-bound，切換前執行 `stripSignatureBlocks`
- **StreamingToolExecutor**（feature gate: `streamingToolExecution`）：在 streaming 期間**並行**執行工具，`getRemainingResults()` 在 streaming 後 drain 剩餘結果

### Extended Thinking 啟用條件

`ThinkingConfig` 類型：

| type | 說明 |
|------|------|
| `'adaptive'` | 新版預設，server-side 處理，thinking 加密 |
| `'disabled'` | 關閉 thinking |

傳遞路徑：`QueryEngine.initialThinkingConfig` → `toolUseContext.options.thinkingConfig` → `deps.callModel({ thinkingConfig, ... })`

**三大硬性規則**（query.ts:151-163 注釋）：
1. 含 thinking/redacted_thinking block 的訊息，發送時 `max_thinking_length` 必須 > 0
2. thinking block 不可是 block 中最後一個 element
3. thinking block 必須在整個 assistant trajectory 期間保留（一個 turn，或若含 tool_use 則延伸到後續的 tool_result + 下一個 assistant message）

### Cache Control 設定位置

**System prompt 分界**（constants/prompts.ts:114）：
```ts
export const SYSTEM_PROMPT_DYNAMIC_BOUNDARY = '__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__'
```
- 此標記**之前**的 section：可用 `scope: 'global'`（跨用戶、跨 org 全局快取）
- 此標記**之後**的 section：user/session-specific，不做全局快取

**Tool pool cache 穩定性**（tools.ts:354-366）：
- 工具池排序：built-in tools 字母序為前綴，MCP tools 字母序附後
- 伺服器端 `claude_code_global_system_caching` 政策在最後一個 built-in tool 後放置全局快取斷點
- 目的：MCP tools 的增減不會讓 built-in tool 的快取 key 失效

`getCacheControl()` 函式位於 `services/api/claude.ts`（非此次外流範圍），由 yoloClassifier 等地方匯入使用。

### 迴圈終止條件

`queryLoop()` 以 `return { reason: ... }` 方式終止：

| reason | 觸發條件 |
|--------|---------|
| `'completed'` | 無 tool use，無錯誤，正常結束 |
| `'aborted_streaming'` | streaming 期間 AbortController 被中止 |
| `'aborted_tools'` | 工具執行期間被中止 |
| `'blocking_limit'` | token 使用達硬性封鎖閾值（autocompact OFF 時） |
| `'max_turns'` | `turnCount > maxTurns` |
| `'hook_stopped'` | PreToolUse hook 返回 `stop_hook_active` |
| `'stop_hook_prevented'` | Stop hook 返回 `preventContinuation: true` |
| `'model_error'` | 未處理的 model/runtime 錯誤 |
| `'prompt_too_long'` | prompt-too-long 無法 recovery |
| `'image_error'` | 圖片/媒體過大錯誤無法 recovery |
| `'stop_hook_prevented'` | Stop hook 阻止繼續 |

maxTurns 限制：`maxTurns` 參數存在時，每次 tool execution 後 `nextTurnCount > maxTurns` 會 yield `max_turns_reached` attachment 並返回。
