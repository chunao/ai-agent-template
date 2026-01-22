# MCP (Model Context Protocol) 設定

Claude Codeが外部ツール・データソースにアクセスするための設定です。

## セットアップ

### 1. 設定ファイルのコピー

```bash
cp config.example.json config.json
```

### 2. 環境変数の設定

`.env` ファイルまたはシステム環境変数で以下を設定：

```bash
# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx

# プロジェクトルート（Filesystem MCP用）
PROJECT_ROOT=D:\projects\your-project

# オプション：データベース
DATABASE_URL=postgresql://user:pass@localhost/dbname
SQLITE_PATH=./data/app.db

# オプション：検索
BRAVE_API_KEY=BSA_xxxxxxxxxxxxx

# オプション：Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxxxxxxxxxxxx
```

### 3. MCPの有効化/無効化

`config.json` を編集して、使用するMCPを `mcpServers` セクションに、
使用しないMCPを `disabledMcpServers` セクションに配置します。

## 推奨構成

### 基本構成（常時有効）

| MCP | 用途 |
|-----|------|
| github | Issue/PR管理、リポジトリ操作 |
| filesystem | ファイル・ディレクトリ操作 |

### プロジェクト別（必要時のみ有効）

| MCP | 用途 |
|-----|------|
| codex | セカンドオピニオン、設計レビュー |
| postgres/sqlite | データベース連携 |
| brave-search | Web検索、技術調査 |
| supabase | Supabaseバックエンド連携 |

## 注意事項

### コンテキストウィンドウ管理

> **重要**: MCPは常に **10個以下** に抑えてください。
>
> MCPを有効化しすぎると、コンテキストウィンドウが縮小します（200K → 70K）。

### セキュリティ

- APIキーは環境変数で管理（ハードコード禁止）
- `config.json` は `.gitignore` に追加済み
- トークンは最小限の権限で発行

## MCPの追加

新しいMCPを追加する場合：

1. `disabledMcpServers` にエントリを追加
2. 必要な環境変数を設定
3. テスト後、`mcpServers` に移動して有効化

## トラブルシューティング

### MCPが認識されない

```bash
# npxキャッシュをクリア
npx clear-npx-cache

# MCPサーバーを直接テスト
npx -y @modelcontextprotocol/server-github
```

### 環境変数が読み込まれない

- シェルを再起動
- `.env` ファイルの構文を確認
- `${VAR_NAME}` 形式が正しいか確認

## 参考リンク

- [MCP公式ドキュメント](https://modelcontextprotocol.io/)
- [MCP Server一覧](https://github.com/modelcontextprotocol/servers)
