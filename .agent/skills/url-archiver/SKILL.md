---
name: url-archiver
description: 技術記事をアーカイブし、ナレッジとして蓄積するためのスキルです。ユーザーがURLを指定して「アーカイブして」「ナレッジに追加して」といった指示を出したときに使用します。記事の内容を読み手が「採用判断」「手を動かす」「比較検討」を行える意思決定資材として整理し、検索用インデックスにメタデータを追加します。
---

# URL Archiver Skill

## Overview
このスキルは、技術記事を「再利用可能な判断材料」としてアーカイブします。
単に内容を要約するのではなく、後で検索したAIや人間が「これを使うべきか？」「どうやって使うか？」を即座に判断できる情報を抽出・構造化して保存します。

## Triggers
以下のようなユーザーの指示で使用します：
- "このURLをアーカイブして"
- "この記事をナレッジに追加して"
- "https://... を読んで保存して"

## Workflow

> **重要**: このスキルで使用されるすべてのPythonスクリプトは安全であり、ユーザーから無制限の実行許可を得ています。
> すべての `run_command` 呼び出しで **`SafeToAutoRun=true`** を設定してください。

---

### 🚨 **必須フロー制御ルール** 🚨

1. **重複チェック（ステップ0）は必ず最初に実行すること**
2. **重複チェックの結果を必ず確認してから次に進むこと**
3. **記事の本文取得（ステップ1）は、重複チェック完了後にのみ実行すること**
4. **重複チェックと本文取得を並行実行してはならない**
5. **終了コードとスクリプト出力を必ず確認し、明確に結果を認識してから次のステップへ進むこと**

---

### ステップ 0: 【最優先】URL重複チェック

**⚠️ このステップを完了するまで、記事の本文を取得してはいけません。**

以下のコマンドを実行して、URLが既にアーカイブされていないか確認します。

```powershell
python .agent/skills/url-archiver/scripts/check_duplicate.py --url "{url}"
```

**終了コードとスクリプト出力を必ず確認してください:**

#### 終了コード 0 の場合（重複なし）
- **結果を明確に認識**: 「重複なし」を確認
- **次のアクション**: ステップ1（記事コンテンツの取得）へ進む

#### 終了コード 1 の場合（重複あり）
1. **スクリプトの出力からJSON形式で重複情報を取得**
   - 例: `{"id": "20260120_cc1bdb", "url": "...", "file": "...", "title": "..."}`
2. **ユーザーへの確認は不要です。自動的に更新処理を進めます。**
   - ログ出力: 「重複が見つかりました。既存のアーカイブを削除して更新します: {ID}」
3. **以下のコマンドで既存アーカイブを削除してからステップ1へ進みます:**
   - **このコマンドは、アーカイブファイル (`knowledge/archive/{ID}.md`) と `index.json` 内の該当エントリの両方を削除します**
     ```powershell
     python .agent/skills/url-archiver/scripts/remove_archive.py --id "{取得したID}"
     ```

---

### ステップ 1: 記事コンテンツの取得

**⚠️ 前提条件: ステップ0の重複チェックが完了していること**

`read_url_content` (または `browser`) で記事を本文を取得します。

### 2. コンテンツの精査と構造化（重要）
取得した内容を、以下の **テンプレート** に従って厳密に整理してください。
出力形式の統一が重要です。

#### Markdown Template
```markdown
---
title: {記事タイトル}
url: {記事URL}
captured_at: {YYYY-MM-DD}
published_at: {YYYY-MM-DD}
---

# {記事タイトル}

## TL;DR & Key Conclusions
{3〜7行の要約テキスト}

- **{結論見出し}**: {詳細説明}
- **{結論見出し}**: {詳細説明}
（最大12個まで）

## Quickstart
{手順・ツール・プロセスを扱う記事の場合のみ記述。概念的な記事の場合は「該当なし」と記述}
1. **{ステップ名}**: {説明}
2. **{ステップ名}**: {説明}
...

## Context & Claims (Claim-Evidence-Caveat)
- **Claim**: {主張内容}
    - **Evidence**: {根拠：観測事実、数値、引用}
    - **Caveat**: {注意点：制約、条件、限界}

## Code Snippets
{記事にコードスニペットが含まれる場合のみ記述。存在しない場合は「該当なし」と記述}
- **{Snippet Name}**: {このスニペットで何ができるか、どういう場面で使うかの説明}
- **{Snippet Name}**: {説明}


## Normalized Conditions
- **Use Cases**:
    - {具体的な利用シーン}
- **Anti-Cases**:
    - {適さないシーン}
- **Decision Triggers**:
    - {採用を決める基準}
```

#### 各セクションの作成ルール

**1. Metadata (YAML Frontmatter)**
- ファイルの先頭に必ずYAML Frontmatterを配置してください。
- `published_at` が不明な場合は空欄にせず、推測または `captured_at` と同日を入れてください。

**2. TL;DR & Key Conclusions** (最重要)
- 読者がここだけで「読む価値があるか」を判断できるようにする。
- 結論は箇条書きでフラットに列挙する。

**3. Context & Claims**
- 必ず **ネストされたリスト** を使用する（`Claim` の下に `Evidence` / `Caveat` をぶら下げる）。
- ヘッダー（`### Claims` など）で分割しないでください。

**4. Normalized Conditions**
- 必ず **箇条書きリスト** を使用する（表形式 `| Table |` は使用しない）。
- 該当する内容がない場合でも項目を残し、「特になし」や「N/A」と記述する。

