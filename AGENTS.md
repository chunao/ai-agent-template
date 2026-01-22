# AGENTS.md - AIエージェント設定

> このファイルはAIエージェント（Claude Code等）がプロジェクトを理解するための設定です。
> プロジェクト開始時に内容を編集してください。

---

## プロジェクト概要

- **プロジェクト名**: AI Agent Development Template
- **リポジトリ**: https://github.com/chunao/ai-agent-template.git
- **テンプレート**: GitHub Template機能が有効（"Use this template"で新規リポジトリ作成可能）
- **概要**: AIエージェント（Claude Code, Codex, Gemini等）を活用した開発のためのプロジェクトテンプレート。docs/の資料に基づくAIエージェント開発フローを完成させ、他プロジェクトで再利用可能なテンプレートを構築する。
- **技術スタック**: Python, uv (パッケージ管理), pytest, Claude Code
- **環境構築**: `uv sync` で依存関係インストール、`uv run pytest` でテスト実行

---

## コア原則

### 1. 品質基準

- **80点ルール**: 80点以上の成果が得られたら前進する
- **テスト駆動開発 (TDD)**: RED → GREEN → REFACTOR サイクルを遵守
- **テストカバレッジ**: 80%以上を目標とする

### 2. セキュリティファースト

- シークレット情報（APIキー、パスワード等）をハードコードしない
- 入力バリデーションを徹底する
- 依存関係の脆弱性に注意する

### 3. コード品質

- 命名規約に従う（言語・フレームワークの慣習に準拠）
- DRY原則（Don't Repeat Yourself）を守る
- 適切なエラーハンドリングを実装する

---

## ワークフロー

### Issue駆動開発サイクル

```
Issue作成 → /start-issue → 実装 → PR作成 → マージ → 次のIssueへ
    ↑                                              ↓
    └──────────────── 新しい作業は新しいIssueから ←─┘
```

**重要**: PRがマージされたら、そのブランチでの作業は終了。新しい作業は必ず新しいIssue/ブランチで開始する。

### 設計フェーズ

1. 既存コードベースを理解する
2. 複数の設計案を検討する（3案程度）
3. 各案のトレードオフを評価する
4. **設計はGitHub Issueコメントに一元化**（ローカルに設計MDを残さない）

### 実装フェーズ

1. タスクを小さな単位にブレイクダウンする
2. チェックリスト形式 `[ ]` で進捗を管理する
3. TDDサイクルに従って実装する
4. こまめにコミットする

### レビューフェーズ

1. セキュリティの観点からチェック
2. パフォーマンスの観点からチェック
3. 保守性の観点からチェック
4. テストカバレッジを確認

### PRマージ後

1. **同じブランチで作業を続けない**
2. 新しい作業が必要な場合は新しいIssueを作成
3. `/start-issue` で新しいブランチを作成して作業開始

---

## 禁止事項

- [ ] ローカルに実装計画・設計のMDファイルを残すこと
- [ ] テストを書かずに実装を進めること
- [ ] ハードコードされたシークレット
- [ ] AIの提案を鵜呑みにすること（総合的に判断する）

---

## ディレクトリ構成

```
.
├── AGENTS.md              # このファイル（AIエージェント設定）
├── README.md              # プロジェクト説明
├── .gitignore
├── .claude/               # Claude Code設定
│   ├── settings.local.json
│   ├── commands/          # クイックコマンド
│   └── rules/             # 常時適用ルール
├── .agent/                # 汎用エージェント設定
│   ├── skills/            # カスタムスキル
│   └── workflows/         # ワークフロー定義
├── docs/                  # ドキュメント
│   └── *.md
├── knowledge/             # ナレッジアーカイブ
│   ├── archive/
│   └── index.json
└── src/                   # ソースコード（プロジェクトに応じて）
```

---

## コマンドリファレンス

### 基本コマンド

| コマンド | 説明 |
|---------|------|
| `/tdd` | TDDサイクルを開始 |
| `/plan` | 実装計画を立てる |
| `/review` | コードレビューを実行 |

### Issue管理

| コマンド | 説明 |
|---------|------|
| `/start-issue <番号>` | Issue作業を開始（ブランチ作成、計画をIssueコメントに記載） |
| `/issue-sync <番号>` | 進捗をIssueコメントに同期 |

---

## 参考リンク

- [docs/ai_agent_development_complete_guide.md](docs/ai_agent_development_complete_guide.md) - 完全ガイド
- [docs/ai_development_best_practices.md](docs/ai_development_best_practices.md) - ベストプラクティス
- [docs/agent_extension_parallel_dev_guide.md](docs/agent_extension_parallel_dev_guide.md) - 並列開発ガイド
