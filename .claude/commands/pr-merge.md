# /pr-merge - PRマージとブランチ削除

CIが通っているPRをマージし、ブランチを自動削除します。

## 使い方

```
/pr-merge [PR番号]
```

PR番号を省略した場合、現在のブランチに関連するPRを使用します。

## 実行手順

### 1. PRの特定

```bash
# PR番号が指定された場合
gh pr view $ARGUMENTS --json number,state,headRefName,mergeable,mergeStateStatus

# PR番号が省略された場合
gh pr view --json number,state,headRefName,mergeable,mergeStateStatus
```

### 2. CI結果の簡易確認

```bash
# 最新のワークフロー実行を確認
gh run list --branch <branch> --limit 1 --json status,conclusion
```

#### 判定基準

| conclusion | 状態 | 次のアクション |
|-----------|------|---------------|
| `success` | CI成功 | マージに進む |
| `failure` | CI失敗 | マージをスキップ |
| `null` | 実行中 | 完了を待つか確認 |

### 3. マージの実行

```bash
# マージとリモートブランチ削除を同時に実行
gh pr merge <pr-number> --merge --delete-branch
```

### 4. ローカルブランチの削除案内

マージ完了後、以下のメッセージを表示：

```
PRをマージしました。

リモートブランチは自動削除されました。
ローカルブランチを削除する場合は、以下のコマンドを実行してください：

git checkout main
git pull origin main
git branch -d <branch-name>
```

## エラーハンドリング

| 状況 | 対応 |
|------|------|
| PRが見つからない | `Error: PRが見つかりません。PR番号を確認してください。` |
| CIが失敗 | `Warning: CIが失敗しています。/check-ci で詳細を確認してください。マージをスキップします。` |
| CIが実行中 | `Info: CIが実行中です。完了後に再度実行するか、/check-ci で監視してください。` |
| マージ済み | `Info: このPRは既にマージ済みです。` |
| コンフリクト | `Error: マージコンフリクトがあります。コンフリクトを解決してから再度実行してください。` |

## 出力例

### 成功時

```
## PRマージ完了

| 項目 | 値 |
|------|-----|
| PR番号 | #123 |
| タイトル | Add new feature |
| ブランチ | feature/issue-123-xxx |
| マージ先 | main |

リモートブランチは自動削除されました。

### ローカルブランチの削除

git checkout main
git pull origin main
git branch -d feature/issue-123-xxx
```

### CI失敗時

```
## マージスキップ

| 項目 | 値 |
|------|-----|
| PR番号 | #123 |
| 理由 | CIが失敗しています |

次のステップ:
1. /check-ci 123 で詳細を確認
2. 問題を修正してプッシュ
3. CI成功後に /pr-merge 123 を再実行
```

## 関連コマンド

- `/check-ci` - CI結果を確認
- `/pr-create` - PR作成とCI確認
- `/start-issue` - Issue作業開始
- `/review` - コードレビュー
