# Token Usage Tracker Skill

トークン消費量をリアルタイムで追跡・記録するスキルです。

## 概要

Claude Codeのトークン使用状況を自動的に記録し、以下の情報を提供します：

- セッション単位のトークン消費量
- スキル・タスク単位の詳細な追跡
- ツール呼び出し毎のトークン記録
- 外部AI委任による節約量の追跡

## データ保存場所

```
D:\projects\P010\.token-usage\
├── sessions\
│   └── {session_id}.jsonl     # セッションごとのイベントログ
├── summary.json                # 累積統計サマリー
└── current.json                # リアルタイム表示用
```

**重要**: `.token-usage/` ディレクトリはGit追跡外です（`.gitignore`に追加済み）。

## 使用方法

### 1. セッション開始

```bash
python -m src.token_usage.cli \
  --event session_start \
  --session-id "sess_20260130_143022" \
  --issue "94"
```

### 2. スキル開始

```bash
python -m src.token_usage.cli \
  --event skill_start \
  --skill "tdd-cycle" \
  --issue "94"
```

### 3. ツール呼び出し記録

```bash
python -m src.token_usage.cli \
  --event tool_call \
  --tool "Read" \
  --input-tokens 1234 \
  --output-tokens 567 \
  --model "sonnet-4.5"
```

### 4. スキル終了

```bash
python -m src.token_usage.cli \
  --event skill_end \
  --skill "tdd-cycle"
```

### 5. 外部AI委任記録

```bash
python -m src.token_usage.cli \
  --event external_delegation \
  --delegate-to "codex-cli" \
  --task "code-review" \
  --estimated-tokens-saved 3000
```

### 6. セッション終了

```bash
python -m src.token_usage.cli \
  --event session_end
```

## 環境変数

### TOKEN_USAGE_DIR

ログ保存先ディレクトリを指定します（デフォルト: `D:/projects/P010/.token-usage`）。

```bash
export TOKEN_USAGE_DIR="/path/to/custom/.token-usage"
```

### CLAUDE_SESSION_ID

現在のセッションIDを指定します。複数のWorktreeで作業する場合に使用します。

```bash
export CLAUDE_SESSION_ID="sess_20260130_143022"
```

## イベントログ形式

### session_start

```jsonl
{"timestamp": "2026-01-30T14:30:22Z", "event": "session_start", "session_id": "sess_20260130_143022", "issue": "94", "worktree": "/worktrees/issue-94"}
```

### skill_start

```jsonl
{"timestamp": "2026-01-30T14:30:25Z", "event": "skill_start", "skill": "tdd-cycle", "issue": "94"}
```

### tool_call

```jsonl
{"timestamp": "2026-01-30T14:30:30Z", "event": "tool_call", "tool": "Read", "params": {}, "input_tokens": 1234, "output_tokens": 567, "model": "sonnet-4.5", "cumulative_input": 1234, "cumulative_output": 567}
```

### skill_end

```jsonl
{"timestamp": "2026-01-30T14:32:00Z", "event": "skill_end", "skill": "tdd-cycle", "duration_sec": 90, "total_input": 5000, "total_output": 2000, "tool_calls": 8}
```

### external_delegation

```jsonl
{"timestamp": "2026-01-30T14:35:30Z", "event": "external_delegation", "delegate_to": "codex-cli", "task": "code-review", "estimated_tokens_saved": 3000}
```

### session_end

```jsonl
{"timestamp": "2026-01-30T14:40:00Z", "event": "session_end", "total_input": 15234, "total_output": 6789, "total_tools": 45, "duration_sec": 578}
```

## リアルタイム表示

`display.py` を使用して、リアルタイムでトークン使用状況を表示できます。

```python
from src.token_usage.display import TokenUsageDisplay

display = TokenUsageDisplay(base_dir="D:/projects/P010/.token-usage")
print(display.format_display())
```

**表示例**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Token Usage (Session: 2026-01-30 14:30)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current Context: /tdd-cycle (Issue #94)

Cumulative:
  Input:  12,345 tokens
  Output:  5,678 tokens
  Total:  18,023 tokens

Latest (2026-01-30 14:35:22):
  Event: skill_end (tdd-cycle)
  Input:  1,234 tokens
  Output:   567 tokens
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## トークン数推定

`estimator.py` を使用して、テキストのトークン数を推定できます。

```python
from src.token_usage.estimator import TokenEstimator

estimator = TokenEstimator(model="gpt-4")
tokens = estimator.estimate("Hello, world!")
print(f"推定トークン数: {tokens}")  # 推定トークン数: 4
```

## 既存スキルとの統合

既存のスキル（`/tdd`, `/start-issue`, `/review` など）に、トークン記録機能を追加できます。

**統合例（/tddスキル）**:

```markdown
## TDDサイクル開始

\`\`\`bash
# セッション開始
python -m src.token_usage.cli --event session_start --session-id "$SESSION_ID" --issue "$ISSUE_NUM"

# スキル開始
python -m src.token_usage.cli --event skill_start --skill "tdd-cycle" --issue "$ISSUE_NUM"
\`\`\`

## RED Phase

... テスト作成 ...

## GREEN Phase

... 実装 ...

## REFACTOR Phase

... リファクタリング ...

## TDDサイクル完了

\`\`\`bash
# スキル終了
python -m src.token_usage.cli --event skill_end --skill "tdd-cycle"

# セッション終了
python -m src.token_usage.cli --event session_end
\`\`\`
```

## 統計情報の確認

`statistics.py` を使用して、累積統計を確認できます。

```python
from src.token_usage.statistics import TokenStatistics

stats = TokenStatistics(base_dir="D:/projects/P010/.token-usage")
stats.update_from_session(session_log_file="sessions/sess_20260130_143022.jsonl")

summary = stats.get_summary()
print(f"総トークン数: {summary['total_tokens']['input']} (入力)")
print(f"総トークン数: {summary['total_tokens']['output']} (出力)")
```

## データモデル

Pydanticを使用したデータモデル定義により、型安全性とバリデーションを提供します。

```python
from src.token_usage.models import ToolCallEvent

event = ToolCallEvent(
    tool="Read",
    params={"file_path": "test.py"},
    input_tokens=1234,
    output_tokens=567,
    model="sonnet-4.5",
    cumulative_input=1234,
    cumulative_output=567
)
```

## トラブルシューティング

### ディレクトリが作成されない

`TokenUsageLogger` の初期化時に、`.token-usage/` ディレクトリが自動作成されます。権限エラーが発生する場合は、手動でディレクトリを作成してください。

```bash
mkdir -p "D:/projects/P010/.token-usage/sessions"
```

### セッションIDが重複する

セッションIDはマイクロ秒精度で生成されるため、通常は重複しません。手動でセッションIDを指定する場合は、一意性を保証してください。

### トークン推定が不正確

`tiktoken` ライブラリによる推定値は、実際のClaude APIのトークン数と若干異なる場合があります（±10-20%程度）。これは推定値であり、参考値として使用してください。

## 今後の拡張予定

- Phase 3: AI分析支援機能（`/token-analyze` スキル）
- Phase 4: ツールラッパーによる自動記録
- Phase 5: 外部AI委任の自動判定

## 関連ドキュメント

- Issue #94: トークン消費可視化・分析機能の実装
- `.claude/rules/testing.md`: テスト実装ガイドライン
- `.claude/skills/codex-delegate/SKILL.md`: 外部AI委任機能

---

**実装状況**: Phase 1（ログ収集基盤）+ Phase 2（トークン推定・CLI）完了
