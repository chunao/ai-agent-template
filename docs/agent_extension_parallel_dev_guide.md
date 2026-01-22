# AIエージェント拡張機能と並列開発の実践ガイド

Claude Code (Max), ChatGPT Plus (Codex), Gemini (Antigravity) を活用した効率的な開発環境の構築ガイドです。

---

## 🎯 目次

1. [拡張機能の種類と使い分け](#拡張機能の種類と使い分け)
2. [各ツールにおける推奨構成](#各ツールにおける推奨構成)
3. [並列開発のベストプラクティス](#並列開発のベストプラクティス)
4. [Git worktreeを活用した管理戦略](#git-worktreeを活用した管理戦略)
5. [実践的なワークフロー例](#実践的なワークフロー例)

---

## 🔧 拡張機能の種類と使い分け

### 1. WORKFLOW

**定義**: 段階的なタスク実行フローを定義した自動化スクリプト

**特徴**:
- YAML形式で複数ステップを定義
- 各ステップは独立したプロンプトファイルで管理
- 順次実行により、AIの注意力を各ステップに集中

**最適な用途**:

| 用途 | 具体例 |
|------|--------|
| 多観点レビュー | セキュリティ→パフォーマンス→保守性を順次チェック |
| TDDサイクル | Red→Green→Refactorを強制実行 |
| 調査タスク | 課題明確化→ドキュメント調査→ソースコード調査 |
| リファクタリング連鎖 | 不要インポート削除→型定義整理→ロジック共通化 |

**推奨構成例**:

```yaml
# workflows/code-review/workflow.yaml
name: progressive-review
description: 段階的コードレビュー
steps:
  - name: セキュリティチェック
    prompt: prompts/01-security.md
  - name: パフォーマンスチェック
    prompt: prompts/02-performance.md
  - name: 保守性チェック
    prompt: prompts/03-maintainability.md
  - name: テストカバレッジ
    prompt: prompts/04-test-coverage.md
```

> [!TIP]
> **Progressive Workflow**の原則: 複数の指示をまとめて渡すと精度が落ちる。1ステップずつ渡すことでAIの集中力を維持。

---

### 2. SKILL

**定義**: 再利用可能な機能拡張モジュール（コマンド形式で呼び出し可能）

**特徴**:
- SKILL.md (YAMLフロントマター + Markdown本文) で定義
- 単一責任の原則に従う
- プロジェクト横断で再利用可能

**カテゴリ別推奨Skills**:

#### プロジェクト開発向け (5選)

1. **Playwright Browser Automation**
   - E2Eテスト、ログインフロー検証、レスポンシブデザイン確認
   - カスタムコードをその場で記述・実行可能

2. **software-architecture**
   - Clean Architecture、SOLID原則の適用支援
   - アーキテクチャ設計フェーズで有効

3. **subagent-driven-development**
   - タスクごとに独立したサブエージェントを派遣
   - 実装→仕様準拠チェック→コード品質チェックの2段階レビュー

4. **prompt-engineering**
   - カスタムスキル作成、プロンプト最適化
   - Anthropicのベストプラクティスを適用

5. **Kaizen**
   - 継続的改善の哲学をソフトウェアに適用
   - プロセスのボトルネック分析、段階的リファクタリング

#### 普段使い向け (4選)

1. **brainstorming**
   - ラフなアイデアを対話で構造化された設計に変換
   - 一度に一つの質問、2〜3のアプローチを提案

2. **Canvas Design**
   - デザイン哲学を基にビジュアルアート作成 (PNG/PDF)
   - イベントポスター、ブランドアート等

3. **Image Enhancer**
   - 画像・スクリーンショットの解像度・品質向上
   - エッジのシャープ化、テキストの明瞭度向上

4. **ship-learn-next**
   - フィードバックループに基づく次ステップの決定
   - 小さな実験→収集→決定のサイクル

**Skill管理のベストプラクティス**:

```
.claude/
  skills/
    ├── tdd-workflow/        # TDDサイクル
    │   └── SKILL.md
    ├── review-automation/   # レビュー自動化
    │   └── SKILL.md
    └── issue-workflow/      # Issue駆動開発
        └── SKILL.md
```

> [!IMPORTANT]
> **Antigravity と Claude Code でSkillを共有**
> 
> シンボリックリンクを使用してSkill管理を一元化:
> ```powershell
> # Windowsの場合
> mklink /D "C:\Users\<user>\.antigravity\skills" "C:\Users\<user>\.claude\skills"
> ```

---

### 3. MCP (Model Context Protocol)

**定義**: AIエージェントが外部ツール・データソースにアクセスするための標準プロトコル

**特徴**:
- stdio, SSE, HTTPの3種類のトランスポートに対応
- ツールの移植性を確保（OpenAI、Claude、Gemini間で共通利用）
- 認可、ログ、評価、エラーハンドリングを標準化

**主要なMCP用途**:

| 用途 | 具体例 |
|------|--------|
| データアクセス | 社内DB検索、外部API参照 |
| バージョン管理 | GitHub、GitLab連携 |
| クラウドサービス | Supabase、Vercel連携 |
| AI相互連携 | Codex MCPによるセカンドオピニオン |

**MCP実装の最小設計**:

```json
// db_search.request.json
{
  "type": "object",
  "properties": {
    "query": {"type": "string"},
    "filters": {"type": "object"}
  },
  "required": ["query"]
}

// db_search.response.json
{
  "type": "object",
  "properties": {
    "results": {"type": "array"},
    "total_count": {"type": "integer"}
  }
}
```

> [!CAUTION]
> **コンテキストウィンドウ管理**
> 
> MCPを有効化しすぎるとコンテキストが縮小（200K → 70K）。**10個以下**に抑える。

**MCPの使い分け**:

- **Claude Code**: stdio, SSE, HTTP対応
- **Codex**: stdioのみ対応（HTTPエンドポイント型は非対応）
- **Gemini (Antigravity)**: Function Calling経由で実装

---

## 🛠️ 各ツールにおける推奨構成

### Claude Code (Max プラン)

**強み**:
- Hooks、Rewind、Plan Modeなど高度な機能
- MCPの完全サポート (stdio/SSE/HTTP)
- Skillsの豊富なエコシステム

**推奨構成**:

```
.claude/
├── agents/              # 専門エージェント定義
│   ├── reviewer.md      # レビュー専門
│   ├── tester.md        # テスト実行専門
│   └── debugger.md      # デバッグ専門
├── skills/              # 再利用可能なワークフロー
│   ├── tdd-workflow/
│   ├── review-automation/
│   └── issue-workflow/
├── commands/            # クイック実行用コマンド
│   ├── tdd.md           # /tdd
│   ├── plan.md          # /plan
│   └── review.md        # /review
├── rules/               # 常時適用ルール
│   ├── security.md
│   ├── coding-style.md
│   └── testing.md
├── hooks/               # イベント駆動の自動化
│   └── on-file-edit.md
└── mcp/
    └── config.json      # MCP設定
```

**主要コマンド**:

```bash
# Issue駆動開発
/start-issue <番号>      # Issue開始
/issue-sync <番号>       # 進捗同期
/next                    # 次Issue取得

# 品質管理
/tdd                     # TDDサイクル開始
/progressive-review      # 段階的レビュー

# PR管理
/commit-push-pr          # コミット→プッシュ→PR作成
/pr-review-toolkit:review-pr  # PRレビュー
```

**Usage Limits対策**:

Claude Code Maxプランでも制限に達しやすいため、以下の対策を実施:

1. **リミット分散**: 並列タスクは別インスタンスで実行
2. **ハイブリッド運用**: レビュー等の重い処理はCodexに委譲
3. **コンテキスト最適化**: /compactを活用、重要情報はIssueに記録

---

### ChatGPT Plus + Codex

**強み**:
- コスト効率（トークン効率はClaude Opusの約1/10）
- 一発成功率の高さ（クラウドサンドボックスで事前検証）
- 並列処理の自動化（ユーザー設定不要）

**推奨用途**:

| タスク | 理由 |
|--------|------|
| コードレビュー | 決定論的な動作、一貫したレビュー基準 |
| 大量PRの処理 | コスト効率、並列処理 |
| 複雑なバグ調査 | 宣言型タスクに強い、精密な分析 |
| 設計のセカンドオピニオン | リポジトリ全体を読み込み、包括的な評価 |

**Codex MCPによる責務分離型開発**:

```mermaid
graph LR
    A[Codex MCP] -->|設計| B[Issue コメント]
    B --> C[Claude Code]
    C -->|実装| D[GitHub PR]
    D --> E[Codex]
    E -->|レビュー| F{80点以上?}
    F -->|Yes| G[マージ]
    F -->|No| C
```

**プロンプト例**:

```
Codex MCPや複数のMCPを使って調査・まとめ・報告し、
あらゆる観点から評価して点数と理由をつけて返答。
80点以上になったらIssueコメントを更新。

ローカルに実装計画や設計のmdを残すのは禁止。
```

---

### Gemini (Antigravity IDE)

**強み**:
- Skillsのサポート（Claude Codeと共有可能）
- ワークフロー定義の柔軟性
- リミット分散の選択肢として有効

**推奨用途**:

| タスク | 理由 |
|--------|------|
| 複数ファイルにまたがる実装 | AGENT.mdで規約を定義し自動化 |
| 大規模リファクタリング | モード切替で段階的に実行 |
| PR作成までの定型作業 | ブランチ作成→実装→PR作成を一任 |

**AGENTS.md設定例**:

```markdown
# プロジェクト設定

## コア原則
- テスト駆動開発 (TDD) を徹底
- 80%以上のテストカバレッジを必須
- セキュリティファーストの設計

## ワークフロー
1. 開始時と終了時に必ずCodexにレビューさせる
2. 実装計画はIssueコメントに一元化
3. 80点ルールに従って前進

## 禁止事項
- ローカルに実装計画のmdを残すこと
- テストを書かずに実装を進めること
- ハードコードされたシークレット
```

**Skill共有の設定**:

Antigravityのスキルディレクトリを Claude Code と共有:

```powershell
# シンボリックリンク作成（Windows）
mklink /D "C:\Users\<user>\.antigravity\skills" "C:\Users\<user>\.claude\skills"
```

---

## ⚡ 並列開発のベストプラクティス

### 並列開発が必要になるタイミング

- [ ] 複数のGitHub Issueを同時に扱い始めた
- [ ] /compactや/clearの使用頻度が増えてきた
- [ ] コンテキストの混同によるやり直しが頻発
- [ ] 開発速度を3倍にしたい（CCPM活用時）

### 並列開発の3つのアプローチ

#### アプローチ1: CCPM (Claude Code Project Manager)

**特徴**:
- GitHub Issue単位でコンテキスト完全分離
- Git worktreesによる物理的な作業環境分離
- 6,000スター超のOSS、実運用実績豊富

**構成**:

```
PRD (製品要件定義)
  ↓
Epic (技術実装計画)
  ↓
Task (実装タスク)
  ↓
GitHub Issue
  ↓
Code (実装)
```

**主要コマンド**:

```bash
# 初期化
/pm:init

# PRD作成
/pm:prd-new [機能名]

# Epic変換
/pm:prd-parse [機能名]

# タスク分解
/pm:epic-oneshot [機能名]

# Issue処理
/pm:issue-start [Issue番号]
/pm:issue-sync [Issue番号]

# 次タスク取得
/pm:next
```

**メリット**:
- トレーサビリティ: PRD → Epic → Task → Code
- 並列実行: 1 Issue = 複数ワークストリームで最大3倍高速化
- チームコラボ: AIと人間が同一Issue上で協調作業

**デメリット**:
- GitHub Issues必須
- PRD/Epicの管理コスト
- worktree管理の学習コスト

---

#### アプローチ2: Issue Workflow + git worktree

**特徴**:
- TDD強制ワークフロー
- 品質ゲートの自動化
- 並行作業サポート

**セットアップ**:

```bash
# uvのインストール
winget install astral-sh.uv

# Issue Workflowのインストール
uv tool install git+https://github.com/drillan/issue-workflow.git

# プロジェクト初期化
issue-workflow init --language python
```

**並列作業の開始**:

```bash
# Worktree追加
/add-worktree issue#123

# 別ターミナルで別Issue
/add-worktree issue#456
```

**メリット**:
- TDDサイクルの強制
- 品質ツール（lint, format, typecheck）の自動実行
- workflow-config.jsonでカスタマイズ可能

**デメリット**:
- Pythonプロジェクトが中心（他言語は要カスタマイズ）
- 初期セットアップコスト

---

#### アプローチ3: マルチインスタンス運用

**特徴**:
- 複数のAIエージェントインスタンスを同時起動
- ツール間でリミット分散
- 各インスタンスが独立したコンテキストを保持

**運用パターン**:

```mermaid
graph TD
    A[Issue #123] --> B[Claude Code インスタンス1]
    C[Issue #456] --> D[Claude Code インスタンス2]
    E[Issue #789] --> F[Antigravity インスタンス]
    B --> G[worktree/issue-123]
    D --> H[worktree/issue-456]
    F --> I[worktree/issue-789]
```

**ツール配分の推奨**:

| インスタンス | 担当タスク | 理由 |
|-------------|----------|------|
| Claude Code #1 | フロントエンド実装 | Hooks、Plan Modeの活用 |
| Claude Code #2 | バックエンドAPI | TDD Workflow |
| Antigravity | リファクタリング | リミット分散、別モデルの視点 |
| Codex | レビュー・品質チェック | 決定論的、コスト効率 |

**メリット**:
- リミット制限の回避
- 並列処理による高速化
- 各ツールの強みを活用

**デメリット**:
- コンテキストスイッチによる認知負荷
- 複数サブスクリプションのコスト
- 進捗管理の複雑化

---

## 🌳 Git worktreeを活用した管理戦略

### Git worktreeとは

複数のブランチを同時にチェックアウトできる仕組み。Issue単位で独立した作業ディレクトリを作成可能。

### セットアップ

```bash
# プロジェクトルート
cd C:\projects\myapp

# worktreeディレクトリ準備
mkdir ..\myapp-worktrees

# Issue#123用のworktree作成
git worktree add ..\myapp-worktrees\issue-123 -b feature/issue-123

# Issue#456用のworktree作成
git worktree add ..\myapp-worktrees\issue-456 -b feature/issue-456
```

### ディレクトリ構成

```
C:\projects\
├── myapp\                    # メインリポジトリ
│   ├── .git\
│   └── src\
└── myapp-worktrees\          # worktree管理ディレクトリ
    ├── issue-123\            # Issue #123専用
    │   └── src\
    ├── issue-456\            # Issue #456専用
    │   └── src\
    └── issue-789\            # Issue #789専用
        └── src\
```

### 並列開発のワークフロー

```mermaid
sequenceDiagram
    participant Dev as 開発者
    participant C1 as Claude Code #1
    participant C2 as Claude Code #2
    participant Git as Git worktree
    
    Dev->>Git: worktree add issue-123
    Dev->>Git: worktree add issue-456
    
    Dev->>C1: /start-issue 123 (in worktree/issue-123)
    Dev->>C2: /start-issue 456 (in worktree/issue-456)
    
    par Issue #123
        C1->>Git: commit & push feature/issue-123
    and Issue #456
        C2->>Git: commit & push feature/issue-456
    end
    
    Dev->>C1: /commit-push-pr
    Dev->>C2: /commit-push-pr
```

### 管理コマンド集

```bash
# worktree一覧確認
git worktree list

# 特定worktreeで作業
cd ..\myapp-worktrees\issue-123
claude start  # Claude Codeを起動

# 作業完了後、worktree削除
# （PRマージ後に実行）
git worktree remove ..\myapp-worktrees\issue-123

# ブランチも削除
git branch -d feature/issue-123
```

### 注意点とベストプラクティス

> [!WARNING]
> **ディスク容量管理**
> 
> worktreeはリポジトリのコピーを作成するため、ディスク容量に注意。不要なworktreeは定期的に削除。

> [!TIP]
> **依存関係の管理**
> 
> 各worktreeで`npm install`や`pip install`が必要。node_modules等は各worktreeに個別に配置される。

**推奨構成**:

```powershell
# worktree管理スクリプト (PowerShell)

# 新規Issue開始
function Start-IssueWork {
    param($IssueNumber)
    git worktree add "..\myapp-worktrees\issue-$IssueNumber" -b "feature/issue-$IssueNumber"
    cd "..\myapp-worktrees\issue-$IssueNumber"
    # 依存関係インストール
    npm install  # または pip install -r requirements.txt
}

# Issue完了
function Complete-IssueWork {
    param($IssueNumber)
    cd ..\myapp  # メインリポジトリに戻る
    git worktree remove "..\myapp-worktrees\issue-$IssueNumber"
    git branch -d "feature/issue-$IssueNumber"
}
```

---

## 📋 実践的なワークフロー例

### ワークフロー1: CCPM + 並列開発

**シナリオ**: 新機能「ユーザー認証」を3つのIssueに分割して並列開発

```bash
# 1. PRD作成
/pm:prd-new ユーザー認証

# 対話形式で以下を定義:
# - ユーザーストーリー
# - 受け入れ基準
# - 技術的な制約

# 2. Epic変換
/pm:prd-parse ユーザー認証

# 出力例:
# Epic: ユーザー認証システム
# - データベース設計
# - サービスレイヤー実装
# - API実装
# - UI実装
# - テスト

# 3. タスク分解
/pm:epic-oneshot ユーザー認証

# GitHub Issuesに自動登録:
# Issue #123: データベースとサービスレイヤー
# Issue #124: APIエンドポイント
# Issue #125: UIコンポーネント

# 4. 並列開始
# ターミナル1
cd ..\myapp-worktrees\issue-123
/pm:issue-start 123

# ターミナル2
cd ..\myapp-worktrees\issue-124
/pm:issue-start 124

# ターミナル3 (Antigravity)
cd ..\myapp-worktrees\issue-125
# UI実装開始

# 5. 進捗同期（各ターミナルで）
/pm:issue-sync 123
/pm:issue-sync 124

# 6. PRマージ後
Complete-IssueWork 123
Complete-IssueWork 124
Complete-IssueWork 125
```

**開発速度**: 最大3倍（データベース、API、UIを同時並行）

---

### ワークフロー2: 責務分離型 (Codex設計 + Claude実装 + Codexレビュー)

```mermaid
graph TD
    A[1. Codex MCP: 設計] --> B[Issue コメントに記録]
    B --> C[2. Claude Code: 実装]
    C --> D[3. Codex: レビュー]
    D --> E{80点以上?}
    E -->|No| F[Claude Code: 修正]
    F --> D
    E -->|Yes| G[4. Claude Code: PR作成]
    G --> H[5. Codex: 最終レビュー]
    H --> I[マージ]
```

**ステップ詳細**:

**1. Codex MCPで設計**

```
Codex MCPを使って以下を調査・設計:
- 既存アーキテクチャの分析
- 3つの実装案の提案
- 各案のトレードオフ評価
- 推奨案の選定理由

80点以上になったらIssue #XXXのコメントを更新。
ローカルに設計mdは残さない。
```

**2. Claude Codeで実装**

```bash
# Issue開始
/start-issue 123

# TDDワークフロー
/tdd

# 段階的実装
# - テストコード作成（Red）
# - 最小限の実装（Green）
# - リファクタリング（Refactor）
```

**3. Codexでレビュー**

```bash
# Codex CLIでレビュー実行
codex review --issue 123

# 評価基準:
# - アーキテクチャの適切性
# - セキュリティリスク
# - パフォーマンスへの影響
# - 保守性
```

**4. Claude CodeでPR作成**

```bash
/commit-push-pr
```

**5. Codexで最終レビュー**

```bash
codex pr-review --pr 456
```

---

### ワークフロー3: Progressive Workflow + Issue Workflow

**シナリオ**: 既存機能のリファクタリング（段階的レビュー必須）

```bash
# 1. Issue作成
# GitHub上で Issue #789 "支払いモジュールのリファクタリング" を作成

# 2. worktree準備
Start-IssueWork 789

# 3. Issue開始
/start-issue 789

# 4. 段階的リファクタリング (Progressive Workflow)
/progressive-workflow refactoring

# workflow定義:
# Step 1: 不要なインポート削除
# Step 2: 型定義の整理
# Step 3: ロジックの共通化
# Step 4: エラーハンドリングの統一
# Step 5: テストカバレッジの向上

# 5. 各ステップ後に品質チェック
# (Issue Workflowが自動実行)
# - lint
# - format
# - typecheck
# - test

# 6. 段階的レビュー (Progressive Workflow)
/progressive-review

# workflow定義:
# Step 1: セキュリティチェック
# Step 2: パフォーマンスチェック
# Step 3: 保守性チェック
# Step 4: テストカバレッジチェック

# 7. PR作成
/commit-push-pr

# 8. PRレビュー
/pr-review-toolkit:review-pr
```

**メリット**:
- 各ステップでAIの注意力を集中
- 品質ゲートで確実にチェック
- 段階的なコミットで変更履歴が明確

---

## 🚀 導入ロードマップ

### フェーズ1: 基礎環境構築 (Week 1)

- [ ] Claude Code Max プランの契約
- [ ] ChatGPT Plus + Codex の設定
- [ ] Gemini (Antigravity) の設定
- [ ] Git worktree の基本理解
- [ ] AGENTS.md の作成

### フェーズ2: 拡張機能のセットアップ (Week 2)

**Claude Code**:
- [ ] CCPM のインストール (`/pm:init`)
- [ ] Issue Workflow のインストール
- [ ] Progressive Workflow のインストール
- [ ] おすすめSkills 3〜5個の選定・インストール

**Codex**:
- [ ] Codex MCP の設定
- [ ] GitHub CLI の認証

**Antigravity**:
- [ ] Claude Code とSkillの共有設定（シンボリックリンク）
- [ ] AGENTS.md の配置

### フェーズ3: ワークフロー定義 (Week 3)

- [ ] TDD ワークフローの定義
- [ ] Progressive Review ワークフローの定義
- [ ] Issue駆動開発フローの定義
- [ ] workflow-config.json の設定

### フェーズ4: 並列開発の試行 (Week 4)

- [ ] Git worktree の実践
- [ ] 2〜3 Issue での並列開発テスト
- [ ] CCPM の実運用テスト
- [ ] 認知負荷の評価とWIP制限の設定

### フェーズ5: 本格運用 (Week 5〜)

- [ ] チーム全体への展開
- [ ] ベストプラクティスの文書化
- [ ] 継続的な改善サイクルの確立

---

## 📊 効果測定

### KPI設定

| 指標 | 目標 | 測定方法 |
|------|------|----------|
| 開発速度 | 2〜3倍向上 | Issue完了時間の比較 |
| 手戻り削減 | 50%減 | レビュー後の修正回数 |
| コード品質 | テストカバレッジ80%以上 | CI/CDでの自動測定 |
| 認知負荷 | WIP 3以下 | 同時進行タスク数 |
| リミット活用 | Claude Code制限到達を50%減 | 使用量ログの分析 |

---

## ⚠️ よくある失敗と対策

### 失敗1: worktreeの管理ミス

**症状**: ブランチの混乱、マージコンフリクト多発

**対策**:
- worktree管理スクリプトの導入
- 定期的な`git worktree list`によるチェック
- PRマージ後は即座にworktree削除

### 失敗2: コンテキストスイッチの増大

**症状**: 脳の疲労、集中力低下、夕方にパフォーマンス悪化

**対策**:
- WIP制限を3以下に設定
- 1日のうち特定の時間帯は1ツールに集中
- ポモドーロテクニックの導入

### 失敗3: MCP有効化しすぎ

**症状**: コンテキストウィンドウが縮小（200K → 70K）

**対策**:
- MCPは10個以下に制限
- プロジェクトごとに必要なMCPのみ有効化
- `disabledMcpServers`で未使用MCPを無効化

### 失敗4: PRD/Epicの品質が低い

**症状**: トレーサビリティの価値が低下、設計の手戻り

**対策**:
- PRDテンプレートの作成
- Codex MCPによる設計レビューの強制
- Epic作成時に複数案を比較評価

---

## 🎓 まとめ

### WORKFLOW vs SKILL vs MCP

| 拡張機能 | 粒度 | 実行方法 | 最適用途 |
|---------|------|---------|---------|
| **WORKFLOW** | 複数ステップ | 順次実行 | 多観点レビュー、TDDサイクル、段階的リファクタリング |
| **SKILL** | 単一機能 | コマンド呼び出し | ブラウザ自動化、プロンプト最適化、継続的改善 |
| **MCP** | 外部連携 | APIアクセス | DB検索、GitHub連携、クラウドサービス統合 |

### 推奨セットアップ

**Claude Code (Max)**:
- CCPM (並列処理)
- Progressive Workflow (段階的レビュー)
- Issue Workflow (TDD+品質ゲート)
- おすすめSkills 5選

**ChatGPT Plus + Codex**:
- Codex MCP (設計・レビュー)
- 並列処理（自動）
- コスト効率重視の運用

**Gemini (Antigravity)**:
- Skill共有（Claude Codeと）
- リミット分散
- ワークフロー定義

### Git worktree管理

- Issue単位でworktree作成
- 管理スクリプトで自動化
- PRマージ後は即座に削除
- 並列開発で最大3倍の高速化

これらの仕組みを組み合わせることで、**効率的で高品質な並列開発**が実現できます。

---

## 🎁 推奨MCP・SKILLカタログ

### 必須MCP (5選)

#### 1. GitHub MCP

**用途**: GitHub連携、Issue/PR管理、リポジトリ操作

**機能**:
- リポジトリの検索・クローン
- Issue/PRの作成・更新・検索
- コミット履歴の参照
- ブランチ管理

**インストール**:

```json
// ~/.claude/mcp/config.json (Claude Code)
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxx"
      }
    }
  }
}
```

**使用例**:

```
Issue #123 の内容を取得して実装計画を立ててください
PR #456 のレビューコメントに対応してください
```

---

#### 2. Codex MCP

**用途**: セカンドオピニオン、設計レビュー、深い分析

**機能**:
- リポジトリ全体の分析
- 設計案の評価（複数案の比較）
- コードレビュー
- バグ調査

**インストール**:

```json
// ~/.claude/mcp/config.json
{
  "mcpServers": {
    "codex": {
      "command": "codex",
      "args": ["mcp"]
    }
  }
}
```

**使用例**:

```
Codex MCPを使って、この認証システムの設計を3つの案で提案してください。
各案のトレードオフを評価し、推奨案を選定してください。
```

---

#### 3. Filesystem MCP

**用途**: ファイル・ディレクトリ操作、検索

**機能**:
- ファイルの読み書き
- ディレクトリの作成・削除
- ファイル検索
- パス解決

**インストール**:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "D:\\projects"]
    }
  }
}
```

**使用例**:

```
プロジェクト内の全てのTODOコメントを検索してリストアップしてください
```

---

#### 4. Postgres/SQLite MCP

**用途**: データベース連携、スキーマ参照、クエリ実行

**機能**:
- スキーマの取得
- クエリの実行
- データの検索
- マイグレーション支援

**インストール (Postgres)**:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@localhost/dbname"]
    }
  }
}
```

**使用例**:

```
usersテーブルのスキーマを確認して、emailフィールドにインデックスを追加するマイグレーションを作成してください
```

---

#### 5. Web Search MCP (Brave/Google)

**用途**: リアルタイム情報検索、技術調査

**機能**:
- Web検索
- 最新情報の取得
- ドキュメント参照
- ライブラリ比較

**インストール (Brave)**:

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "BSA_xxxxx"
      }
    }
  }
}
```

**使用例**:

```
React 19の新機能を調査して、現在のプロジェクトで活用できる機能をリストアップしてください
```

---

### 推奨MCP (用途別)

#### クラウドサービス連携

**Supabase MCP**
```json
{
  "supabase": {
    "command": "npx",
    "args": ["-y", "supabase-mcp"],
    "env": {
      "SUPABASE_URL": "https://xxx.supabase.co",
      "SUPABASE_KEY": "eyJxxx"
    }
  }
}
```

**Vercel MCP**
```json
{
  "vercel": {
    "command": "npx",
    "args": ["-y", "vercel-mcp"],
    "env": {
      "VERCEL_TOKEN": "xxx"
    }
  }
}
```

#### コミュニケーション

**Slack MCP**
```json
{
  "slack": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-slack"],
    "env": {
      "SLACK_BOT_TOKEN": "xoxb-xxx",
      "SLACK_TEAM_ID": "T123456"
    }
  }
}
```

#### その他

**Memory MCP** (長期記憶)
```json
{
  "memory": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-memory"]
  }
}
```

**Sequential Thinking MCP** (推論強化)
```json
{
  "sequential-thinking": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
  }
}
```

---

### 必須SKILL (10選)

#### 開発ワークフロー系

**1. TDD Workflow**

**機能**: Red-Green-Refactorサイクルの自動化

**インストール**:
```bash
# Claude Code
/plugin marketplace add awesome-claude-skills
/plugin install tdd-workflow
```

**使用例**:
```
/tdd
# 1. テストコード作成 (Red)
# 2. 最小限の実装 (Green)
# 3. リファクタリング (Refactor)
```

---

**2. Progressive Workflow**

**機能**: 段階的タスク実行でAIの集中力を維持

**インストール**:
```bash
/plugin marketplace add 7tsuno/claude-plugins
/plugin install progressive-workflow
```

**ワークフロー定義例**:
```yaml
# workflows/code-review/workflow.yaml
name: progressive-review
description: 段階的コードレビュー
steps:
  - name: セキュリティ
    prompt: prompts/01-security.md
  - name: パフォーマンス
    prompt: prompts/02-performance.md
  - name: 保守性
    prompt: prompts/03-maintainability.md
