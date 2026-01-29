# /pr-merge - PRマージとブランチ削除

CIが通っているPRをマージし、ブランチを自動削除します。

## 使い方

```
/pr-merge [PR番号]
```

PR番号を省略した場合、現在のブランチに関連するPRを使用します。

## 前提条件

- **Worktree削除を実行する場合、mainリポジトリでClaude Codeセッションを実行していること**
- Worktreeディレクトリ内でセッションを実行中の場合、Worktree削除ができません
- セッションを終了し、mainリポジトリで再起動してから実行してください

## 実行手順

### 1. PRの特定

```bash
# PR番号が指定された場合
gh pr view $ARGUMENTS --json number,state,headRefName,mergeable,mergeStateStatus

# PR番号が省略された場合
gh pr view --json number,state,headRefName,mergeable,mergeStateStatus
```

### 2. CI結果の簡易確認

```bash
# 最新のワークフロー実行を確認
gh run list --branch <branch> --limit 1 --json status,conclusion
```

#### 判定基準

| conclusion | 状態 | 次のアクション |
|-----------|------|---------------|
| `success` | CI成功 | マージに進む |
| `failure` | CI失敗 | マージをスキップ |
| `null` | 実行中 | 完了を待つか確認 |

### 3. マージの実行

```bash
# マージとリモートブランチ削除を同時に実行
gh pr merge <pr-number> --merge --delete-branch
```

### 4. ローカルブランチの自動削除

マージ完了後、ローカルブランチを自動削除します。

#### 4.1. ブランチ名の取得

ステップ1で取得した `headRefName` を使用します。

#### 4.2. worktreeの存在確認

```bash
# 対象ブランチがworktreeで使用されているか確認
git worktree list | grep <branch-name>
```

#### 4.3. worktreeの削除（存在する場合）

worktreeが存在する場合は、ブランチ削除前にworktreeを削除します。

**重要**: Worktree削除前に、現在のセッションがWorktree内で実行されていないことを確認してください。

##### 4.3.1. セッション位置の確認

**Bash版**:
```bash
# 絶対パス正規化して比較
current_dir=$(realpath "$(pwd)")
worktree_path=$(realpath "<worktree-path>" 2>/dev/null)

if [[ -n "$worktree_path" && "$current_dir" == "$worktree_path"* ]]; then
  echo "⚠️ Worktree削除にはセッション終了が必要"
  echo ""
  echo "現在、このClaude CodeセッションはWorktreeディレクトリ内で実行されています。"
  echo "Worktreeを削除するには、以下の手順を実行してください："
  echo ""
  echo "### 手順"
  echo ""
  echo "1. **このセッションを終了してください**（Ctrl+D または exit）"
  echo ""
  echo "2. **mainリポジトリで新しいセッションを開始してください**:"
  echo ""
  echo "   **Bash**:"
  echo "   \`\`\`bash"
  echo "   cd /d/projects/P010 && claude code"
  echo "   \`\`\`"
  echo ""
  echo "3. **新しいセッションで削除コマンドを実行してください**:"
  echo "   \`\`\`"
  echo "   /pr-merge"
  echo "   \`\`\`"
  echo ""
  echo "### なぜセッション終了が必要か"
  echo ""
  echo "Claude Codeセッションがディレクトリ内で実行中の場合、そのディレクトリは「使用中」とみなされ、OSが削除を許可しません。セッションを終了することで、ディレクトリが解放され、削除が可能になります。"
  exit 1
fi
```

**PowerShell版**:
```powershell
# 絶対パス正規化して比較
$currentDir = (Resolve-Path -Path (Get-Location)).Path
$worktreePath = (Resolve-Path -Path "<worktree-path>" -ErrorAction SilentlyContinue).Path

if ($worktreePath -and ($currentDir -like "$worktreePath*")) {
  Write-Host "⚠️ Worktree削除にはセッション終了が必要"
  Write-Host ""
  Write-Host "現在、このClaude CodeセッションはWorktreeディレクトリ内で実行されています。"
  Write-Host "Worktreeを削除するには、以下の手順を実行してください："
  Write-Host ""
  Write-Host "### 手順"
  Write-Host ""
  Write-Host "1. **このセッションを終了してください**（Ctrl+D または exit）"
  Write-Host ""
  Write-Host "2. **mainリポジトリで新しいセッションを開始してください**:"
  Write-Host ""
  Write-Host "   **PowerShell**:"
  Write-Host "   ``````powershell"
  Write-Host "   cd D:\projects\P010; claude code"
  Write-Host "   ``````"
  Write-Host ""
  Write-Host "3. **新しいセッションで削除コマンドを実行してください**:"
  Write-Host "   ``````"
  Write-Host "   /pr-merge"
  Write-Host "   ``````"
  Write-Host ""
  Write-Host "### なぜセッション終了が必要か"
  Write-Host ""
  Write-Host "Claude Codeセッションがディレクトリ内で実行中の場合、そのディレクトリは「使用中」とみなされ、OSが削除を許可しません。セッションを終了することで、ディレクトリが解放され、削除が可能になります。"
  exit 1
}
```

##### 4.3.2. Worktreeの削除と物理確認

