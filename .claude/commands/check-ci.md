# /check-ci - CI結果確認

PR作成後のGitHub Actions実行結果を確認します。

## 使い方

```
/check-ci <PR番号>
```

または現在のブランチのCIを確認：

```
/check-ci
```

## 実行手順

### 1. PR/ブランチの特定

PR番号が指定された場合：
```bash
# PRの情報を取得
gh pr view $ARGUMENTS --json headRefName,number,state
```

PR番号が指定されていない場合：
```bash
# 現在のブランチ名を取得
git branch --show-current
```

### 2. ワークフロー実行の取得

```bash
# 最新のワークフロー実行を取得
gh run list --branch <branch> --limit 5 --json databaseId,status,conclusion,createdAt,name
```

#### ステータスの解釈

| status | conclusion | 状態 |
|--------|-----------|------|
| `in_progress` | - | 実行中 |
| `completed` | `success` | 成功 |
| `completed` | `failure` | 失敗 |
| `completed` | `cancelled` | キャンセル |
| `queued` | - | 待機中 |

### 3. 結果の確認

#### 成功の場合

```
CI結果: 成功
ワークフロー: {name}
実行時間: {duration}
```

#### 失敗の場合

```bash
# 詳細を確認
gh run view <run-id> --json jobs

# 失敗したジョブのログを取得
gh run view <run-id> --log --job <job-id>
```

#### 実行中の場合

待機オプションを使用：

```bash
# 完了まで待機（gh run watch）
gh run watch <run-id>
```

### 4. 待機オプション

CI実行中の場合、以下の戦略で待機します：

#### ポーリング戦略

| 回数 | 間隔 |
|------|------|
| 1-5回 | 10秒 |
| 6-10回 | 30秒 |
| 11回以降 | 60秒 |

#### タイムアウト設定

- デフォルト: 5分
- 最大: 15分

タイムアウトに達した場合は、現在のステータスを報告して終了します。

```
タイムアウト: CIはまだ実行中です
現在のステータス: in_progress
確認方法: gh run view <run-id>
```

### 5. 失敗時の対応

CI失敗時は以下の情報を提供：

1. **失敗したジョブ名**
2. **エラーログの抜粋**
3. **推定原因**（パターンマッチング）

```bash
# 失敗ログの取得
gh run view <run-id> --log-failed
```

#### よくある失敗パターン

| パターン | 原因 | 対処 |
|---------|------|------|
| `pytest` エラー | テスト失敗 | テストを修正 |
| `ModuleNotFoundError` | 依存関係エラー | `uv sync` を実行 |
| `SyntaxError` | 構文エラー | コードを修正 |
| `Type error` | 型エラー | 型定義を修正 |

## 出力例

### 成功時

```
## CI結果: 成功

| 項目 | 値 |
|------|-----|
| ワークフロー | Test |
| ステータス | success |
| 実行時間 | 1m 23s |
| ブランチ | feature/issue-13-xxx |

次のステップ: PRをマージできます
```

### 失敗時

```
## CI結果: 失敗

| 項目 | 値 |
|------|-----|
| ワークフロー | Test |
| ステータス | failure |
| 失敗ジョブ | test |

### エラーログ

{ログ抜粋}

### 推定原因

テストが失敗しています。以下を確認してください：
- tests/test_xxx.py の修正
```

### 実行中（タイムアウト時）

```
## CI結果: 実行中

タイムアウト（5分）に達しました。

| 項目 | 値 |
|------|-----|
| ワークフロー | Test |
| ステータス | in_progress |
| 実行ID | 12345678 |

手動確認: gh run view 12345678
```

## 関連コマンド

- `/start-issue` - Issue作業開始
- `/tdd` - TDDサイクル実行
- `/review` - コードレビュー
- `/pr-create` - PR作成とCI確認
- `/pr-merge` - PRをマージ
