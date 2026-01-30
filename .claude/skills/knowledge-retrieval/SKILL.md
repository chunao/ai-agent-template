---
name: knowledge-retrieval
description: ユーザーが「方法」についてのガイダンスやベストプラクティスを求めている場合、または過去の知識やアーカイブされた例（`knowledge/index.json`から）が有益である可能性のある複雑なタスクに直面している場合に、このスキルを使用してください。このスキルにより、過去にアーカイブされた記事を発見し活用することができます。
---

# Knowledge Retrieval (ナレッジ検索)

## 概要

このスキルは、ローカルにアーカイブされた技術記事を「参考情報」として活用するためのものです。Gemini APIにナレッジ検索を委譲することで、メインエージェントのコンテキストウィンドウを節約します。

### 前提条件

- `gemini` CLIツールがインストールされていること
  - インストール: `npm install -g @google/generative-ai-cli` または Homebrew等
  - 認証: `gemini auth login` で認証を完了しておくこと
- Gemini CLIの認証を使用するため、`GEMINI_API_KEY` 環境変数は不要

### 基本方針

- **メインエージェントの知識を第一に**: タスクの実行は、あなた自身の知識とベストプラクティスを基盤として進めてください
- **ローカルナレッジは参考情報**: アーカイブされた記事は「こういう手段も世の中にはあるんだな」という参考程度の位置づけです
- **選択的な適用**: 「なるほど、これは使えそうな情報だ」と判断したものについてのみ、その知見をあなたの判断に組み込んでください
- **絶対視しない**: ローカルナレッジに記載されている方法が唯一の解決策ではありません。あなた自身の判断を優先してください

## ワークフロー

### ステップ 1: Gemini CLIによるナレッジ検索（コンテキスト節約）

**重要**: メインエージェントは `index.json` を読み込みません。代わりに、Gemini CLIにナレッジ検索タスクを委譲します。これにより、メインエージェントのコンテキストウィンドウを節約できます。

**stdin + -p方式の採用**: 大きなファイル（125KB以上）を送信するため、stdin経由でindex.jsonを流し込み、`-p`オプションで短い指示を追加します。

以下のコマンドを実行して、Gemini CLIに検索を依頼します：

```bash
# タイマー開始（ログ記録用）
START_TIME=$(date +%s)

# ユーザーリクエストを変数に代入（シェルインジェクション対策）
USER_REQUEST="[ここにユーザーの質問やタスク内容を記述]"

# .claude/logsディレクトリが存在しない場合は作成
mkdir -p .claude/logs

# stdin + -p方式でGemini CLIを実行
cat knowledge/index.json | timeout 120 gemini -p "以下のナレッジインデックスを分析し、「${USER_REQUEST}」に関連する記事を最大5件選択してください。

【分析観点】
- tags: 現在のトピックとの一致度
- use_cases: 現在の状況との適合性
- decision_triggers: 類似したトリガーの存在
- anti_cases: 避けるべき条件の確認

【出力フォーマット】
以下の形式で、選択した記事のIDのみを出力してください：

SELECTED_ARTICLE_IDS:
- 20260120_a1cce2
- 20260121_63d325" 2>&1
EXIT_CODE=$?

# タイマー終了とログ記録
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "{\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"task\":\"knowledge-retrieval\",\"model\":\"gemini-2.5-pro\",\"duration_sec\":${DURATION},\"exit_code\":${EXIT_CODE}}" >> .claude/logs/gemini_usage.jsonl
```

**セキュリティ対策**:
- ユーザー入力を変数 `USER_REQUEST` に代入し、直接シェルコマンドに埋め込まない
- 二重引用符で囲まれたプロンプト内で `${USER_REQUEST}` を展開（シェルの変数展開機能を利用）
- `timeout 120` でタイムアウトを設定（120秒）

**ログ記録**:
- 実行前に `START_TIME` を記録
- 実行後に `END_TIME` を記録し、`DURATION` を計算
- `.claude/logs/gemini_usage.jsonl` にJSONL形式でログを追記

**注意事項**:
- `[ここにユーザーの質問やタスク内容を記述]` の部分を、実際のユーザーリクエストに置き換えてください
- `gemini` コマンドが見つからない場合: `gemini` CLIのインストールと認証を確認してください

**エラー時のフォールバック**:
- `gemini` コマンドが見つからない場合: Gemini CLIのインストールと認証を確認してください
- API呼び出しが失敗した場合: ネットワーク接続を確認してリトライしてください
- 120秒以上応答がない場合（タイムアウト）: ユーザーに状況を報告し、スキップしてください

### ステップ 2: IDリストの抽出

