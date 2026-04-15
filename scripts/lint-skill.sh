#!/usr/bin/env bash
# lint-skill.sh — Static quality checks for SKILL.md files
# Usage: ./scripts/lint-skill.sh <path-to-SKILL.md>
# Exit code: 0=pass, 1=fail

set -euo pipefail

SKILL_FILE="${1:?Usage: lint-skill.sh <SKILL.md>}"

if [ ! -f "$SKILL_FILE" ]; then
  echo "FAIL: File not found: $SKILL_FILE"
  exit 1
fi

ERRORS=0
WARNINGS=0

# --- Frontmatter checks ---
# Must have YAML frontmatter with --- delimiters
FIRST_LINE=$(head -1 "$SKILL_FILE")
if [ "$FIRST_LINE" != "---" ]; then
  echo "FAIL: Missing YAML frontmatter opening ---"
  ERRORS=$((ERRORS + 1))
fi

# Must have 'name:' field
if ! grep -q '^name:' "$SKILL_FILE"; then
  echo "FAIL: Missing 'name' field in frontmatter"
  ERRORS=$((ERRORS + 1))
fi

# Must have 'description:' field
if ! grep -q '^description:' "$SKILL_FILE"; then
  echo "FAIL: Missing 'description' field in frontmatter"
  ERRORS=$((ERRORS + 1))
fi

# Description should be <= 1024 chars
DESC_LINE=$(grep '^description:' "$SKILL_FILE" || true)
if [ -n "$DESC_LINE" ]; then
  DESC_LEN=${#DESC_LINE}
  if [ "$DESC_LEN" -gt 1100 ]; then
    echo "WARN: Description is ${DESC_LEN} chars (recommended <=1024)"
    WARNINGS=$((WARNINGS + 1))
  fi
fi

# Name should be lowercase with hyphens
NAME_VAL=$(grep '^name:' "$SKILL_FILE" | sed 's/^name:[[:space:]]*//' | tr -d '"' | tr -d "'")
if echo "$NAME_VAL" | grep -qE '[A-Z_]'; then
  echo "WARN: Name '$NAME_VAL' should be lowercase with hyphens only"
  WARNINGS=$((WARNINGS + 1))
fi

# --- Structure checks ---
# Should have at least one ## heading (workflow section)
H2_COUNT=$(grep -c '^## ' "$SKILL_FILE" || true)
if [ "$H2_COUNT" -lt 1 ]; then
  echo "FAIL: No ## headings found — skill lacks structure"
  ERRORS=$((ERRORS + 1))
fi

# Should have numbered steps (1. or Step or Phase)
if ! grep -qE '(^1\.|^Step|^Phase|^[0-9]+[\.\)] )' "$SKILL_FILE"; then
  echo "WARN: No numbered steps/phases found — workflow may lack clarity"
  WARNINGS=$((WARNINGS + 1))
fi

# --- Size checks ---
FILE_SIZE=$(wc -c < "$SKILL_FILE")
LINE_COUNT=$(wc -l < "$SKILL_FILE")

# Warn if file > 20KB
if [ "$FILE_SIZE" -gt 20480 ]; then
  echo "WARN: File is $(( FILE_SIZE / 1024 ))KB — consider splitting into references"
  WARNINGS=$((WARNINGS + 1))
fi

# --- Resource reference checks ---
# Check if referenced paths exist (basic)
while IFS= read -r ref_path; do
  # Extract path from markdown references like `references/xxx.md` or `scripts/xxx.sh`
  clean_path=$(echo "$ref_path" | sed 's/`//g' | sed 's/.*(\([^)]*\)).*/\1/' | tr -d ' ')
  if [ -n "$clean_path" ] && ! echo "$clean_path" | grep -qE '^(http|https|~|/|\$)'; then
    SKILL_DIR=$(dirname "$SKILL_FILE")
    if [ ! -f "$SKILL_DIR/$clean_path" ]; then
      echo "WARN: Referenced file not found: $clean_path (relative to $SKILL_DIR)"
      WARNINGS=$((WARNINGS + 1))
    fi
  fi
done < <(grep -oE '`[^`]*(references|scripts|assets)/[^`]*`' "$SKILL_FILE" 2>/dev/null || true)

# --- Summary ---
echo ""
echo "=== lint-skill: $(basename "$(dirname "$SKILL_FILE")") ==="
echo "  File: ${LINE_COUNT} lines, $(( FILE_SIZE / 1024 ))KB"
echo "  Errors: $ERRORS"
echo "  Warnings: $WARNINGS"
echo ""

if [ "$ERRORS" -gt 0 ]; then
  echo "RESULT: FAIL"
  exit 1
else
  echo "RESULT: PASS${WARNINGS:+ (with $WARNINGS warnings)}"
  exit 0
fi
