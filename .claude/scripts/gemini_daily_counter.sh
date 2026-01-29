#!/bin/bash

# Gemini CLI 日次使用量カウンター
# 今日のリクエスト数をカウントし、無料枠（1,000回/日）との比較を表示

LOG_FILE=".claude/logs/gemini_usage.jsonl"
TODAY=$(date +%Y-%m-%d)
LIMIT=1000

# ログファイルが存在しない場合は0件として扱う
if [ ! -f "$LOG_FILE" ]; then
  COUNT=0
else
  COUNT=$(grep "$TODAY" "$LOG_FILE" 2>/dev/null | wc -l)
fi

PERCENTAGE=$((COUNT * 100 / LIMIT))
REMAINING=$((LIMIT - COUNT))

echo "=== Gemini CLI 使用状況 ($TODAY) ==="
echo "リクエスト数: $COUNT / $LIMIT (無料枠)"
echo "残り: $REMAINING リクエスト"

# 80%到達時にアラート表示
if [ $PERCENTAGE -ge 80 ]; then
  echo "⚠️  警告: 無料枠の80%に到達しました"
fi