Gemini CLIの出力から、`SELECTED_ARTICLE_IDS:` セクション以降の行を抽出し、各行から記事ID（`YYYYMMDD_XXXXXX` 形式）を取得します。

**期待される出力**:
```
SELECTED_ARTICLE_IDS:
- 20260120_a1cce2
- 20260121_63d325
- 20260121_555780
```

正規表現 `\d{8}_[a-f0-9]{6}` でIDを抽出できます。

### ステップ 3: コンテンツの取得

抽出したIDの記事のみを読み込みます。これにより、必要最小限のコンテキスト消費で済みます。

```python
view_file(AbsolutePath="d:/projects/P010/knowledge/archive/20260120_a1cce2.md")
view_file(AbsolutePath="d:/projects/P010/knowledge/archive/20260121_63d325.md")
view_file(AbsolutePath="d:/projects/P010/knowledge/archive/20260121_555780.md")
```

### ステップ 4: ナレッジの参考活用（選択的適用）

取得した記事を読み、以下の観点で評価してください：

**評価のポイント**:
- この情報は現在のタスクに本当に有用か？
- あなた自身の知識と矛盾していないか？比較してどちらが適切か？
- 記事の情報は最新か？（`published_at` を確認）
- この手法は現在の状況に適用可能か？

**有用と判断した場合の活用方法**:
- 解決策や計画の「一つの選択肢」として考慮する
- ベストプラクティスを参考にしつつ、状況に応じてカスタマイズする
- 既知の落とし穴（失敗モード）があれば、回避策を検討する
- 運用コストや前提条件を理解した上で、採用するか判断する

**注意**: アーカイブされた記事は「こういうアプローチもある」という参考情報です。あなた自身の知識とベストプラクティスを第一に考え、有用と判断したもののみを組み込んでください。

## 重要な注意点

-   **あなたの知識を第一に**: このスキルは補助的なツールです。あなた自身の知識、ベストプラクティス、判断力を最優先してください。
-   **コンテキスト分離の利点**: このワークフローでは、メインエージェントは `index.json`（約88KB）を一切読み込みません。Gemini APIが別コンテキストで処理するため、メインエージェントのコンテキストウィンドウを100%節約できます。
-   **AI検索の信頼性**: Gemini 2.5 Proは1Mトークンのコンテキストウィンドウを持ち、index.json全体を総合的に分析できます。タグの表記ゆれ（例: "MCP" と "Model Context Protocol"）も適切に認識します。
-   **選択的な参照**: Gemini APIが選択した記事IDのみを読み込みます。通常3〜5件の記事に絞り込まれるため、必要最小限のコンテキスト消費で済みます。これらの記事はあくまで「こういう手段もあるんだな」という参考情報です。
-   **鮮度の確認**: `published_at` の日付を確認してください。古い記事には時代遅れの情報が含まれている可能性があります。あなた自身の判断を使用してください。
-   **一つの参考例**: アーカイブされたナレッジは、物事を行うための*一つの*方法（例）を表しており、必ずしも*唯一の*または*絶対的に最良の*方法ではありません。あなた自身の知識と比較し、有用と判断したもののみを採用してください。

## 使用例

### 例1: Claude Codeの並列実行について知りたい場合

**ユーザーリクエスト**: "Claude Codeで複数のタスクを並列実行する方法を教えて"

**実行コマンド**:
```bash
START_TIME=$(date +%s)
USER_REQUEST="Claude Codeで複数のタスクを並列実行する方法を教えて"

mkdir -p .claude/logs

cat knowledge/index.json | timeout 120 gemini -p "以下のナレッジインデックスを分析し、「${USER_REQUEST}」に関連する記事を最大5件選択してください。

【分析観点】
- tags: 現在のトピックとの一致度
- use_cases: 現在の状況との適合性
- decision_triggers: 類似したトリガーの存在
- anti_cases: 避けるべき条件の確認

【出力フォーマット】
以下の形式で、選択した記事のIDのみを出力してください：

SELECTED_ARTICLE_IDS:
- 20260120_a1cce2
- 20260121_63d325" 2>&1
EXIT_CODE=$?

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo "{\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"task\":\"knowledge-retrieval\",\"model\":\"gemini-2.5-pro\",\"duration_sec\":${DURATION},\"exit_code\":${EXIT_CODE}}" >> .claude/logs/gemini_usage.jsonl
```

**出力例**:
```
SELECTED_ARTICLE_IDS:
- 20260120_a1cce2
- 20260121_f9e324
- 20260121_1153aa
```