**Bash版**:
```bash
# git worktree remove 実行
git worktree remove "<worktree-path>" || git worktree remove --force "<worktree-path>"

# 物理ディレクトリの確認と削除
if [ -d "<worktree-path>" ]; then
  if [ -z "$(ls -A "<worktree-path>" 2>/dev/null)" ]; then
    # 空ディレクトリは自動削除
    rmdir "<worktree-path>" 2>/dev/null && echo "✅ 残存ディレクトリを削除しました" || echo "⚠️ 削除権限がありません"
  else
    # 中身がある場合は警告
    echo "⚠️ ディレクトリに未保存のファイルがあります: <worktree-path>"
    ls -la "<worktree-path>"
  fi
fi

# 最終確認
if [ ! -d "<worktree-path>" ]; then
  echo "✅ Worktree削除完了"
else
  echo "⚠️ 手動削除が必要です: <worktree-path>"
fi
```

**PowerShell版**:
```powershell
# git worktree remove 実行
git worktree remove "<worktree-path>"
if ($LASTEXITCODE -ne 0) {
  git worktree remove --force "<worktree-path>"
}

# 物理ディレクトリの確認と削除
if (Test-Path "<worktree-path>") {
  $items = Get-ChildItem -Path "<worktree-path>" -Force
  if ($items.Count -eq 0) {
    # 空ディレクトリは自動削除
    Remove-Item "<worktree-path>" -Force -ErrorAction SilentlyContinue
    if (-not (Test-Path "<worktree-path>")) {
      Write-Host "✅ 残存ディレクトリを削除しました"
    } else {
      Write-Host "⚠️ 削除権限がありません"
    }
  } else {
    # 中身がある場合は警告
    Write-Host "⚠️ ディレクトリに未保存のファイルがあります: <worktree-path>"
    Get-ChildItem -Path "<worktree-path>" -Force
  }
}

# 最終確認
if (-not (Test-Path "<worktree-path>")) {
  Write-Host "✅ Worktree削除完了"
} else {
  Write-Host "⚠️ 手動削除が必要です: <worktree-path>"
}
```

#### 4.4. mainブランチへの切り替え

現在のブランチが削除対象の場合、またはローカルmainを最新化するために実行します。

```bash
# mainに切り替え（現在ブランチが対象の場合）
git checkout main

# mainを最新化（git branch -d の成功に必要）
git pull origin main
```

#### 4.5. ローカルブランチの削除

```bash
# 安全な削除（マージ済みブランチのみ削除可能）
git branch -d <branch-name>
```

#### 4.6. 削除結果の報告

削除が成功した場合、結果をユーザーに報告します。

## エラーハンドリング

| 状況 | 対応 |
|------|------|
| PRが見つからない | `Error: PRが見つかりません。PR番号を確認してください。` |
| CIが失敗 | `Warning: CIが失敗しています。/check-ci で詳細を確認してください。マージをスキップします。` |
| CIが実行中 | `Info: CIが実行中です。完了後に再度実行するか、/check-ci で監視してください。` |
| マージ済み | `Info: このPRは既にマージ済みです。` |
| コンフリクト | `Error: マージコンフリクトがあります。コンフリクトを解決してから再度実行してください。` |
| ローカルブランチ削除に失敗 | `Warning: ローカルブランチの削除に失敗しました。手動で削除してください: git branch -d <branch-name>` |
| worktree削除に失敗 | `Warning: worktreeの削除に失敗しました。手動で削除してください: git worktree remove <path>` |

## 出力例

### 成功時

```
## PRマージ完了

| 項目 | 値 |
|------|-----|
| PR番号 | #123 |
| タイトル | Add new feature |
| ブランチ | feature/issue-123-xxx |
| マージ先 | main |

リモートブランチは自動削除されました。
ローカルブランチを自動削除しました: feature/issue-123-xxx
```

### 成功時（worktree使用中）

```
## PRマージ完了

| 項目 | 値 |
|------|-----|
| PR番号 | #123 |
| タイトル | Add new feature |
| ブランチ | feature/issue-123-xxx |
| マージ先 | main |

リモートブランチは自動削除されました。
worktreeを削除しました: D:\projects\P010-worktrees\issue-123-xxx
ローカルブランチを自動削除しました: feature/issue-123-xxx
```

### CI失敗時

```
## マージスキップ

| 項目 | 値 |
|------|-----|
| PR番号 | #123 |
| 理由 | CIが失敗しています |

次のステップ:
1. /check-ci 123 で詳細を確認
2. 問題を修正してプッシュ
3. CI成功後に /pr-merge 123 を再実行
```

## トラブルシューティング

### Worktreeが削除できない

**症状**: `Device or resource busy` または `Directory not empty` エラー

**原因**: 現在のClaude CodeセッションがWorktreeディレクトリ内で実行中

**解決方法**:
1. Ctrl+D でセッションを終了
2. mainリポジトリに移動: `cd D:\projects\P010` (PowerShell) または `cd /d/projects/P010` (Bash)
3. 新しいセッションを開始: `claude code`
4. 削除コマンドを再実行: `/pr-merge`

### ディレクトリが残っている

**症状**: `git worktree list` には表示されないが、ディレクトリが残っている

**原因**: `git worktree remove` は成功したが、物理ディレクトリが残っている

**解決方法**:
1. 空ディレクトリの場合: 自動的に削除されます（ステップ 4.3.2 で処理）
2. ファイルが残っている場合: 内容を確認後、手動削除するか `--force` オプションを使用

## 関連コマンド

- `/check-ci` - CI結果を確認
- `/pr-create` - PR作成とCI確認
- `/start-issue` - Issue作業開始
- `/review` - コードレビュー
- `/worktree-clean` - worktreeの手動管理