```

---

**3. Subagent Driven Development**

**機能**: タスクごとに専門サブエージェントを派遣

**特徴**:
- 実装→仕様準拠チェック→コード品質チェックの2段階レビュー
- 並行タスク実行で効率化

**使用例**:
```
この実装計画に基づいて、subagent-driven-developmentで開発してください
```

---

#### ブラウザ・UI系

**4. Playwright Browser Automation**

**機能**: E2Eテスト、ブラウザ自動化

**用途**:
- ログインフローのテスト
- フォーム送信の自動化
- レスポンシブデザイン検証

**使用例**:
```
Playwrightを使って、ログインから商品購入までのE2Eテストを作成してください
```

---

#### 設計・アーキテクチャ系

**5. Software Architecture**

**機能**: Clean Architecture、SOLID原則の適用

**使用例**:
```
このプロジェクトにClean Architectureを適用した設計を提案してください
```

---

**6. Brainstorming**

**機能**: アイデアを対話で構造化

**特徴**:
- 一度に一つの質問
- 選択式優先
- 2〜3のアプローチを提案

**使用例**:
```
/brainstorming
新機能「リアルタイム通知」のアイデアを整理したい
```

---

#### 品質・改善系

**7. Kaizen**

**機能**: 継続的改善のワークフロー

**用途**:
- プロセスのボトルネック分析
- 段階的リファクタリング
- 技術的負債の解消

**使用例**:
```
この支払いモジュールをKaizenアプローチでリファクタリングしてください
```

---

**8. Prompt Engineering**

**機能**: カスタムスキル作成、プロンプト最適化

**用途**:
- サブエージェント設計
- プロンプトのベストプラクティス適用

**使用例**:
```
このタスク用のカスタムスキルを作成してください
```

---

#### レビュー系

**9. Ask Codex / Ask Peer (プラグイン)**

**機能**: セカンドオピニオンの取得

**インストール**:
```bash
claude plugin marketplace add hiroro-work/claude-plugins
claude plugin install ask-codex@hiropon-plugins
claude plugin install peer@hiropon-plugins
```

**使用例**:
```
/ask-codex この実装計画をレビューしてください
/ask-peer OAuth失敗時のフォールバック処理について相談したい
```

---

#### その他

**10. Ship-Learn-Next**

**機能**: フィードバックループに基づく次ステップ決定

**特徴**:
- 小さな実験→フィードバック収集→次のステップ決定

**使用例**:
```
この機能をリリースした後、次に何を学習・開発すべきか提案してください
```

---

### 便利SKILL (追加推奨)

#### Canvas Design

**用途**: ビジュアルアート作成

**機能**:
- デザイン哲学を作成
- それを視覚化 (PNG/PDF)
- 90%ビジュアル、10%テキスト

**使用例**:
```
イベント用のポスターを作成してください
```

---

#### Image Enhancer

**用途**: 画像品質向上

**機能**:
- 解像度のアップスケール
- エッジのシャープ化
- テキストの明瞭度向上

**使用例**:
```
このスクリーンショットの品質を向上させてください
```

---

### SKILL/MCPの選定基準

```mermaid
graph TD
    A[タスク分析] --> B{タスクの種類}
    B -->|外部データアクセス| C[MCP検討]
    B -->|定型ワークフロー| D[WORKFLOW検討]
    B -->|単一機能の拡張| E[SKILL検討]
    
    C --> F{どのデータ?}
    F -->|GitHub| G[GitHub MCP]
    F -->|DB| H[Postgres/SQLite MCP]
    F -->|Web| I[Web Search MCP]
    
    D --> J{何段階?}
    J -->|多観点レビュー| K[Progressive Workflow]
    J -->|TDDサイクル| L[TDD Workflow]
    
    E --> M{何の機能?}
    M -->|ブラウザ操作| N[Playwright]
    M -->|設計支援| O[Software Architecture]
    M -->|改善提案| P[Kaizen]
