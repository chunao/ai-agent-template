# /start-issue - Issue作業開始

指定されたGitHub Issueの作業を開始します。

## 使い方

```
/start-issue 123
```

## ワークフロー全体像

```
1. リモート確認 → 2. Issue取得 → 3. Worktree確認
  ↓
4. 要件確認 → 5. 調査・ブレインストーミング → 6. ナレッジ参照
  ↓
7. 計画作成 → 8. 計画レビュー → 9. 作業開始
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

### 3. Worktree前提チェック

**前提条件**: このコマンドはWorktree環境で実行する必要があります。

> **必須**: ワークフローの原則「1 Issue = 1 Worktree」に従い、すべてのIssue作業は専用のWorktree環境で行います。

#### チェック方法

現在のディレクトリがWorktree内かどうかを確認してください：

**Bash版**:
```bash
# Worktree環境かどうかを判定
current_dir=$(pwd)
if ! git worktree list | grep -q "$current_dir"; then
  echo "エラー: このコマンドはWorktree環境で実行する必要があります"
  echo ""
  echo "次の手順:"
  echo "1. /worktree-start $ARGUMENTS を実行してWorktree環境を作成"
  echo "2. 作成されたWorktree内で /start-issue $ARGUMENTS を再実行"
  exit 1
fi
```

**PowerShell版**:
```powershell
# Worktree環境かどうかを判定
$currentDir = (Get-Location).Path
$worktreeList = git worktree list
if (-not ($worktreeList -match [regex]::Escape($currentDir))) {
  Write-Host "エラー: このコマンドはWorktree環境で実行する必要があります" -ForegroundColor Red
  Write-Host ""
  Write-Host "次の手順:"
  Write-Host "1. /worktree-start $ARGUMENTS を実行してWorktree環境を作成"
  Write-Host "2. 作成されたWorktree内で /start-issue $ARGUMENTS を再実行"
  exit 1
}
```

#### Worktree未作成の場合

Worktreeが未作成の場合は、先に `/worktree-start $ARGUMENTS` を実行してWorktree環境を準備してください。

Worktree環境の作成と環境ファイルの同期は `/worktree-start` の責務です。詳細は `/worktree-start` コマンドを参照してください。

### 4. 要件確認フェーズ

Issueの内容を分析し、未確定・曖昧な部分がないか確認してください。

#### 確認すべき観点

| 観点 | 確認内容 |
|------|---------|
| スコープ | 変更範囲が明確か（何をやる/やらない） |
| アプローチ | 複数の実装方式がありうるか |
| 受け入れ基準 | 完了条件が明確に定義されているか |
| 依存関係 | 他のIssue/機能への影響が不明確でないか |

#### アクション

- 曖昧な点がある場合は**常に** `AskUserQuestion` でユーザーに確認する
- 確認漏れよりも過剰確認を許容する（ユーザー方針）
- 確認結果は後続の計画作成に反映する

### 5. 調査・ブレインストーミングフェーズ

計画作成前に、以下の調査を実施してください。

- **関連コードの調査**: Exploreエージェントで変更対象の構造・パターン・影響範囲を把握
- **複数アプローチの検討**: 実装方式を比較し、80点ルールで最適案を選択
- **外部AIヒアリング**: Codex CLI（優先）またはGemini CLI（フォールバック）で複数視点からのフィードバックを取得。詳細は既存の実装を参考にしてください。
- **フィードバック活用**: AIの提案を参考にし、最終判断はメインエージェントが行う

### 6. ナレッジ参照フェーズ

`knowledge-retrieval` スキルで過去のアーカイブ記事から関連知見を検索してください。詳細は `.claude/skills/knowledge-retrieval/SKILL.md` を参照。

> ステップ4〜6の結果を踏まえて、以下のステップ7で実装計画を作成してください。

> ステップ4〜6の結果を踏まえて、以下のステップ7で実装計画を作成してください。

### 7. 実装計画の作成

以下の形式で実装計画を作成し、**Issueコメントに投稿**してください。

**テンプレート**: `.claude/templates/implementation-plan.md` を参照

> **重要**: ローカルに設計MDファイルを残さない。Issueコメントに一元化する。

### 8. 計画レビュー（2段階）

実装計画を投稿したら、**実装を開始する前に**必ずレビューを行ってください。

#### 計画レビューの実行（必須手順）

##### Step 1: Codex CLI存在確認

**原則として、すべてのレビューはCodex CLIに委任すること。**

まず、Codex CLIの存在を確認します：

```bash
# Windows
where codex 2>nul && echo "Codex CLI available" || echo "Codex CLI not found"
```

- **Codex CLI が存在する場合** → Step 2（Codex委任）へ進む
- **Codex CLI が存在しない場合** → Step 3（Claude Codeフォールバック）へ進む

##### Step 2: Codex委任（原則）

codex-delegateスキルを使用してplan-reviewを実行：

```
codex-delegateスキルを使用して、plan-reviewを実行してください。
対象: Issue #$ARGUMENTS の実装計画
Issue: #$ARGUMENTS
```

##### Step 3: Claude Code サブエージェント（Codex CLI利用不可時のみ）

**Codex CLI利用不可時のみ**以下の手順で実行：

Codex CLI利用不可条件：
- Codex CLIがインストールされていない
- `OPENAI_API_KEY` が設定されていない
- Codex CLI実行がエラーで失敗した

この場合：

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

#### 再採点の必須化ルール

80点未満の場合、以下のルールに従って再採点を実施してください：

| 回数 | 条件 | 対応 |
|------|------|------|
| 1回目が80点未満 | - | **必須**: 指摘事項を修正し、plan-reviewerによる再採点を実行する |
| 2回目も80点未満 | 60点以上 かつ 指摘が軽微 | **任意（AI判断）**: 続行可能。判断理由をIssueコメントに記録する |
| 2回目も80点未満 | 60点未満 または 重大な指摘あり | **必須**: 再度修正し、再採点を実行する |

##### 「軽微な指摘」の判断基準

軽微な指摘の判断基準：重大な仕様欠落・セキュリティリスク・アーキテクチャ上の根本的問題がなく、指摘が文言の曖昧さや詳細度に関するものである場合。

> ⚠️ **禁止事項**: 1回目が80点未満の場合、修正後の再採点をスキップすることは禁止です。

#### レビュー結果をIssueに投稿

レビュー結果を取得したら、**スコアに関わらず**Issueコメントに投稿してください。
修正→再レビューの場合、毎回新規コメントとして投稿されるため、レビュー履歴が自然に蓄積されます。

**テンプレート**: `.claude/templates/plan-review-result.md` を参照

投稿完了後、「計画レビュー結果をIssue #$ARGUMENTS に投稿しました。」と報告してください。

### 9. 作業開始の確認

> **前提条件**: 以下のいずれかを満たしていること。満たさない場合、作業開始レポートは作成できません。
> - 直近のレビュースコアが80点以上である
> - 2回目以降のレビューでAI判断による続行を決定し、判断理由をIssueに記録済みである

**テンプレート**: `.claude/templates/work-start-report.md` を参照

> **重要**: 作業開始レポートを投稿したら、ここで停止してください。実装を開始しないでください。ユーザーの指示を待ち、`/tdd` コマンドが実行された後に実装を開始します。

## 注意事項

- 設計に迷う場合は、3案を比較検討し80点ルールで決定
- 大きなIssueは小さなタスクに分割
- 不明点があればIssueコメントで質問
- **作業開始レポート投稿後は、ユーザーの `/tdd` コマンドを待つこと**
- **PRの作成はユーザーの明示的な指示がある場合のみ実行可能**
- **進捗報告は `/issue-sync` で必ず行うこと（TDD後、review後）**
- **1回目のレビューが80点未満の場合、修正後の再採点を省略してはならない**（「修正したので問題ない」という自己判断での先行禁止）

## 関連コマンド

- `/issue-sync $ARGUMENTS` - 進捗を同期
- `/tdd` - TDDサイクルを開始
- `/review` - コードレビューを実行
- `/pr-create` - PR作成とCI確認
- `/plan` - 詳細な実装計画を立てる
- `/check-ci` - CI結果を確認
- `/pr-merge` - PRマージとブランチ削除
- `/worktree-start` - Worktreeで並列作業開始
- `/worktree-list` - Worktree一覧表示
- `/worktree-clean` - Worktree削除
