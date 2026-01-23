# 1 Issue 1 Worktree ワークフロー

各Issueの作業を独立したWorktreeで行い、並列作業時のコンフリクトを防ぎ作業の独立性を保証する。

## 原則: 1 Issue = 1 Worktree

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

## 例外ケース（Worktreeを使わない場合）

以下の場合はWorktreeなしの通常ブランチ作業でも可:

- 単一ファイルの軽微な修正（typo修正、コメント追加等）
- ドキュメントのみの変更
- 並列作業の予定がない単独Issue
- CI/CD設定ファイルのみの変更

> これらの例外ケースでも、`/start-issue` の通常ブランチ作成フローを使用可能。

## 禁止事項

- メインリポジトリのmainブランチで直接作業すること
- 1つのWorktreeで複数のIssueの変更を混在させること
- Worktreeを作成せずに複数Issueを並列作業すること
