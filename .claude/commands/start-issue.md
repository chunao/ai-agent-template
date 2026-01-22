# /start-issue - Issue作業開始

指定されたGitHub Issueの作業を開始します。

## 使い方

```
/start-issue 123
```

## 実行手順

### 1. リモート状態の確認（重要）

**作業開始前に必ずリモートの状態を確認してください。**

```bash
# リモートの最新状態を取得
git fetch origin

# 現在のブランチとリモートの状態を確認
git branch -a

# 既存のPR状態を確認
gh pr list --state all | grep "issue-$ARGUMENTS"
```

#### チェックポイント

| 状態 | 対応 |
|------|------|
| 該当ブランチが存在しない | → 新規作成OK |
| ブランチが存在 & PRなし | → 既存ブランチを確認し、必要なら削除して新規作成 |
| ブランチが存在 & PRがOpen | → 既存PRで作業を継続するか確認 |
| ブランチが存在 & PRがMerged | → ⚠️ **新しいIssue/ブランチで作業すべき** |

> **警告**: PRがマージ済みのブランチで作業を続けると、変更がmainに反映されません。必ず新しいブランチを作成してください。

### 2. Issueの取得と理解

GitHub Issue #$ARGUMENTS の内容を取得し、以下を把握してください：

- タイトルと説明
- ラベル（bug, feature, enhancement等）
- 受け入れ基準（あれば）
- 関連するIssueやPR

### 3. ブランチの作成

```bash
# mainブランチを最新に更新
git checkout main
git pull origin main

# ブランチ命名規則
# feature/issue-{番号}  - 新機能
# fix/issue-{番号}      - バグ修正
# refactor/issue-{番号} - リファクタリング

git checkout -b feature/issue-$ARGUMENTS
```

### 4. 実装計画の作成

以下の形式で実装計画を作成し、**Issueコメントに投稿**してください：

```markdown
## 実装計画

### 概要
{このIssueで何を実現するか}

### 設計方針
{選択したアプローチとその理由}

### タスク
- [ ] {タスク1}
- [ ] {タスク2}
- [ ] {タスク3}

### 影響範囲
- {変更するファイル/モジュール}

### テスト計画
- [ ] {テスト項目1}
- [ ] {テスト項目2}
```

> **重要**: ローカルに設計MDファイルを残さない。Issueコメントに一元化する。

### 5. 作業開始の確認

```markdown
## 作業開始レポート

**Issue**: #$ARGUMENTS
**ブランチ**: feature/issue-$ARGUMENTS
**開始日時**: {現在日時}

### 次のステップ
1. /tdd でテスト駆動開発を開始
2. 進捗は /issue-sync で同期
```

## 注意事項

- 設計に迷う場合は、3案を比較検討し80点ルールで決定
- 大きなIssueは小さなタスクに分割
- 不明点があればIssueコメントで質問

## 関連コマンド

- `/issue-sync $ARGUMENTS` - 進捗を同期
- `/tdd` - TDDサイクルを開始
- `/plan` - 詳細な実装計画を立てる
