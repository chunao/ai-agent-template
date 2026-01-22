# /worktree-list - Worktree一覧表示

現在のworktree一覧と各worktreeの状態を表示します。

## 使い方

```
/worktree-list
```

## 実行手順

### 1. Worktree一覧の取得

```bash
# worktree一覧を取得
git worktree list
```

### 2. 各Worktreeの詳細情報を取得

各worktreeについて以下の情報を収集します：

```bash
# 各worktreeのディレクトリで以下を実行
# ブランチ名
git -C {worktree-path} branch --show-current

# 最新コミット情報
git -C {worktree-path} log -1 --format="%h %s (%cr)"

# 未コミットの変更
git -C {worktree-path} status --porcelain
```

### 3. 出力フォーマット

```markdown
## Worktree一覧

| # | パス | ブランチ | 最新コミット | 状態 |
|---|------|---------|------------|------|
| 1 | D:\projects\P010 (main) | main | abc1234 Initial commit (2 days ago) | クリーン |
| 2 | D:\projects\P010-worktrees\issue-7-xxx | feature/issue-7-xxx | def5678 Add feature (1 hour ago) | 変更あり |
| 3 | D:\projects\P010-worktrees\issue-8-yyy | fix/issue-8-yyy | ghi9012 Fix bug (30 min ago) | クリーン |

### 状態の説明

| 状態 | 意味 |
|------|------|
| クリーン | 未コミットの変更なし |
| 変更あり | 未コミットの変更あり |
| ステージ済み | ステージ済みの変更あり |

### アクション

- 特定のworktreeで作業を開始: 該当ディレクトリでClaude Codeを起動
- worktreeを削除: `/worktree-clean {issue番号}`
- 新しいworktreeを作成: `/worktree-start {issue番号}`
```

### 4. 関連PR/Issue情報（オプション）

Issue番号がブランチ名に含まれている場合、関連情報を表示：

```bash
# Issue番号を抽出
ISSUE_NUM=$(echo "$BRANCH" | grep -oE 'issue-[0-9]+' | grep -oE '[0-9]+')

# Issue情報を取得
gh issue view $ISSUE_NUM --json title,state -q '"\(.title) (\(.state))"'

# PR情報を取得
gh pr list --head "$BRANCH" --json number,state -q '.[0] | "PR #\(.number) (\(.state))"'
```

### 5. 拡張出力フォーマット

```markdown
## Worktree一覧（詳細）

### 1. メインリポジトリ
- **パス**: D:\projects\P010
- **ブランチ**: main
- **最新コミット**: abc1234 Initial commit (2 days ago)
- **状態**: クリーン

### 2. Issue #7 - Add new feature
- **パス**: D:\projects\P010-worktrees\issue-7-add-new-feature
- **ブランチ**: feature/issue-7-add-new-feature
- **最新コミット**: def5678 Add feature (1 hour ago)
- **状態**: 変更あり
- **Issue**: #7 - Add new feature (OPEN)
- **PR**: なし

### 3. Issue #8 - Fix login bug
- **パス**: D:\projects\P010-worktrees\issue-8-fix-login-bug
- **ブランチ**: fix/issue-8-fix-login-bug
- **最新コミット**: ghi9012 Fix bug (30 min ago)
- **状態**: クリーン
- **Issue**: #8 - Fix login bug (OPEN)
- **PR**: #15 (OPEN)
```

## エラーハンドリング

| 状況 | 対応 |
|------|------|
| worktreeが存在しない | メインリポジトリのみ表示 |
| worktreeディレクトリがアクセス不可 | 警告を表示しスキップ |
| git情報取得失敗 | 「情報取得失敗」と表示 |

## 関連コマンド

- `/worktree-start {issue番号}` - 新しいworktreeを作成
- `/worktree-clean {issue番号}` - worktreeを削除
- `/start-issue {issue番号}` - 通常のIssue作業開始