**記事の読み込み**:
```python
view_file(AbsolutePath="d:/projects/P010/knowledge/archive/20260120_a1cce2.md")
view_file(AbsolutePath="d:/projects/P010/knowledge/archive/20260121_f9e324.md")
view_file(AbsolutePath="d:/projects/P010/knowledge/archive/20260121_1153aa.md")
```

### 例2: MCPについて知りたい場合

**ユーザーリクエスト**: "MCPサーバーの実装方法を知りたい"

**実行コマンド**:
```bash
START_TIME=$(date +%s)
USER_REQUEST="MCPサーバーの実装方法を知りたい"

mkdir -p .claude/logs

cat knowledge/index.json | timeout 120 gemini -p "以下のナレッジインデックスを分析し、「${USER_REQUEST}」に関連する記事を最大5件選択してください。

【分析観点】
- tags: 現在のトピックとの一致度
- use_cases: 現在の状況との適合性
- decision_triggers: 類似したトリガーの存在
- anti_cases: 避けるべき条件の確認

【出力フォーマット】
以下の形式で、選択した記事のIDのみを出力してください：

SELECTED_ARTICLE_IDS:
- 20260121_3808a9
- 20260121_61630a" 2>&1
EXIT_CODE=$?

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo "{\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"task\":\"knowledge-retrieval\",\"model\":\"gemini-2.5-pro\",\"duration_sec\":${DURATION},\"exit_code\":${EXIT_CODE}}" >> .claude/logs/gemini_usage.jsonl
```

**出力例**:
```
SELECTED_ARTICLE_IDS:
- 20260121_3808a9
- 20260121_61630a
- 20260120_c13016
```

---

## 手動検証手順

このスキルは `.md` ファイルのため、自動テストはありません。以下の手動検証手順で動作を確認してください：

### 検証手順

#### 1. 基本動作確認

短いテストリクエストで動作を確認します：

```bash
# プロジェクトルートに移動
cd D:\projects\P010

# .claude/logsディレクトリを作成（存在しない場合）
mkdir -p .claude/logs

# テスト実行
START_TIME=$(date +%s)
USER_REQUEST="Claude Code並列実行"

cat knowledge/index.json | timeout 120 gemini -p "以下のナレッジインデックスを分析し、「${USER_REQUEST}」に関連する記事を最大5件選択してください。

【分析観点】
- tags: 現在のトピックとの一致度
- use_cases: 現在の状況との適合性
- decision_triggers: 類似したトリガーの存在
- anti_cases: 避けるべき条件の確認

【出力フォーマット】
以下の形式で、選択した記事のIDのみを出力してください：

SELECTED_ARTICLE_IDS:
- 20260120_a1cce2
- 20260121_63d325" 2>&1
EXIT_CODE=$?

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "{\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"task\":\"knowledge-retrieval\",\"model\":\"gemini-2.5-pro\",\"duration_sec\":${DURATION},\"exit_code\":${EXIT_CODE}}" >> .claude/logs/gemini_usage.jsonl
```

#### 2. ログ記録確認

ログファイルに1行追加されたことを確認します：

```bash
# ログファイルの最後の1行を表示
tail -n 1 .claude/logs/gemini_usage.jsonl

# 期待される出力形式:
# {"timestamp":"2026-01-30T...Z","task":"knowledge-retrieval","model":"gemini-2.5-pro","duration_sec":5,"exit_code":0}
```

#### 3. エラーハンドリング確認（オプション）

タイムアウトや認証エラー時の動作を確認します：

```bash
# タイムアウトテスト（意図的に短い時間を設定）
timeout 1 gemini -p "test" 2>&1
EXIT_CODE=$?
echo "Exit code: $EXIT_CODE"

# 期待される結果: exit_code が 124 (timeout) または 1 (エラー)
```

### 確認項目

- [ ] Gemini CLIが正常に実行される
- [ ] `.claude/logs/gemini_usage.jsonl` に1行追加される
- [ ] ログにタイムスタンプ、タスク名、モデル名、実行時間、終了コードが含まれる
- [ ] `exit_code` が 0（成功）または適切なエラーコード
- [ ] タイムアウト（120秒）が設定されている

### トラブルシューティング

| 問題 | 原因 | 対処法 |
|------|------|--------|
| `gemini: command not found` | Gemini CLIが未インストール | `npm install -g @google/generative-ai-cli` でインストール |
| 認証エラー | 認証が未完了 | `gemini auth login` で認証 |
| タイムアウト | ネットワーク遅延 | タイムアウト値を延長（`timeout 180`） |
| ログが記録されない | ディレクトリが存在しない | `mkdir -p .claude/logs` を実行 |


