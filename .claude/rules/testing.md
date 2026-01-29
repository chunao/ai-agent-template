# テストルール

以下のテストルールを遵守してください。

## 基本原則

### TDD (テスト駆動開発)

1. **RED**: まず失敗するテストを書く
2. **GREEN**: テストを通す最小限のコードを書く
3. **REFACTOR**: コードを改善する

### テストカバレッジ

- **目標**: 80%以上
- **必須**: 重要なビジネスロジック
- **推奨**: ユーティリティ関数、エッジケース

## テストの書き方

### 命名規則

```
test_<テスト対象>_<条件>_<期待結果>
```

例: `test_user_login_with_valid_credentials_returns_token`

### AAA パターン

```python
def test_example():
    # Arrange - 準備
    user = create_test_user()

    # Act - 実行
    result = user.login("password")

    # Assert - 検証
    assert result.is_success
```

### テストの独立性

- 各テストは他のテストに依存しない
- テストの実行順序に依存しない
- 共有状態を避ける

## テストの種類

| 種類 | 目的 | カバレッジ目標 |
|------|------|---------------|
| 単体テスト | 個々の関数・メソッド | 80%以上 |
| 統合テスト | モジュール間連携 | 重要パス |
| E2Eテスト | ユーザーシナリオ | クリティカルパス |

## テスト要否の判断基準

### 新規テスト作成の要否

新しいコードやワークフロー定義を追加した際に、新規テストを作成すべきかどうかの判断基準です。

| ファイルタイプ | 新規テスト作成 | 備考 |
|--------------|---------------|------|
| `*.py`, `*.js`, `*.ts`, `*.jsx`, `*.tsx` | 必須 | コードロジック変更には対応するテストが必要 |
| `.github/workflows/*.yml` | 推奨 | CI/CD設定の動作を検証するテスト |
| `pyproject.toml` | 不要 | 依存関係のみの変更 |
| `*.md`, `*.json`, `*.yaml` | 不要 | ドキュメント/設定ファイル |
| `.claude/**/*.md` | 推奨 | ワークフロー定義の整合性を検証するテスト（下記「変更影響マップ」参照） |

### 既存テスト実行の要否（PR作成前）

PR作成前に既存テストを実行すべきかどうかの判断基準です。

| 状況 | 既存テスト実行 | 備考 |
|------|--------------|------|
| **すべての変更** | **必須** | 影響範囲が予見できないため、全テスト実行を推奨 |
| **例外1**: ドキュメントのみ変更（typo修正等） | 任意 | ただし、ワークフロー定義（`.claude/**/*.md`）は除く |
| **例外2**: コメントのみ変更 | 任意 | コードの動作に影響しない変更 |

> **重要**: 上記「例外」に該当する場合でも、**関連テストの存在を確認**し、影響がないことを確認してください。不明な場合は全テスト実行を推奨します。

> **注意**: GitHub Actions が `paths` フィルターで自動判定しますが、ローカルでも事前にテストを実行することを推奨します。

### 変更影響マップ

ワークフロー定義ファイル（`.claude/**/*.md`）と関連テストファイルの対応関係です。これらのファイルを変更した場合、対応するテストファイルを実行してください。

| 変更ファイル | 影響を受けるテスト | 理由 |
|------------|------------------|------|
| `.claude/commands/start-issue.md` | `tests/test_worktree_workflow.py` | Worktreeフローの整合性を検証 |
| `.claude/commands/worktree-start.md` | `tests/test_worktree_workflow.py` | Worktreeフローの整合性を検証 |
| `.claude/commands/pr-merge.md` | `tests/test_pr_merge_command.py` | PRマージコマンドの動作を検証 |
| `.claude/commands/check-ci.md` | `tests/test_check_ci_command.py` | CI確認コマンドの動作を検証 |
| `.claude/skills/ci-analyzer/*.md` | `tests/test_ci_analyzer_skill.py` | CI分析スキルの動作を検証 |
| `.claude/agents/ci-fixer.md` | `tests/test_ci_fixer_agent.py` | CI修正エージェントの動作を検証 |
| `.claude/agents/plan-reviewer.md` | `tests/test_review_assignment.py` | レビューアサインメントの整合性を検証 |
| `.claude/agents/reviewer.md` | `tests/test_review_assignment.py` | レビューアサインメントの整合性を検証 |
| `.claude/skills/tdd-cycle/*.md` | `tests/test_review_assignment.py`, `tests/test_issue_number_context_extraction.py` | TDDサイクルの動作を検証 |
| `.claude/skills/progressive-review/*.md` | `tests/test_review_assignment.py` | プログレッシブレビューの動作を検証 |
| `.claude/rules/review-assignment-guide.md` | `tests/test_review_assignment.py` | レビューアサインメントの整合性を検証 |

