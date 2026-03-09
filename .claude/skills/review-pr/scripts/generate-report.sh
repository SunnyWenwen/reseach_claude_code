#!/usr/bin/env bash
# 產生 PR 審查報告的 metadata 檔案
# 用法: generate-report.sh <pr-number> <session-id>

PR_NUMBER="$1"
SESSION_ID="$2"
OUTPUT_DIR="./review-reports"
OUTPUT_FILE="${OUTPUT_DIR}/pr-${PR_NUMBER}-${SESSION_ID}.md"

mkdir -p "$OUTPUT_DIR"

cat > "$OUTPUT_FILE" <<EOF
# PR #${PR_NUMBER} Review Report
- Session: ${SESSION_ID}
- Date: $(date '+%Y-%m-%d %H:%M:%S')
- Reviewer: Claude Code (review-pr skill)
EOF

echo "報告 metadata 已建立：$OUTPUT_FILE"
