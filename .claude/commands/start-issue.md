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

### 3. Worktree環境の準備

> **必須**: すべてのIssue作業において、例外なくWorktreeを使用してください。
> Worktreeにより作業の独立性が保証され、並列作業時のコンフリクトを防ぎます。

#### Worktree作成済みの場合

既に `/worktree-start $ARGUMENTS` でWorktreeが作成済みの場合は、Worktreeディレクトリに移動してステップ5（実装計画の作成）に進んでください。

```bash
cd D:\projects\P010-worktrees\issue-$ARGUMENTS-{スラッグ}
```

#### Worktree未作成の場合（同一セッション内で作成）

Worktreeが未作成の場合は、同一セッション内で以下の環境準備を実行し、そのまま計画立案を続行してください。

```bash
# 1. リモート最新状態を取得
git fetch origin

# 2. worktree用ディレクトリを作成（存在しない場合）
mkdir -p ../P010-worktrees

# 3. worktreeを作成（ブランチも同時に作成される）
git worktree add -b {prefix}/issue-$ARGUMENTS-{スラッグ} ../P010-worktrees/issue-$ARGUMENTS-{スラッグ} origin/main

# 4. 環境ファイルをコピー（存在しない場合はスキップ、エラーにしない）
cp .env ../P010-worktrees/issue-$ARGUMENTS-{スラッグ}/.env 2>/dev/null || true
cp .env.local ../P010-worktrees/issue-$ARGUMENTS-{スラッグ}/.env.local 2>/dev/null || true
cp .claude/settings.local.json ../P010-worktrees/issue-$ARGUMENTS-{スラッグ}/.claude/settings.local.json 2>/dev/null || true

# 5. ワークディレクトリを変更
cd ../P010-worktrees/issue-$ARGUMENTS-{スラッグ}
```

> **注意**: `git worktree add -b` でブランチは作成済みのため、ステップ4（ブランチの作成）はスキップし、ステップ5（実装計画の作成）に直接進んでください。

### 4. ブランチの作成

```bash
# mainブランチを最新に更新
git checkout main
git pull origin main
```

#### ブランチ命名規則

ブランチ名は `{prefix}/issue-{番号}-{スラッグ}` 形式で作成してください。

| prefix | 用途 |
|--------|------|
| `feature/` | 新機能 |
| `fix/` | バグ修正 |
| `refactor/` | リファクタリング |
| `docs/` | ドキュメント |

#### スラッグ生成ルール

Issueタイトルから以下のルールでスラッグを生成してください：

1. **英語タイトルの場合**
   - 小文字に変換
   - スペースや特殊文字をハイフン `-` に置換
   - 連続するハイフンは1つにまとめる
   - 先頭・末尾のハイフンは削除
   - 50文字程度に制限（単語の区切りで切る）

2. **日本語タイトルの場合**
   - 内容を表す英語のスラッグを作成（意訳）
   - 例: 「ユーザー認証機能を追加」→ `add-user-authentication`

#### 例

| Issueタイトル | ブランチ名 |
|--------------|-----------|
| Add user authentication | `feature/issue-5-add-user-authentication` |
| Fix login validation bug | `fix/issue-10-fix-login-validation-bug` |
| ブランチ名にIssue内容を含める | `feature/issue-6-improve-branch-naming` |

```bash
git checkout -b feature/issue-$ARGUMENTS-{スラッグ}
```

### 5. 実装計画の作成

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

### 6. 計画レビュー（2段階）

実装計画を投稿したら、**実装を開始する前に**必ずレビューを行ってください。

#### Step 1: セルフチェック

以下のチェックリストで自己確認を行います：

| 観点 | チェック項目 | ✅ |
|------|-------------|---|
| 受け入れ基準 | Issueの要件をすべてカバーしているか | |
| タスク粒度 | 各タスクは明確で実行可能か | |
| 影響範囲 | 変更が影響するファイルをすべて把握しているか | |
| テスト計画 | 受け入れ基準に対応するテストがあるか | |
| アーキテクチャ | 既存パターンに従っているか | |

#### Step 2: 計画レビューの実行

セルフチェック後、客観的な視点でのレビューを受けます：

##### 方法1: Codex委任（推奨 - レートリミット対策）

codex-delegateスキルを使用してplan-reviewを実行：

```
codex-delegateスキルを使用して、plan-reviewを実行してください。
対象: Issue #$ARGUMENTS の実装計画
Issue: #$ARGUMENTS
```

##### 方法2: Claude Code サブエージェント（フォールバック）

Codex CLI利用不可時：

```
subagent_type: "general-purpose"
prompt: ".claude/agents/plan-reviewer.md の手順に従って、Issue #$ARGUMENTS の実装計画をレビューしてください。"
```

#### レビュー判定基準

| スコア | 判定 | 次のアクション |
|--------|------|---------------|
| 80点以上 | ✅ 実装開始OK | 作業開始レポートを投稿し、実装を開始 |
| 60-79点 | ⚠️ 要修正 | 指摘事項を修正し、再レビュー |
| 60点未満 | ❌ 計画見直し | 計画を根本から見直す |

> **80点ルール**: 完璧な計画より、素早いフィードバックと改善を優先します。

### 7. 作業開始の確認

```markdown
## 作業開始レポート

**Issue**: #$ARGUMENTS
**ブランチ**: {prefix}/issue-$ARGUMENTS-{スラッグ}
**開始日時**: {現在日時}

### 次のステップ
1. /tdd でテスト駆動開発を開始
2. 進捗は /issue-sync で同期

### PR作成前チェックリスト
- [ ] テストが実行され、すべてパスしていること
- [ ] コード変更がある場合、対応するテストが追加されていること
```

> **重要**: 作業開始レポートを投稿したら、ここで停止してください。実装を開始しないでください。ユーザーの指示を待ち、`/tdd` コマンドが実行された後に実装を開始します。

## 注意事項

- 設計に迷う場合は、3案を比較検討し80点ルールで決定
- 大きなIssueは小さなタスクに分割
- 不明点があればIssueコメントで質問
- **作業開始レポート投稿後は、ユーザーの `/tdd` コマンドを待つこと**
- **PRの作成はユーザーの明示的な指示がある場合のみ実行可能**
- **進捗報告は `/issue-sync` で必ず行うこと（TDD後、review後）**

## 関連コマンド

- `/issue-sync $ARGUMENTS` - 進捗を同期
- `/tdd` - TDDサイクルを開始
- `/plan` - 詳細な実装計画を立てる
- `/check-ci` - CI結果を確認
- `/pr-merge` - PRマージとブランチ削除
- `/worktree-start` - Worktreeで並列作業開始
- `/worktree-list` - Worktree一覧表示
- `/worktree-clean` - Worktree削除
