# /worktree-clean - Worktree削除

指定したIssueのworktreeを安全に削除します。

## 使い方

```
/worktree-clean 123
/worktree-clean 123 --delete-branch
```

- 引数なし: worktreeのみ削除（ブランチは保持）
- `--delete-branch`: ローカルブランチも削除

## 前提条件

- **Worktree削除を実行する場合、mainリポジトリでClaude Codeセッションを実行していること**
- Worktreeディレクトリ内でセッションを実行中の場合、Worktree削除ができません
- セッションを終了し、mainリポジトリで再起動してから実行してください

## 実行手順

### 1. 対象Worktreeの特定

```bash
# worktree一覧から対象を特定
git worktree list | grep "issue-$ARGUMENTS"
```

#### チェックポイント

| 状態 | 対応 |
|------|------|
| Worktreeが存在しない | エラー（存在しないことを案内） |
| Worktreeが存在する | 削除プロセスを続行 |

### 2. 安全性チェック

削除前に以下を確認します：

#### 2.1 未コミットの変更チェック

```bash
# 未コミットの変更を確認
git -C ../P010-worktrees/issue-$ARGUMENTS-{スラッグ} status --porcelain
```

未コミットの変更がある場合：
```
⚠️ 警告: 未コミットの変更があります

変更ファイル:
- {file1}
- {file2}

削除を続行しますか？
1. はい（変更を破棄）
2. いいえ（中断）
```

#### 2.2 未プッシュのコミットチェック

```bash
# リモートとの差分を確認
git -C ../P010-worktrees/issue-$ARGUMENTS-{スラッグ} log origin/main..HEAD --oneline
```

未プッシュのコミットがある場合：
```
⚠️ 警告: 未プッシュのコミットがあります

未プッシュのコミット:
- abc1234 Add feature
- def5678 Fix bug

削除を続行しますか？
1. はい（プッシュせずに削除）
2. いいえ（中断してプッシュを促す）
```

#### 2.3 PRの状態チェック

```bash
# ブランチ名を取得
BRANCH=$(git -C ../P010-worktrees/issue-$ARGUMENTS-{スラッグ} branch --show-current)

# PRの状態を確認
gh pr list --head "$BRANCH" --state all --json number,state,mergedAt
```

| PR状態 | 対応 |
|--------|------|
| PRなし | 通常の削除確認 |
| Open | 警告を表示（PRがまだオープン） |
| Merged | 安全に削除可能 |
| Closed | 警告を表示（PRがクローズされた） |

### 3. Worktreeの削除

**重要**: Worktree削除前に、現在のセッションがWorktree内で実行されていないことを確認してください。

#### 3.1. セッション位置の確認

**Bash版**:
```bash
# 絶対パス正規化して比較
current_dir=$(realpath "$(pwd)")
worktree_path=$(realpath "../P010-worktrees/issue-$ARGUMENTS-{スラッグ}" 2>/dev/null)

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
  echo "   /worktree-clean $ARGUMENTS"
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
$worktreePath = (Resolve-Path -Path "../P010-worktrees/issue-$ARGUMENTS-{スラッグ}" -ErrorAction SilentlyContinue).Path

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
  Write-Host "   /worktree-clean $ARGUMENTS"
  Write-Host "   ``````"
  Write-Host ""
  Write-Host "### なぜセッション終了が必要か"
  Write-Host ""
  Write-Host "Claude Codeセッションがディレクトリ内で実行中の場合、そのディレクトリは「使用中」とみなされ、OSが削除を許可しません。セッションを終了することで、ディレクトリが解放され、削除が可能になります。"
  exit 1
}
```

#### 3.2. Worktreeの削除と物理確認

**Bash版**:
```bash
# git worktree remove 実行
git worktree remove "../P010-worktrees/issue-$ARGUMENTS-{スラッグ}"

# 未コミットの変更がある場合は強制削除
if [ $? -ne 0 ]; then
  git worktree remove --force "../P010-worktrees/issue-$ARGUMENTS-{スラッグ}"
fi

# 物理ディレクトリの確認と削除
WORKTREE_PATH="../P010-worktrees/issue-$ARGUMENTS-{スラッグ}"
if [ -d "$WORKTREE_PATH" ]; then
  if [ -z "$(ls -A "$WORKTREE_PATH" 2>/dev/null)" ]; then
    # 空ディレクトリは自動削除
    rmdir "$WORKTREE_PATH" 2>/dev/null && echo "✅ 残存ディレクトリを削除しました" || echo "⚠️ 削除権限がありません"
  else
    # 中身がある場合は警告
    echo "⚠️ ディレクトリに未保存のファイルがあります: $WORKTREE_PATH"
    ls -la "$WORKTREE_PATH"
  fi
fi

# 最終確認
if [ ! -d "$WORKTREE_PATH" ]; then
  echo "✅ Worktree削除完了"
else
  echo "⚠️ 手動削除が必要です: $WORKTREE_PATH"
fi
```

