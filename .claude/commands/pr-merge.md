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

### 4. ローカルブランチの自動削除

マージ完了後、ローカルブランチを自動削除します。

#### 4.1. ブランチ名の取得

ステップ1で取得した `headRefName` を使用します。

#### 4.2. worktreeの存在確認

```bash
# 対象ブランチがworktreeで使用されているか確認
git worktree list | grep <branch-name>
```

#### 4.3. worktreeの削除（存在する場合）

worktreeが存在する場合は、ブランチ削除前にworktreeを削除します。

```bash
# worktreeを削除
git worktree remove <worktree-path>
```

#### 4.4. mainブランチへの切り替え

現在のブランチが削除対象の場合、またはローカルmainを最新化するために実行します。

```bash
# mainに切り替え（現在ブランチが対象の場合）
git checkout main

# mainを最新化（git branch -d の成功に必要）
git pull origin main
```

#### 4.5. ローカルブランチの削除

```bash
# 安全な削除（マージ済みブランチのみ削除可能）
git branch -d <branch-name>
```

#### 4.6. 削除結果の報告

削除が成功した場合、結果をユーザーに報告します。

## エラーハンドリング

| 状況 | 対応 |
|------|------|
| PRが見つからない | `Error: PRが見つかりません。PR番号を確認してください。` |
| CIが失敗 | `Warning: CIが失敗しています。/check-ci で詳細を確認してください。マージをスキップします。` |
| CIが実行中 | `Info: CIが実行中です。完了後に再度実行するか、/check-ci で監視してください。` |
| マージ済み | `Info: このPRは既にマージ済みです。` |
| コンフリクト | `Error: マージコンフリクトがあります。コンフリクトを解決してから再度実行してください。` |
| ローカルブランチ削除に失敗 | `Warning: ローカルブランチの削除に失敗しました。手動で削除してください: git branch -d <branch-name>` |
| worktree削除に失敗 | `Warning: worktreeの削除に失敗しました。手動で削除してください: git worktree remove <path>` |

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
ローカルブランチを自動削除しました: feature/issue-123-xxx
```

### 成功時（worktree使用中）

```
## PRマージ完了

| 項目 | 値 |
|------|-----|
| PR番号 | #123 |
| タイトル | Add new feature |
| ブランチ | feature/issue-123-xxx |
| マージ先 | main |

リモートブランチは自動削除されました。
worktreeを削除しました: D:\projects\P010-worktrees\issue-123-xxx
ローカルブランチを自動削除しました: feature/issue-123-xxx
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
- `/worktree-clean` - worktreeの手動管理
