# /worktree-start - Worktreeで並列作業開始

git worktreeを使って新しい作業ディレクトリを作成し、指定したIssueの作業環境を準備します。

> **責務**: このコマンドは「環境準備」を担当します。Worktree作成と環境ファイルの同期を行い、作業環境を分離します。実装計画の作成・レビューは `/start-issue` の責務です。

## 使い方

```
/worktree-start 123
```

## 実行手順

### 1. 事前チェック

```bash
# リモートの最新状態を取得
git fetch origin

# 既存のworktree一覧を確認
git worktree list
```

#### チェックポイント

| 状態 | 対応 |
|------|------|
| 該当Issueのworktreeが存在しない | → 新規作成OK |
| 該当Issueのworktreeが存在する | → エラー（既存のworktreeを使用） |

### 2. Issueの取得と理解

```bash
# Issue情報を取得
gh issue view $ARGUMENTS
```

以下を把握してください：
- タイトルと説明
- ラベル（bug, feature, enhancement等）
- 受け入れ基準（あれば）

### 3. Worktreeディレクトリの作成

#### ディレクトリ構成

```
D:\projects\P010\                    # メインリポジトリ
D:\projects\P010-worktrees\          # worktree用ディレクトリ
  └── issue-{番号}-{スラッグ}\       # 各Issue用
```

#### ブランチ命名規則

`/start-issue` と同じルールに従います：

| prefix | 用途 |
|--------|------|
| `feature/` | 新機能 |
| `fix/` | バグ修正 |
| `refactor/` | リファクタリング |
| `docs/` | ドキュメント |

#### スラッグ生成ルール

Issueタイトルから以下のルールでスラッグを生成：

1. **英語タイトルの場合**
   - 小文字に変換
   - スペースや特殊文字をハイフン `-` に置換
   - 50文字程度に制限

2. **日本語タイトルの場合**
   - 内容を表す英語のスラッグを作成（意訳）

### 4. Worktreeの作成

```bash
# worktree用ディレクトリを作成（存在しない場合）
mkdir -p ../P010-worktrees

# worktreeを作成（mainブランチをベースに新しいブランチを作成）
git worktree add -b {prefix}/issue-$ARGUMENTS-{スラッグ} ../P010-worktrees/issue-$ARGUMENTS-{スラッグ} origin/main
```

#### 成功時の出力

```
Worktreeを作成しました:
- パス: D:\projects\P010-worktrees\issue-$ARGUMENTS-{スラッグ}
- ブランチ: {prefix}/issue-$ARGUMENTS-{スラッグ}
```

### 5. 環境ファイルの同期

`.claude/worktree-sync.yaml` に定義されたファイルをコピーします。

```bash
# .env ファイルをコピー（存在する場合）
cp .env ../P010-worktrees/issue-$ARGUMENTS-{スラッグ}/.env 2>/dev/null || true

# .env.local ファイルをコピー（存在する場合）
cp .env.local ../P010-worktrees/issue-$ARGUMENTS-{スラッグ}/.env.local 2>/dev/null || true

# settings.local.json をコピー（存在する場合）
cp .claude/settings.local.json ../P010-worktrees/issue-$ARGUMENTS-{スラッグ}/.claude/settings.local.json 2>/dev/null || true
```

### 6. 作業開始の案内

```markdown
## Worktree作成完了（環境準備完了）

**Issue**: #$ARGUMENTS
**Worktreeパス**: D:\projects\P010-worktrees\issue-$ARGUMENTS-{スラッグ}
**ブランチ**: {prefix}/issue-$ARGUMENTS-{スラッグ}

### 次のステップ（標準フロー）

1. 新しいターミナルを開く
2. worktreeディレクトリに移動:
   ```bash
   cd D:\projects\P010-worktrees\issue-$ARGUMENTS-{スラッグ}
   ```
3. Claude Codeを起動:
   ```bash
   claude
   ```
4. `/start-issue $ARGUMENTS` で実装計画を作成（計画立案フェーズ）
5. `/tdd` でテスト駆動開発を開始（実装フェーズ）

> **注意**: `/start-issue` は計画立案の責務を持ちます。環境準備は本コマンドで完了しているため、`/start-issue` ではWorktree作成をスキップしてステップ5（実装計画の作成）から開始されます。

### 現在のworktree一覧
`/worktree-list` で確認できます
```

## エラーハンドリング

| 状況 | 対応 |
|------|------|
| Worktreeが既に存在する | 既存のworktreeパスを表示し、そちらで作業を継続するよう案内 |
| ディレクトリ作成失敗 | 権限エラーの場合は手動作成を案内 |
| ブランチが既に存在する | 既存ブランチを使用するか確認 |
| 環境ファイルが存在しない | スキップして続行（警告を表示） |

## 関連コマンド

- `/worktree-list` - worktree一覧を表示
- `/worktree-clean $ARGUMENTS` - worktreeを削除
- `/start-issue $ARGUMENTS` - 通常のIssue作業開始
- `/tdd` - TDDサイクルを開始