> **使用方法**: 上記のファイルを変更した場合、対応するテストファイルを実行してください。影響範囲が不明な場合は、全テスト（`pytest`）を実行してください。

## 動作確認（テスト不要ファイル向け）

テストコードが不要なファイル（Markdown、YAML、JSON等）を変更した場合は、自動テストの代わりに以下の動作確認を実施してください。

> **適用条件**: 変更ファイルがすべて「テスト不要」に該当する場合に適用。テスト必須ファイルが1つでも含まれる場合は通常のTDDサイクルを実行すること。

### コマンド定義ファイル（`.claude/commands/*.md`, `.claude/skills/**/*.md`）

- [ ] Markdown構文エラーがない（見出し・リスト・テーブルの記法）
- [ ] 定義されたコマンド/スキルの手順が論理的に正しい
- [ ] 参照するファイルパスが正しい
- [ ] 関連コマンド/スキルとの整合性がある
- [ ] 出力フォーマットが既存のパターンと統一されている

### 設定ファイル（`*.yaml`, `*.yml`, `*.json`）

- [ ] 構文エラーがない（YAML/JSONバリデーション）
- [ ] 参照するファイルパスが正しい
- [ ] 既存機能に影響がない
- [ ] デフォルト値や必須項目が適切に設定されている

### ドキュメントファイル（`*.md` - ルール/ガイドライン）

- [ ] 記述内容が既存のルールと矛盾しない
- [ ] 参照リンク・パスが正しい
- [ ] 判断基準やテーブルが他のドキュメントと整合している

### 動作確認結果の記録

動作確認完了後、以下の形式でIssueコメントに投稿してください：

```markdown
## 動作確認結果 - {日時}

### 変更ファイル
- {ファイル1}
- {ファイル2}

### チェック結果
- [x] {確認項目1}
- [x] {確認項目2}
- [x] {確認項目3}

### 確認方法
- {どのように確認したか}

### 判定: ✅ 確認完了
```

## 禁止事項

- テストなしで実装を進めること
- テストをスキップしたままマージすること
- 本番データを使ったテスト

## CI拡張ガイド

新しい言語やフレームワークをプロジェクトに追加する際のガイドです。

### 新言語追加時のチェックリスト

新しい言語を追加する場合は、以下の項目を確認してください：

| ステップ | 作業内容 | 確認 |
|---------|---------|------|
| 1 | `.github/workflows/test.yml` の `paths` フィルターに拡張子を追加 | ☐ |
| 2 | テスト実行ステップを追加 | ☐ |
| 3 | 依存関係のセットアップステップを追加 | ☐ |
| 4 | ローカルでテスト実行を確認 | ☐ |

### test.yml の更新方法

#### 1. paths フィルターの更新

```yaml
paths:
  # 既存
  - "**/*.py"
  - "**/*.js"
  - "**/*.ts"
  # 新言語を追加
  - "**/*.go"    # Go
  - "**/*.rs"    # Rust
```

#### 2. テストステップの追加

既存の Python テストステップの後に、新言語のテストステップを追加します：

```yaml
steps:
  # ... 既存のPythonテスト ...

  # JavaScript/TypeScript テスト（例）
  - name: Setup Node.js
    uses: actions/setup-node@v4
    with:
      node-version: '20'
    if: hashFiles('package.json') != ''

  - name: Install npm dependencies
    run: npm ci
    if: hashFiles('package.json') != ''

  - name: Run npm test
    run: npm test
    if: hashFiles('package.json') != ''
```

#### 3. 条件付き実行

`if` 条件を使用して、該当ファイルが存在する場合のみステップを実行することを推奨します：

```yaml
if: hashFiles('package.json') != ''  # package.json がある場合のみ実行
if: hashFiles('go.mod') != ''        # go.mod がある場合のみ実行
if: hashFiles('Cargo.toml') != ''    # Cargo.toml がある場合のみ実行
```

### 言語別テストコマンド一覧

| 言語 | パッケージマネージャ | テストコマンド | セットアップAction |
|------|---------------------|---------------|-------------------|
| Python | uv | `uv run pytest` | `astral-sh/setup-uv@v3` |
| JavaScript/TypeScript | npm | `npm test` | `actions/setup-node@v4` |
| Go | go modules | `go test ./...` | `actions/setup-go@v5` |
| Rust | cargo | `cargo test` | `dtolnay/rust-toolchain@stable` |

### 現在の対応状況

| 言語 | paths検知 | テスト実行 | 状態 |
|------|----------|-----------|------|
| Python | ✅ | ✅ | 完全対応 |
| JavaScript | ✅ | ❌ | 検知のみ |
| TypeScript | ✅ | ❌ | 検知のみ |

> **注意**: JavaScript/TypeScript は paths フィルターで検知されますが、テストステップは未実装です。JS/TS コードを追加する際は、テストステップも追加してください。
