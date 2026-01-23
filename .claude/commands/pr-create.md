# /pr-create - PR作成とCI確認

PRを作成し、自動的にCI結果を確認します。

## 使い方

```
/pr-create [--wait]
```

- 引数なし: PR作成後、CI結果を一度確認。実行中の場合は選択肢を提示
- `--wait`: CI完了まで自動待機

## 実行手順

### 1. 事前チェック

```bash
# 現在のブランチを確認
git branch --show-current

# コミット済みの変更があることを確認
git status
```

#### チェックポイント

| 状態 | 対応 |
|------|------|
| 未コミットの変更がある | コミットを促す |
| mainブランチ上にいる | エラー（featureブランチで実行） |
| リモートにプッシュされていない | プッシュを実行 |

### 2. リモートへのプッシュ

```bash
# 現在のブランチをリモートにプッシュ
git push -u origin $(git branch --show-current)
```

### 3. Issue情報の取得

PR作成に必要なIssue情報を取得します。Issue番号は以下の優先順位で特定してください：

1. 会話コンテキストから（`/start-issue XX` で開始した場合）
2. ブランチ名からフォールバック抽出:

```bash
BRANCH=$(git branch --show-current)
ISSUE_NUM=$(echo "$BRANCH" | grep -oE 'issue-[0-9]+' | grep -oE '[0-9]+')
```

Issue番号が特定できたら、Issueタイトルを取得します：

```bash
ISSUE_TITLE=$(gh issue view $ISSUE_NUM --json title -q '.title')
```

### 4. PR作成（日本語）

PRタイトルとボディを日本語で作成します。

#### タイトル生成ルール

- Issueタイトルをそのまま使用する
- 例: `PRを日本語で作成するようにする`

#### ボディ生成ルール

以下のテンプレートに従い、Issue内容と `git diff main...HEAD` の差分を参考に、各セクションを日本語で記述してください：

```bash
gh pr create --title "$ISSUE_TITLE" --body "$(cat <<'EOF'
## 概要
- {Issueの目的と実装内容を箇条書きで記載}

## 変更内容
- {変更したファイルと変更内容を記載}

## テスト
- {テスト内容・検証結果を記載}

Closes #{Issue番号}
EOF
)"
```

#### 注意事項

- タイトル・ボディは必ず日本語で記述すること
- `Closes #XX` はGitHubのIssue自動クローズ機能を利用するため、必ず含めること
- ボディのセクション（概要・変更内容・テスト）は省略せず、実際の変更に基づいて記述すること

### 5. PR番号の取得

```bash
# 作成したPRの番号を取得
gh pr view --json number -q '.number'
```

### 6. CI結果の確認

PR作成後、自動的にCI結果を確認します。

#### ワークフロー実行の取得

```bash
# 最新のワークフロー実行を取得
gh run list --branch $(git branch --show-current) --limit 5 --json databaseId,status,conclusion,createdAt,name
```

#### ステータスの解釈

| status | conclusion | 状態 |
|--------|-----------|------|
| `in_progress` | - | 実行中 |
| `completed` | `success` | 成功 |
| `completed` | `failure` | 失敗 |
| `completed` | `cancelled` | キャンセル |
| `queued` | - | 待機中 |
| `completed` | `skipped` | スキップ（paths filterなど） |

### 7. 結果に応じた処理

#### CI成功の場合

```
## CI結果: 成功

| 項目 | 値 |
|------|-----|
| ワークフロー | Test |
| ステータス | success |
| 実行時間 | {duration} |

次のステップ: `/pr-merge {PR番号}` でマージできます
```

#### CI実行中の場合

```
## CI結果: 実行中

| 項目 | 値 |
|------|-----|
| ワークフロー | Test |
| ステータス | in_progress |
| 実行ID | {run-id} |

選択してください:
1. 待機する - CI完了まで待機します
2. 後で確認 - `/check-ci {PR番号}` で後ほど確認してください
```

`--wait` オプションが指定されている場合、自動的に待機モードに入ります。

#### 待機オプション（ポーリング戦略）

| 回数 | 間隔 |
|------|------|
| 1-5回 | 10秒 |
| 6-10回 | 30秒 |
| 11回以降 | 60秒 |

#### タイムアウト設定

- デフォルト: 5分
- 最大: 15分

タイムアウトに達した場合は、現在のステータスを報告して終了します。

```bash
# 完了まで待機
gh run watch <run-id>
```

#### CI失敗の場合

```
## CI結果: 失敗

| 項目 | 値 |
|------|-----|
| ワークフロー | Test |
| ステータス | failure |
| 失敗ジョブ | {job-name} |

### エラーログ

{ログ抜粋}

### 推定原因

{パターンマッチングによる原因推定}

次のステップ:
1. エラーを修正
2. コミット＆プッシュ
3. `/check-ci {PR番号}` でCI結果を再確認
```

```bash
# 失敗ログの取得
gh run view <run-id> --log-failed
```

#### CIがスキップされた場合

paths filterなどでCIがスキップされた場合:

```
## CI結果: スキップ

| 項目 | 値 |
|------|-----|
| ワークフロー | Test |
| ステータス | skipped |
| 理由 | paths filter により対象外 |

次のステップ: `/pr-merge {PR番号}` でマージできます
```

#### CIが設定されていない場合

ワークフロー実行が取得できない場合:

```
## CI結果: 未検出

CIワークフローが検出されませんでした。

PR #XX を作成しました。
→ {PR URL}

次のステップ:
- `/pr-merge {PR番号}` で直接マージ
- または手動でCIを確認してください
```

### 8. 出力例

#### 成功時の完全な出力

```
PR #XX を作成しました。
→ https://github.com/{owner}/{repo}/pull/XX

CI結果を確認中...

## CI結果: 成功

| 項目 | 値 |
|------|-----|
| ワークフロー | Test |
| ステータス | success |
| 実行時間 | 1m 23s |

次のステップ: `/pr-merge XX` でマージできます
```

## エラーハンドリング

| 状況 | 対応 |
|------|------|
| PR作成失敗 | エラーメッセージを表示し、原因を案内 |
| 既にPRが存在する | 既存PRのURLを表示し、`/check-ci` での確認を案内 |
| プッシュ失敗 | リモートとの差分を確認し、対処法を案内 |
| CI取得失敗 | PRのURLを表示し、手動確認を案内 |

## 関連コマンド

- `/check-ci` - CI結果を確認
- `/pr-merge` - PRをマージ
- `/review` - コードレビュー
- `/start-issue` - Issue作業開始
