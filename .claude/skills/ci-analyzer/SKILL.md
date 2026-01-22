---
name: ci-analyzer
description: CI失敗ログの解析と分析を行うスキルです。GitHub Actionsのログを取得し、エラーパターンを識別して原因を特定します。失敗原因をカテゴリ別に整理し、具体的な対処法を推奨します。
---

# CI Analyzer Skill

## Overview

GitHub Actions の CI 失敗時にログを取得・解析し、失敗原因を特定するスキルです。

## Workflow Steps

### Step 1: ログの取得

```bash
# 失敗したワークフロー実行のログを取得
gh run view <run-id> --log

# 失敗したジョブのみのログを取得
gh run view <run-id> --log-failed

# 特定ジョブのログを取得
gh run view <run-id> --log --job <job-id>
```

### Step 2: エラーパターンの識別

ログを解析し、以下のカテゴリに分類します。

#### エラーカテゴリ

| カテゴリ | パターン | 例 |
|---------|---------|-----|
| テスト失敗 | `FAILED`, `AssertionError`, `pytest` | テストケースの失敗 |
| 構文エラー | `SyntaxError`, `IndentationError` | Python構文エラー |
| 型エラー | `TypeError`, `Type error` | 型不一致 |
| 依存関係エラー | `ModuleNotFoundError`, `ImportError` | モジュール未インストール |
| ビルドエラー | `Build failed`, `Compilation error` | ビルド失敗 |
| 設定エラー | `Configuration error`, `Invalid config` | 設定ファイルの問題 |

### Step 3: 原因の特定

エラーログから以下の情報を抽出：

1. **エラーメッセージ**: 具体的なエラー内容
2. **発生箇所**: ファイル名と行番号
3. **スタックトレース**: エラーの発生経路
4. **コンテキスト**: エラー前後の処理

### Step 4: レポート作成

```markdown
## CI解析レポート

### 概要
- **実行ID**: {run-id}
- **失敗ジョブ**: {job-name}
- **エラーカテゴリ**: {category}

### エラー詳細

| 項目 | 内容 |
|------|------|
| エラーメッセージ | {message} |
| 発生ファイル | {file}:{line} |
| エラー種別 | {type} |

### ログ抜粋

```
{relevant_log_excerpt}
```

### 推奨対処法

1. {recommendation_1}
2. {recommendation_2}

### 関連ファイル

- {file_1}
- {file_2}
```

## エラーパターン別の対処法

### テスト失敗

**識別パターン**:
- `FAILED tests/`
- `AssertionError`
- `pytest` + `FAILED`

**推奨対処**:
1. 失敗したテストを特定
2. テストコードまたは実装コードを修正
3. ローカルで `uv run pytest` を実行して確認

### 構文エラー (SyntaxError)

**識別パターン**:
- `SyntaxError:`
- `IndentationError:`
- `invalid syntax`

**推奨対処**:
1. エラーが発生したファイルと行番号を確認
2. インデント、括弧、コロンなどを確認
3. ローカルで `python -m py_compile {file}` で確認

### 依存関係エラー (ModuleNotFoundError)

**識別パターン**:
- `ModuleNotFoundError:`
- `ImportError:`
- `No module named`

**推奨対処**:
1. 不足しているモジュールを特定
2. `pyproject.toml` に依存関係を追加
3. `uv sync` を実行

### 型エラー (TypeError)

**識別パターン**:
- `TypeError:`
- `Type error`
- `expected X but got Y`

**推奨対処**:
1. 型の不一致箇所を特定
2. 引数や戻り値の型を修正
3. 型注釈を追加して `mypy` で確認

## Usage Example

```
User: CIが失敗したので解析して

Agent:
1. [Step 1] ログを取得します...
   gh run view 12345 --log-failed

2. [Step 2] エラーパターンを識別します...
   → テスト失敗を検出

3. [Step 3] 原因を特定します...
   → tests/test_example.py:25 で AssertionError

4. [Step 4] レポートを作成します...
   → 解析レポートを出力
```

## Integration

このスキルは `/check-ci` コマンドと連携して使用されます。

1. `/check-ci` でCI失敗を検出
2. `ci-analyzer` スキルでログを解析
3. `ci-fixer` エージェントで修正を提案（オプション）
