# Undercover 模式

來源：外流原始碼 2.1.88 `utils/undercover.ts`（89 行）

## 用途

Undercover 模式是 Anthropic **內部員工（ANT）專用**的安全機制，用於在公開/開源 repo 提交程式碼時，防止洩漏 Anthropic 內部資訊（模型代號、版本號、內部工具等）。

**所有程式碼均被 `process.env.USER_TYPE === 'ant'` 條件包住**。外部版本 build 時，bundler 透過 dead-code elimination 將所有 ant 分支移除，所有函式在外部版本中 reduce 為 trivial return（`return false` / `return ''`）。外部用戶不受影響。

---

## 啟用條件（`isUndercover()`）

```ts
export function isUndercover(): boolean {
  if (process.env.USER_TYPE === 'ant') {
    if (isEnvTruthy(process.env.CLAUDE_CODE_UNDERCOVER)) return true
    // Auto: active unless we've positively confirmed we're in an allowlisted internal repo.
    return getRepoClassCached() !== 'internal'
  }
  return false
}
```

| 條件 | 結果 |
|------|------|
| `CLAUDE_CODE_UNDERCOVER=1`（env var） | 強制 ON |
| repo remote 在內部白名單（`INTERNAL_MODEL_REPOS`）中 → `repoClass === 'internal'` | OFF |
| 其他（外部 repo、非 git 目錄、`repoClass` 尚未判定）| **預設 ON** |

**沒有強制 OFF**：設計上刻意不提供。若無法確認是內部 repo，就保持 undercover，避免洩漏。

---

## Undercover 指令原文（`getUndercoverInstructions()`）

注入到 system prompt 中的完整指令：

```
## UNDERCOVER MODE — CRITICAL

You are operating UNDERCOVER in a PUBLIC/OPEN-SOURCE repository. Your commit
messages, PR titles, and PR bodies MUST NOT contain ANY Anthropic-internal
information. Do not blow your cover.

NEVER include in commit messages or PR descriptions:
- Internal model codenames (animal names like Capybara, Tengu, etc.)
- Unreleased model version numbers (e.g., opus-4-7, sonnet-4-8)
- Internal repo or project names (e.g., claude-cli-internal, anthropics/…)
- Internal tooling, Slack channels, or short links (e.g., go/cc, #claude-code-…)
- The phrase "Claude Code" or any mention that you are an AI
- Any hint of what model or version you are
- Co-Authored-By lines or any other attribution

Write commit messages as a human developer would — describe only what the code
change does.

GOOD:
- "Fix race condition in file watcher initialization"
- "Add support for custom key bindings"
- "Refactor parser for better error messages"

BAD (never write these):
- "Fix bug found while testing with Claude Capybara"
- "1-shotted by claude-opus-4-6"
- "Generated with Claude Code"
- "Co-Authored-By: Claude Opus 4.6 <…>"
```

---

## 一次性提示對話框（`shouldShowUndercoverAutoNotice()`）

當 undercover 由**自動偵測**啟用（非手動設 env var）時，首次顯示說明對話框。

條件：
1. `CLAUDE_CODE_UNDERCOVER` env var **未設定**
2. `isUndercover()` 為 true（自動偵測）
3. `getGlobalConfig().hasSeenUndercoverAutoNotice` 為 false（未看過）

---

## Co-Authored-By 移除邏輯

注釋中提到 Co-Authored-By 移除，但實際實作應在 `commitAttribution.ts`（非本檔）。`getUndercoverInstructions()` 只是在 prompt 中**禁止 Claude 自行添加** Co-Authored-By，並非在 git hooks 中主動移除。

---

## 洩漏防護項目清單

| 類別 | 範例 |
|------|------|
| 模型代號（動物名）| Capybara, Tengu 等 |
| 未發布版本號 | opus-4-7, sonnet-4-8 |
| 內部 repo | claude-cli-internal, anthropics/... |
| 內部工具 | go/cc（短連結）、#claude-code-（Slack） |
| AI 身份 | "Claude Code"、"Generated with Claude Code" |
| 版本資訊 | "1-shotted by claude-opus-4-6" |
| 歸因資訊 | Co-Authored-By 行 |
