# AI Agent Development Template

AIエージェント（Claude Code, Codex, Gemini等）を活用した開発のためのプロジェクトテンプレートです。

## クイックスタート

### 1. テンプレートをコピー

```bash
# 新規プロジェクトディレクトリを作成
mkdir my-new-project
cd my-new-project

# テンプレートの内容をコピー（.gitを除く）
cp -r /path/to/this-template/* .
cp -r /path/to/this-template/.* . 2>/dev/null || true

# Gitを初期化
git init
```

### 2. プロジェクト設定を編集

1. **AGENTS.md** を開いてプロジェクト情報を記入
2. **README.md** をプロジェクト固有の内容に書き換え

### 3. 開発開始

```bash
# Claude Codeを起動
claude

# 利用可能なコマンド
/tdd      # TDDサイクルを開始
/plan     # 実装計画を立てる
/review   # コードレビューを実行
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
│   ├── commands/             # クイックコマンド
│   │   ├── tdd.md            # /tdd
│   │   ├── plan.md           # /plan
│   │   └── review.md         # /review
│   ├── rules/                # 常時適用ルール
│   │   ├── security.md
│   │   ├── coding-style.md
│   │   └── testing.md
│   └── skills/               # カスタムスキル（空）
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

### コマンド (.claude/commands/)

| コマンド | 説明 |
|---------|------|
| `/tdd` | TDD (Red-Green-Refactor) サイクルを実行 |
| `/plan` | 実装計画を立てる（3案比較、80点ルール） |
| `/review` | 段階的コードレビュー（セキュリティ、パフォーマンス、保守性、テスト） |

### ルール (.claude/rules/)

| ルール | 説明 |
|--------|------|
| security.md | セキュリティ関連のルール |
| coding-style.md | コーディングスタイルのルール |
| testing.md | テスト関連のルール |

### スキル (.agent/skills/)

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
