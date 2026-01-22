# /worktree-clean - Worktree削除

指定したIssueのworktreeを安全に削除します。

## 使い方

```
/worktree-clean 123
/worktree-clean 123 --delete-branch
```

- 引数なし: worktreeのみ削除（ブランチは保持）
- `--delete-branch`: ローカルブランチも削除

## 実行手順

### 1. 対象Worktreeの特定

```bash
# worktree一覧から対象を特定
git worktree list | grep "issue-$ARGUMENTS"
```

#### チェックポイント

| 状態 | 対応 |
|------|------|
| Worktreeが存在しない | エラー（存在しないことを案内） |
| Worktreeが存在する | 削除プロセスを続行 |

### 2. 安全性チェック

削除前に以下を確認します：

#### 2.1 未コミットの変更チェック

```bash
# 未コミットの変更を確認
git -C ../P010-worktrees/issue-$ARGUMENTS-{スラッグ} status --porcelain
```

未コミットの変更がある場合：
```
⚠️ 警告: 未コミットの変更があります

変更ファイル:
- {file1}
- {file2}

削除を続行しますか？
1. はい（変更を破棄）
2. いいえ（中断）
```

#### 2.2 未プッシュのコミットチェック

```bash
# リモートとの差分を確認
git -C ../P010-worktrees/issue-$ARGUMENTS-{スラッグ} log origin/main..HEAD --oneline
```

未プッシュのコミットがある場合：
```
⚠️ 警告: 未プッシュのコミットがあります

未プッシュのコミット:
- abc1234 Add feature
- def5678 Fix bug

削除を続行しますか？
1. はい（プッシュせずに削除）
2. いいえ（中断してプッシュを促す）
```

#### 2.3 PRの状態チェック

```bash
# ブランチ名を取得
BRANCH=$(git -C ../P010-worktrees/issue-$ARGUMENTS-{スラッグ} branch --show-current)

# PRの状態を確認
gh pr list --head "$BRANCH" --state all --json number,state,mergedAt
```

| PR状態 | 対応 |
|--------|------|
| PRなし | 通常の削除確認 |
| Open | 警告を表示（PRがまだオープン） |
| Merged | 安全に削除可能 |
| Closed | 警告を表示（PRがクローズされた） |

### 3. Worktreeの削除

```bash
# worktreeを削除
git worktree remove ../P010-worktrees/issue-$ARGUMENTS-{スラッグ}
```

強制削除が必要な場合（未コミットの変更がある場合）：
```bash
git worktree remove --force ../P010-worktrees/issue-$ARGUMENTS-{スラッグ}
```

### 4. ローカルブランチの削除（オプション）

`--delete-branch` オプションが指定されている場合：

```bash
# ローカルブランチを削除
git branch -d {prefix}/issue-$ARGUMENTS-{スラッグ}
```

マージされていないブランチの場合：
```bash
# 強制削除（確認後）
git branch -D {prefix}/issue-$ARGUMENTS-{スラッグ}
```

### 5. 削除完了の報告

```markdown
## Worktree削除完了

**Issue**: #$ARGUMENTS
**削除したパス**: D:\projects\P010-worktrees\issue-$ARGUMENTS-{スラッグ}
**ブランチ**: {prefix}/issue-$ARGUMENTS-{スラッグ}

### 削除内容
- [x] Worktreeディレクトリ
- [ ] ローカルブランチ（--delete-branch で削除可能）

### 現在のworktree一覧
`/worktree-list` で確認できます
```

`--delete-branch` 指定時：
```markdown
## Worktree削除完了

**Issue**: #$ARGUMENTS
**削除したパス**: D:\projects\P010-worktrees\issue-$ARGUMENTS-{スラッグ}
**ブランチ**: {prefix}/issue-$ARGUMENTS-{スラッグ}

### 削除内容
- [x] Worktreeディレクトリ
- [x] ローカルブランチ

### 現在のworktree一覧
`/worktree-list` で確認できます
```

## エラーハンドリング

| 状況 | 対応 |
|------|------|
| Worktreeが存在しない | エラーメッセージを表示 |
| 削除権限がない | 手動削除を案内 |
| ブランチがmainにマージされていない | 警告を表示し確認を求める |
| PRがまだオープン | 警告を表示し確認を求める |
| ディレクトリが使用中 | プロセスを終了するよう案内 |

## 関連コマンド

- `/worktree-list` - worktree一覧を表示
- `/worktree-start {issue番号}` - 新しいworktreeを作成
- `/pr-merge {PR番号}` - PRをマージ
