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

## 禁止事項

- Worktreeを使わずにIssue作業を行うこと
- メインリポジトリのmainブランチで直接作業すること
- 1つのWorktreeで複数のIssueの変更を混在させること