**PowerShell版**:
```powershell
# git worktree remove 実行
$WORKTREE_PATH = "../P010-worktrees/issue-$ARGUMENTS-{スラッグ}"
git worktree remove $WORKTREE_PATH

# 未コミットの変更がある場合は強制削除
if ($LASTEXITCODE -ne 0) {
  git worktree remove --force $WORKTREE_PATH
}

# 物理ディレクトリの確認と削除
if (Test-Path $WORKTREE_PATH) {
  $items = Get-ChildItem -Path $WORKTREE_PATH -Force
  if ($items.Count -eq 0) {
    # 空ディレクトリは自動削除
    Remove-Item $WORKTREE_PATH -Force -ErrorAction SilentlyContinue
    if (-not (Test-Path $WORKTREE_PATH)) {
      Write-Host "✅ 残存ディレクトリを削除しました"
    } else {
      Write-Host "⚠️ 削除権限がありません"
    }
  } else {
    # 中身がある場合は警告
    Write-Host "⚠️ ディレクトリに未保存のファイルがあります: $WORKTREE_PATH"
    Get-ChildItem -Path $WORKTREE_PATH -Force
  }
}

# 最終確認
if (-not (Test-Path $WORKTREE_PATH)) {
  Write-Host "✅ Worktree削除完了"
} else {
  Write-Host "⚠️ 手動削除が必要です: $WORKTREE_PATH"
}
```

### 4. ローカルブランチの削除（オプション）

`--delete-branch` オプションが指定されている場合：

```bash
# ローカルブランチを削除
git branch -d {prefix}/issue-$ARGUMENTS-{スラッグ}
```

マージされていないブランチの場合：
```bash
# 強制削除（確認後）
git branch -D {prefix}/issue-$ARGUMENTS-{スラッグ}
```

### 5. 削除完了の報告

```markdown
## Worktree削除完了

**Issue**: #$ARGUMENTS
**削除したパス**: D:\projects\P010-worktrees\issue-$ARGUMENTS-{スラッグ}
**ブランチ**: {prefix}/issue-$ARGUMENTS-{スラッグ}

### 削除内容
- [x] Worktreeディレクトリ
- [ ] ローカルブランチ（--delete-branch で削除可能）

### 現在のworktree一覧
`/worktree-list` で確認できます
```

`--delete-branch` 指定時：
```markdown
## Worktree削除完了

**Issue**: #$ARGUMENTS
**削除したパス**: D:\projects\P010-worktrees\issue-$ARGUMENTS-{スラッグ}
**ブランチ**: {prefix}/issue-$ARGUMENTS-{スラッグ}

### 削除内容
- [x] Worktreeディレクトリ
- [x] ローカルブランチ

### 現在のworktree一覧
`/worktree-list` で確認できます
```

## エラーハンドリング

| 状況 | 対応 |
|------|------|
| Worktreeが存在しない | エラーメッセージを表示 |
| 削除権限がない | 手動削除を案内 |
| ブランチがmainにマージされていない | 警告を表示し確認を求める |
| PRがまだオープン | 警告を表示し確認を求める |
| ディレクトリが使用中 | プロセスを終了するよう案内 |

## トラブルシューティング

### Worktreeが削除できない

**症状**: `Device or resource busy` または `Directory not empty` エラー

**原因**: 現在のClaude CodeセッションがWorktreeディレクトリ内で実行中

**解決方法**:
1. Ctrl+D でセッションを終了
2. mainリポジトリに移動: `cd D:\projects\P010` (PowerShell) または `cd /d/projects/P010` (Bash)
3. 新しいセッションを開始: `claude code`
4. 削除コマンドを再実行: `/worktree-clean {issue番号}`

### ディレクトリが残っている

**症状**: `git worktree list` には表示されないが、ディレクトリが残っている

**原因**: `git worktree remove` は成功したが、物理ディレクトリが残っている

**解決方法**:
1. 空ディレクトリの場合: 自動的に削除されます（ステップ 3.2 で処理）
2. ファイルが残っている場合: 内容を確認後、手動削除するか `--force` オプションを使用

## 関連コマンド

- `/worktree-list` - worktree一覧を表示
- `/worktree-start {issue番号}` - 新しいworktreeを作成
- `/pr-merge {PR番号}` - PRをマージ