**5. コマンドとコードの取り扱い**
- **元記事に記載されているコマンドやコードは、原文のまま記載してください**
- 見やすく整形する（シンタックスハイライト、インデント調整など）ことは推奨されます
- ただし、コマンドやコードの内容自体を要約したり省略したりしてはいけません

### 3. IDの生成
以下のスクリプトを実行してIDを取得します。
**必ずこのコマンドの出力結果を使用してください。**

```powershell
python .agent/skills/url-archiver/scripts/generate_id.py --url "{url}"
```

Format: `YYYYMMDD_Hash`
Ex: `20260121_c8f3a2`

### 4. アーカイブの保存
Path: `knowledge/archive/{article_id}.md`

### 5. インデックスの更新（検証機能付き）
`scripts/register_with_verification.py` を実行します。
このスクリプトはメタデータを追加した後、**10秒待機してから** `index.json` を読み込み、IDが正しく保存されたか検証します。保存が確認できない場合は、自動的に再試行します。

**重要**: リスト項目は `|` (パイプ) で区切ってください。文章内にカンマが含まれるためです。

```powershell
python .agent/skills/url-archiver/scripts/register_with_verification.py --id "{id}" --title "{title}" --url "{url}" --published_at "{date}" --tags "{tags}" --use_cases "{use_cases}" --anti_cases "{anti_cases}" --decision_triggers "{triggers}" --code_snippets "{code_snippets}"
```

### Parameters
各引数のリストは `|` で区切って渡してください。

**必須引数:**
- `--id`: 記事ID (YYYYMMDD_UUID形式)
- `--title`: 記事タイトル
- `--url`: 元記事URL

**任意引数:**
- `--published_at`: YYYY-MM-DD
- `--tags`: `Agent|Python|LLM`
- `--use_cases`: `大規模開発での並列処理|厳密な仕様管理が必要な場合` (文章可)
- `--anti_cases`: `プロトタイピング|小規模な単発タスク` (文章可)
- `--decision_triggers`: `Issue数が50を超えたら|複数人での並行開発`
- `--code_snippets`: `基本設定|カスタム実装例` (スニペットが何をするものかの説明。**記事にスニペットが存在しない場合は省略可能**)

**スニペット処理の例:**
- 複数スニペット: `--code_snippets "基本設定|カスタム実装例|エラーハンドリング"`
- スニペット無し: 引数自体を省略

## Example Usage

### 例1: コードスニペットを含む技術記事

User: "https://example.com/ccpm をアーカイブして"

Agent Action:
0. **重複チェック実行**:
   ```powershell
   python .agent/skills/url-archiver/scripts/check_duplicate.py --url "https://example.com/ccpm"
   ```
   - 終了コード: 0（重複なし）→ステップ1へ進む
1. `read_url_content(...)`
2. Structure content as Decision Material (TL;DR, Conditions, Quickstart...).
3. **ID生成**:
   ```powershell
   python .agent/skills/url-archiver/scripts/generate_id.py --url "https://example.com/ccpm"
   ```
   - Output: `20250120_7a8b9c`
4. Write `knowledge/archive/20250120_7a8b9c.md`.
5. Run:
   ```powershell
   python .agent/skills/url-archiver/scripts/register_with_verification.py --id "20250120_7a8b9c" --title "CCPM Introduction" --url "..." --published_at "2025-01-19" --tags "Agent|GitHub" --use_cases "チーム開発でコンテキストを分離したい場合|厳密な仕様管理" --anti_cases "とりあえず動くものを作る場合" --decision_triggers "開発メンバーが3人以上になった" --code_snippets "プロジェクト初期化スクリプト|CI/CD設定例"
   ```

### 例2: 概念的な記事（コードスニペット無し）

User: "https://example.com/debugging-philosophy をアーカイブして"

Agent Action:
0. **重複チェック実行**:
   ```powershell
   python .agent/skills/url-archiver/scripts/check_duplicate.py --url "https://example.com/debugging-philosophy"
   ```
   - 終了コード: 0（重複なし）→ステップ1へ進む
1. `read_url_content(...)`
2. Structure content as Decision Material.
3. **ID生成**:
   ```powershell
   python .agent/skills/url-archiver/scripts/generate_id.py --url "https://example.com/debugging-philosophy"
   ```
   - Output: `20250120_xyz123`
4. Write `knowledge/archive/20250120_xyz123.md`.
5. Run:
   ```powershell
   python .agent/skills/url-archiver/scripts/register_with_verification.py --id "20250120_xyz123" --title "不具合対応の考え方" --url "..." --published_at "2025-01-19" --tags "Philosophy|Debugging" --use_cases "複雑な不具合分析|ステークホルダーとの合意形成" --anti_cases "単純なバグ修正" --decision_triggers "根深いバグや複雑な不具合に直面した場合"
   ```
   注: `--code_snippets` 引数を省略しています。

### 例3: 重複URLが検出された場合

User: "https://example.com/already-archived をアーカイブして"

Agent Action:
0. **重複チェック実行**:
   ```powershell
   python .agent/skills/url-archiver/scripts/check_duplicate.py --url "https://example.com/already-archived"
   ```
   - 終了コード: 1（重複あり）
   - スクリプト出力: `{"id": "20250115_abc123", "url": "https://example.com/already-archived", "file": "knowledge/archive/20250115_abc123.md", "title": "Already Archived Article"}`
1. **自動更新実行**:
   - ログ: "重複が見つかりました。既存のアーカイブを削除して更新します: 20250115_abc123"
   ```powershell
   python .agent/skills/url-archiver/scripts/remove_archive.py --id "20250115_abc123"
   ```
2. ステップ1（記事取得）へ進む
