# /review - コードレビュー

段階的にコードレビューを実行します。

## レビュー実行フロー（必須手順）

### Step 1: Codex CLI存在確認

**原則として、すべてのレビューはCodex CLIに委任すること。**

まず、Codex CLIの存在を確認します：

```bash
# Windows
where codex 2>nul && echo "Codex CLI available" || echo "Codex CLI not found"
```

- **Codex CLI が存在する場合** → Step 2（Codex委任）へ進む
- **Codex CLI が存在しない場合** → Step 3（Claude Codeフォールバック）へ進む

### Step 2: Codex委任（原則）

codex-delegateスキルを使用してprogressive-reviewを実行：

```
codex-delegateスキルを使用して、progressive-reviewを実行してください。
対象: 現在のブランチの変更（git diff main...HEAD）
Issue: #{ブランチから抽出したIssue番号}
```

### Step 3: Claude Code（Codex CLI利用不可時のみ）

**Codex CLI利用不可時のみ**以下の手順で実行：

Codex CLI利用不可条件：
- Codex CLIがインストールされていない
- `OPENAI_API_KEY` が設定されていない
- Codex CLI実行がエラーで失敗した

この場合、以下の「レビュー観点」に従って従来通り4観点の段階的レビューを実行してください。

## レビュー観点

### 1. セキュリティチェック

- [ ] 入力バリデーションは適切か
- [ ] 認証・認可の実装は正しいか
- [ ] シークレット情報がハードコードされていないか
- [ ] SQLインジェクション等の脆弱性はないか
- [ ] XSS対策は適切か

### 2. パフォーマンスチェック

- [ ] N+1問題がないか
- [ ] 不要なデータベースクエリがないか
- [ ] メモリリークの可能性はないか
- [ ] キャッシュ戦略は適切か

### 3. 保守性チェック

- [ ] 命名規約に従っているか
- [ ] DRY原則を守っているか
- [ ] 単一責任の原則を守っているか
- [ ] 適切なコメントがあるか（ただし過剰ではないか）

### 4. テストチェック

- [ ] テストカバレッジは80%以上か
- [ ] エッジケースをカバーしているか
- [ ] テストは独立して実行可能か
- [ ] テストの意図が明確か

## 評価基準

| 観点 | 配点 |
|------|------|
| セキュリティ | 25点 |
| パフォーマンス | 25点 |
| 保守性 | 25点 |
| テスト | 25点 |

**合計80点以上** → 承認
**80点未満** → 修正が必要

## レビュー完了後の処理

レビューが完了したら、スコアに応じて以下の処理を行ってください。

### 80点以上の場合（承認）

レビュー結果を自動的にIssueにコメントします。

#### Step 1: Issue番号の特定

会話のコンテキストからIssue番号を特定してください。以下の優先順位で取得します：

1. 会話中で `/start-issue XX` が実行された場合、そのIssue番号を使用
2. 会話中でIssue番号が明示的に言及されている場合、それを使用
3. （フォールバック）上記で特定できない場合のみ、ブランチ名から抽出：

```bash
# ブランチ名を取得
BRANCH=$(git branch --show-current)

# Issue番号を抽出（例: feature/issue-18-xxx → 18）
ISSUE_NUM=$(echo "$BRANCH" | grep -oE 'issue-[0-9]+' | grep -oE '[0-9]+')

# 抽出結果を確認
echo "Issue番号: $ISSUE_NUM"
```

- Issue番号が特定できた場合 → Step 2 へ進む
- Issue番号が特定できない場合 → 「Issue番号を自動特定できませんでした。手動で `/issue-sync {番号}` を実行してください。」と案内してスキップ

#### Step 2: レビュー結果をIssueに投稿

以下の形式でIssueにコメントを投稿します：

```bash
# 環境に応じた日時取得（クロスプラットフォーム対応）
REVIEW_DATE=$(date "+%Y-%m-%d %H:%M:%S" 2>/dev/null || powershell -Command "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'")

# 使用モデル情報（review.mdのデフォルトモデル: Claude Sonnet 4.5）
EXECUTOR="Claude Code直接実行"
MODEL="Claude Sonnet 4.5"

gh issue comment $ISSUE_NUM --body "$(cat <<EOF
## レビュー完了報告 - ${REVIEW_DATE}

### 実行情報
- **実行者**: ${EXECUTOR}
- **使用モデル**: ${MODEL}
- **実行日時**: ${REVIEW_DATE}

### レビュー結果
| 観点 | スコア |
|------|--------|
| セキュリティ | {X}/25 |
| パフォーマンス | {X}/25 |
| 保守性 | {X}/25 |
| テスト | {X}/25 |
| **合計** | **{X}/100** ✅ |

### 指摘事項
{指摘があれば記載、なければ「特になし」}

### 次のステップ
- PR作成準備完了
EOF
)"
```

投稿完了後、「レビュー結果をIssue #{番号} に投稿しました。」と報告してください。

### 80点未満の場合（要修正）

自動投稿は行いません。以下を案内してください：

- 修正が必要な箇所を明示
- 修正後に再度 `/review` を実行するよう案内
- 必要に応じて `/issue-sync` で進捗を同期することを提案

## Relationship with Progressive Review

本コマンド (`/review`) は Progressive Review スキル (`.claude/skills/progressive-review/SKILL.md`) の実行ワークフローです。

| 項目 | 説明 |
|------|------|
| **本コマンドの責務** | レビューのエントリポイント。スコア判定後のIssue投稿フローを定義 |
| **Progressive Review の責務** | 4観点を段階的に評価する実行ロジック。評価手順の詳細を定義 |
| **reviewer.md との違い** | reviewer.md はサブエージェントとして呼び出される軽量版。本コマンドはPR前最終レビュー |

## 関連コマンド

- `/start-issue` - Issue作業開始
- `/tdd` - TDDサイクル実行
- `/pr-create` - PR作成とCI確認
- `/check-ci` - CI結果を確認
- `/pr-merge` - PRをマージ