```

---

### プロジェクトタイプ別推奨構成

#### Webアプリケーション開発

**必須**:
- GitHub MCP
- Filesystem MCP
- TDD Workflow
- Progressive Workflow
- Playwright Browser Automation

**推奨**:
- Supabase MCP (バックエンド)
- Vercel MCP (デプロイ)
- Web Search MCP (技術調査)
- Software Architecture
- Kaizen

---

#### データベース中心アプリ

**必須**:
- GitHub MCP
- Postgres/SQLite MCP
- Filesystem MCP
- TDD Workflow

**推奨**:
- Codex MCP (スキーマレビュー)
- Progressive Workflow
- Software Architecture

---

#### ドキュメント・コンテンツ作成

**必須**:
- Filesystem MCP
- Web Search MCP

**推奨**:
- Canvas Design
- Image Enhancer
- Brainstorming
- Ship-Learn-Next

---

### コンテキストウィンドウ管理戦略

> [!CAUTION]
> **10個ルール**
> 
> MCPは常に10個以下に抑える。200Kのコンテキストが70Kまで縮小するリスクあり。

**優先度付けの例**:

```json
// 高優先度（常時有効）
{
  "mcpServers": {
    "github": {...},           // 1. GitHub連携
    "filesystem": {...},       // 2. ファイル操作
    "codex": {...}            // 3. レビュー
  },
  
  // プロジェクト特化（必要時のみ）
  "disabledMcpServers": {
    "postgres": {...},         // DB作業時のみ有効化
    "supabase": {...},         // バックエンド作業時のみ
    "slack": {...}            // コミュニケーション時のみ
  }
}
```

**プロジェクト切替時の設定変更**:

```bash
# Webアプリ開発時
cp .claude/mcp/webapp-config.json .claude/mcp/config.json

# データベース作業時
cp .claude/mcp/database-config.json .claude/mcp/config.json
```

---

### まとめ: 最小構成から始める

#### スタート地点（5個）

1. **GitHub MCP** - Issue/PR管理
2. **Filesystem MCP** - ファイル操作
3. **TDD Workflow** - テスト駆動開発
4. **Progressive Workflow** - 段階的レビュー
5. **Codex MCP** - セカンドオピニオン

#### 拡張フェーズ（+5個）

6. **Playwright** - E2Eテスト
7. **Software Architecture** - 設計支援
8. **Web Search MCP** - 技術調査
9. **Kaizen** - 継続的改善
10. **Ask Codex/Peer** - 相談役

この構成で、**効率的で高品質な並列開発環境**が整います。
