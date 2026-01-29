# 1 Issue 1 Worktree ワークフロー

各Issueの作業を独立したWorktreeで行い、並列作業時のコンフリクトを防ぎ作業の独立性を保証する。

## 原則: 1 Issue = 1 Worktree（例外なし）

- **すべてのIssue作業において、例外なくWorktreeを使用すること**
- 各Issueは専用のWorktreeで作業する
- 1つのWorktreeで複数のIssueを同時に作業しない
- メインリポジトリ（`D:\projects\P010`）では直接作業せず、Worktreeを使用する

## 標準フロー

以下の順序でIssue作業を行う:

```
/worktree-start {issue番号}     ← 環境準備（Worktree作成）
  ↓
/start-issue {issue番号}         ← 計画立案（実装計画作成・レビュー）
  ↓
/tdd                            ← 実装（テスト駆動開発）
  ↓
/review                         ← レビュー
  ↓
/pr-create                      ← PR作成
  ↓
/pr-merge                       ← マージ＋Worktree自動削除
```

### コマンドの責務

| コマンド | 責務 |
|---------|------|
| `/worktree-start` | 環境準備: Worktreeの作成、環境ファイルの同期 |
| `/start-issue` | 計画立案: Issue理解、実装計画作成、レビュー |
| `/tdd` | 実装: テスト駆動開発サイクル |
| `/review` | 品質確認: コードレビュー |
| `/pr-create` | 提出: PR作成とCI確認 |
| `/pr-merge` | 完了: マージ、Worktree自動削除 |

## Git操作前の必須確認

git操作（commit, branch, status, pushなど）を実行する前に、必ず以下を確認すること：

1. 現在のディレクトリが正しいworktreeであることを確認
2. 現在のブランチが作業対象のブランチであることを確認

**ガード文（必須）**:
```bash
pwd && git branch --show-current
```

## Worktree使用中の禁止事項

- mainリポジトリ（`D:\projects\P010`）でgit操作を行うこと
- cdせずにパス指定でworktree外のファイルを変更すること
- Worktree内で作業中に、パス指定なしで相対パスで操作すること（現在地を忘れた状態での操作）
- **確認なしでgit操作を実行することは禁止**

## Worktree作業の原則

- **Issue作業開始時は、必ずWorktreeディレクトリに移動してから作業を開始すること**
- **git操作を実行する前に、必ず `pwd` と `git branch --show-current` で現在地とブランチを確認すること**
- **確認なしでgit操作を実行することは禁止**

## 禁止事項（一般）

- Worktreeを使わずにIssue作業を行うこと
- メインリポジトリのmainブランチで直接作業すること
- 1つのWorktreeで複数のIssueの変更を混在させること
