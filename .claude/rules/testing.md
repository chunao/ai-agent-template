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

PR作成前にテストを実行すべきかどうかの判断基準です。

| ファイルタイプ | テスト実行 | 備考 |
|--------------|----------|------|
| `*.py`, `*.js`, `*.ts`, `*.jsx`, `*.tsx` | 必須 | コードロジック変更 |
| `.github/workflows/*.yml` | 必須 | CI/CD設定は動作確認必要 |
| `pyproject.toml` | 必須 | 依存関係変更の影響確認 |
| `*.md`, `*.json`, `*.yaml` | 不要 | ドキュメント/設定ファイル |
| `.claude/**/*.md` | 不要 | ワークフロー定義 |

> **注意**: GitHub Actions が `paths` フィルターで自動判定しますが、ローカルでも事前にテストを実行することを推奨します。

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
