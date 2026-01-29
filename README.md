# AI Agent Development Template

AIエージェント（Claude Code, Codex, Gemini等）を活用した開発のためのプロジェクトテンプレートです。

**リポジトリ**: https://github.com/chunao/ai-agent-template.git

## クイックスタート

### 1. テンプレートからリポジトリを作成

このリポジトリは **GitHub Template** として公開されています。

```bash
# GitHub CLIを使用（推奨）
gh repo create my-new-project --template chunao/ai-agent-template --private
cd my-new-project

# または、GitHubのWebUIから "Use this template" ボタンをクリック
```

### 2. 開発環境のセットアップ

```bash
# uvをインストール（未インストールの場合）
# Windows: winget install astral-sh.uv
# macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係をインストール
uv sync

# テストを実行して動作確認
uv run pytest
```

### 3. プロジェクト設定を編集

1. **AGENTS.md** を開いてプロジェクト情報を記入
2. **README.md** をプロジェクト固有の内容に書き換え
3. **pyproject.toml** のプロジェクト名・説明を更新

### 4. 開発開始

```bash
# Claude Codeを起動
claude

# 利用可能なコマンド
/start-issue 123  # Issue作業を開始
/tdd              # TDDサイクルを開始
/issue-sync 123   # 進捗を同期
/review           # コードレビューを実行
/plan             # 実装計画を立てる
```

---

## ディレクトリ構成

```
.
├── AGENTS.md                 # AIエージェント設定（必ず編集）
├── README.md                 # このファイル（プロジェクト用に書き換え）
├── .gitignore                # Git除外設定
│
├── .claude/                  # Claude Code設定
│   ├── settings.local.json   # ローカル設定
│   ├── agents/               # 専門エージェント定義
│   │   ├── reviewer.md       # レビュー専門
│   │   ├── tester.md         # テスト専門
│   │   └── debugger.md       # デバッグ専門
│   ├── commands/             # クイックコマンド
│   │   ├── tdd.md            # /tdd
│   │   ├── plan.md           # /plan
│   │   ├── review.md         # /review
│   │   ├── start-issue.md    # /start-issue
│   │   └── issue-sync.md     # /issue-sync
│   ├── templates/            # テンプレートファイル
│   │   ├── implementation-plan.md      # 実装計画
│   │   ├── plan-review-result.md       # 計画レビュー結果
│   │   └── work-start-report.md        # 作業開始レポート
│   ├── mcp/                  # MCP設定
│   │   ├── config.example.json  # 設定テンプレート
│   │   └── README.md         # MCP設定ガイド
│   ├── rules/                # 常時適用ルール
│   │   ├── security.md
│   │   ├── coding-style.md
│   │   └── testing.md
│   └── skills/               # カスタムスキル
│       ├── progressive-review/  # 段階的レビュー
│       └── tdd-cycle/        # TDDサイクル
│
├── .agent/                   # 汎用エージェント設定
│   ├── skills/               # 共有スキル
│   │   ├── skill-creator/    # スキル作成支援
│   │   ├── url-archiver/     # URL記事アーカイブ
│   │   ├── claude-runner/    # Claude実行
│   │   └── knowledge-retriever/  # ナレッジ検索
│   └── workflows/            # ワークフロー定義（空）
│
├── docs/                     # ドキュメント
│   ├── ai_agent_development_complete_guide.md
│   ├── ai_development_best_practices.md
│   └── agent_extension_parallel_dev_guide.md
│
└── knowledge/                # ナレッジアーカイブ
    ├── archive/              # アーカイブ記事
    └── index.json            # インデックス
```

---

## 含まれるもの

### 専門エージェント (.claude/agents/)

| エージェント | 説明 |
|-------------|------|
| reviewer.md | コードレビュー専門（セキュリティ、パフォーマンス、保守性を多角評価） |
| tester.md | テスト作成・実行専門（TDD、カバレッジ分析） |
| debugger.md | バグ調査・修正専門（根本原因分析、5 Whys手法） |

### コマンド (.claude/commands/)

| コマンド | 説明 |
|---------|------|
| `/tdd` | TDD (Red-Green-Refactor) サイクルを実行 |
| `/plan` | 実装計画を立てる（3案比較、80点ルール） |
| `/review` | 段階的コードレビュー（セキュリティ、パフォーマンス、保守性、テスト） |
| `/start-issue <番号>` | Issue作業を開始（ブランチ作成、計画をIssueコメントに記載） |
| `/issue-sync <番号>` | 進捗をIssueコメントに同期 |

### ルール (.claude/rules/)

| ルール | 説明 |
|--------|------|
| security.md | セキュリティ関連のルール |
| coding-style.md | コーディングスタイルのルール |
| testing.md | テスト関連のルール |

### MCP設定 (.claude/mcp/)

| ファイル | 説明 |
|---------|------|
| config.example.json | MCP設定テンプレート（GitHub, Filesystem, Codex等） |
| README.md | MCP設定ガイド（セットアップ手順、注意事項） |

### スキル

#### .claude/skills/ (Claude Code専用)

| スキル | 説明 |
|--------|------|
| progressive-review | 段階的コードレビュー（4観点を順次チェック） |
| tdd-cycle | TDDサイクル（Red-Green-Refactor強制実行） |

#### .agent/skills/ (汎用・共有)

| スキル | 説明 |
|--------|------|
| skill-creator | 新しいスキルを作成するための支援 |
| url-archiver | Web記事をナレッジとしてアーカイブ |
| knowledge-retriever | アーカイブしたナレッジを検索・参照 |

---

## ドキュメント

詳細なガイドは `docs/` ディレクトリを参照してください：

- **ai_agent_development_complete_guide.md** - AIエージェント活用開発の完全ガイド
- **ai_development_best_practices.md** - ベストプラクティス集
- **agent_extension_parallel_dev_guide.md** - 拡張機能と並列開発のガイド

---

## 開発原則

### 80点ルール

80点以上の成果が得られたら前進する。完璧主義を追求しすぎない。

### TDD (テスト駆動開発)

1. RED - 失敗するテストを書く
2. GREEN - テストを通す最小限のコードを書く
3. REFACTOR - コードを改善する

### セキュリティファースト

- シークレットをハードコードしない
- 入力バリデーションを徹底する
- 依存関係の脆弱性に注意する

---

## ライセンス

<!-- TODO: ライセンスを指定 -->
