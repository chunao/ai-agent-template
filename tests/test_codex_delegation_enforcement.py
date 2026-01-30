"""
Test for Issue #92: レビュータスクのCodex委任を「推奨」から「原則」に変更し、存在確認手順を明示する

受け入れ基準:
1. すべての修正対象ファイルで「推奨」が「原則」に変更されている
2. すべての修正対象ファイルで「Step 1: Codex CLI存在確認」の手順が追加されている
3. 存在確認コマンド（`where codex 2>nul` for Windows）が記載されている
4. Codex CLI存在時は必ずCodex委任に進む構造になっている
5. Claude Codeフォールバックは「Codex CLI利用不可時のみ」と明記されている
6. 6つのファイルすべてが統一されたフォーマットになっている
"""

import re
from pathlib import Path

import pytest


# 修正対象ファイルのリスト
TARGET_FILES = [
    ".claude/commands/review.md",
    ".claude/commands/start-issue.md",
    ".claude/skills/progressive-review/SKILL.md",
    ".claude/skills/tdd-cycle/SKILL.md",
    ".claude/agents/plan-reviewer.md",
    ".claude/agents/reviewer.md",
]

# プロジェクトルートディレクトリを取得
def _find_project_root() -> Path:
    """プロジェクトルートを .git または pyproject.toml から検出"""
    current = Path(__file__).resolve()
    for parent in [current.parent] + list(current.parents):
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent
    # フォールバック: テストファイルの親の親
    return Path(__file__).parent.parent


PROJECT_ROOT = _find_project_root()


@pytest.fixture
def file_contents():
    """すべての対象ファイルの内容を読み込む"""
    contents = {}
    for file_path in TARGET_FILES:
        full_path = PROJECT_ROOT / file_path
        if not full_path.exists():
            pytest.fail(f"対象ファイルが存在しません: {file_path}")
        contents[file_path] = full_path.read_text(encoding="utf-8")
    return contents


@pytest.fixture
def step_sections(file_contents):
    """各ファイルのStepセクション情報をキャッシュ（パフォーマンス最適化）"""
    sections = {}
    for file_path, content in file_contents.items():
        # Step 1: Codex CLI存在確認 を基準に検索（次の見出しレベル2-6またはファイル末尾まで）
        # [\s\S]*? は任意の文字（改行含む）を非貪欲にマッチ
        # (?=\n^#{2,6}\s+\S|\Z) は「改行+次の見出し」または「ファイル末尾」を lookahead
        step1_match = re.search(
            r"^#{2,6}\s*Step\s+1:\s*Codex\s+CLI存在確認[\s\S]*?(?=\n^#{2,6}\s+\S|\Z)",
            content,
            re.IGNORECASE | re.MULTILINE,
        )

        # Step 1が見つかった場合、その直後のStep 2, 3を検索
        if step1_match:
            step1_end = step1_match.end()
            remaining_content = content[step1_end:]

            # Step 2を検索
            step2_match = re.search(
                r"^#{2,6}\s*Step\s+2:[\s\S]*?(?=\n^#{2,6}\s+\S|\Z)",
                remaining_content,
                re.IGNORECASE | re.MULTILINE,
            )

            # Step 3を検索
            step3_match = None
            if step2_match:
                step2_end = step2_match.end()
                remaining_after_step2 = remaining_content[step2_end:]
                step3_match = re.search(
                    r"^#{2,6}\s*Step\s+3:[\s\S]*?(?=\n^#{2,6}\s+\S|\Z)",
                    remaining_after_step2,
                    re.IGNORECASE | re.MULTILINE,
                )

            sections[file_path] = {
                "step1": step1_match.group() if step1_match else None,
                "step2": step2_match.group() if step2_match else None,
                "step3": step3_match.group() if step3_match else None,
            }
        else:
            sections[file_path] = {"step1": None, "step2": None, "step3": None}

    return sections


class TestCodexDelegationEnforcement:
    """Codex委任の強制化に関するテスト"""

    def test_all_target_files_exist(self):
        """正常系: すべての対象ファイルが存在すること"""
        for file_path in TARGET_FILES:
            full_path = PROJECT_ROOT / file_path
            assert full_path.exists(), f"ファイルが存在しません: {file_path}"

    def test_no_recommendation_wording_remains(self, file_contents):
        """異常系: 「推奨」という文字列が残っていないこと（修正漏れ検出）"""
        for file_path, content in file_contents.items():
            # Codex委任に関する「推奨」という文字列が残っていないか確認
            # （他の文脈での「推奨」は許容）
            pattern = r"(Codex委任|codex-delegate).*?推奨"
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            assert match is None, (
                f"{file_path} に「推奨」という文字列が残っています: {match.group() if match else ''}"
            )

    def test_principle_wording_added(self, file_contents):
        """正常系: 各ファイルに「原則」という文字列が含まれていること"""
        for file_path, content in file_contents.items():
            # 「原則として」または「原則：」のような表現を探す
            pattern = r"原則"
            assert re.search(pattern, content), (
                f"{file_path} に「原則」という文字列が含まれていません"
            )

    def test_codex_cli_check_step_added(self, file_contents):
        """正常系: 各ファイルに「Step 1: Codex CLI存在確認」の見出しが含まれていること"""
        for file_path, content in file_contents.items():
            # 見出しのパターンを探す（見出しレベル2-6に対応）
            pattern = r"^#{2,6}\s*Step\s+1:\s*Codex\s+CLI存在確認"
            assert re.search(pattern, content, re.IGNORECASE | re.MULTILINE), (
                f"{file_path} に「Step 1: Codex CLI存在確認」の見出しが含まれていません"
            )

    def test_codex_cli_check_command_exists(self, file_contents):
        """正常系: 各ファイルに `where codex 2>nul` コマンドが含まれていること"""
        for file_path, content in file_contents.items():
            # Windows用の存在確認コマンドを探す
            pattern = r"where\s+codex\s+2>nul"
            assert re.search(pattern, content), (
                f"{file_path} に `where codex 2>nul` コマンドが含まれていません"
            )

    def test_fallback_condition_clarified(self, file_contents):
        """正常系: 各ファイルに「Codex CLI利用不可時のみ」という文言が含まれていること（文脈付き検証）"""
        for file_path, content in file_contents.items():
            # フォールバック条件がStep 3またはフォールバックのコンテキストで出現することを確認
            # 単語一致のみではなく、文脈付きで検証（誤検知防止）
            pattern = r"(Step\s+3|フォールバック).*?Codex\s+CLI利用不可時のみ"
            assert re.search(pattern, content, re.IGNORECASE | re.DOTALL), (
                f"{file_path} に「Codex CLI利用不可時のみ」という文言が適切な文脈で含まれていません"
            )

    def test_unified_format_across_files(self, file_contents):
        """境界値: 6つのファイルすべてが統一されたフォーマットになっていること"""
        # すべてのファイルに共通して含まれるべきキーワード
        required_keywords = [
            "原則",
            "Step 1: Codex CLI存在確認",
            "where codex 2>nul",
            "Codex CLI利用不可時のみ",
        ]

        for file_path, content in file_contents.items():
            for keyword in required_keywords:
                assert keyword in content, (
                    f"{file_path} に必須キーワード「{keyword}」が含まれていません（統一性の問題）"
                )

    def test_codex_delegation_flow_structure(self, file_contents):
        """正常系: Codex CLI存在時は必ずCodex委任に進む構造になっていること"""
        for file_path, content in file_contents.items():
            # Step 1の後にStep 2（Codex委任）が続いていることを確認（見出しレベル2-6に対応）
            pattern = r"^#{2,6}\s*Step\s+1:.*?^#{2,6}\s*Step\s+2:.*?Codex委任"
            assert re.search(pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL), (
                f"{file_path} に「Step 1 → Step 2: Codex委任」の構造が含まれていません"
            )

    def test_empty_or_invalid_file_detection(self):
        """異常系: 空ファイルや不正なフォーマットの場合、テストが失敗すること"""
        for file_path in TARGET_FILES:
            full_path = PROJECT_ROOT / file_path
            content = full_path.read_text(encoding="utf-8")
            # ファイルが空でないことを確認
            assert len(content.strip()) > 0, f"{file_path} が空ファイルです"
            # Markdown形式であることを確認（最低限の見出しが含まれているか）
            assert re.search(r"^#+\s+", content, re.MULTILINE), (
                f"{file_path} が不正なフォーマットです（見出しが含まれていません）"
            )

    def test_step2_heading_contains_codex_delegation(self, file_contents):
        """正常系: Step 2の見出しに「Codex委任」が含まれていること（厳密化）"""
        for file_path, content in file_contents.items():
            # Step 2の見出しに「Codex委任」または「Codex委任（原則）」が含まれるか確認（見出しレベル2-6に対応）
            pattern = r"^#{2,6}\s*Step\s+2:.*?Codex委任"
            assert re.search(pattern, content, re.IGNORECASE | re.MULTILINE), (
                f"{file_path} の Step 2 見出しに「Codex委任」が含まれていません"
            )

    def test_step_order_is_correct(self, file_contents):
        """境界値: Step 1 → Step 2 → Step 3 の順序が正しいこと"""
        for file_path, content in file_contents.items():
            # Step 1, 2, 3 が順番に出現することを確認（見出しレベル2-6に対応）
            step1_match = re.search(r"^#{2,6}\s*Step\s+1:", content, re.IGNORECASE | re.MULTILINE)
            step2_match = re.search(r"^#{2,6}\s*Step\s+2:", content, re.IGNORECASE | re.MULTILINE)
            step3_match = re.search(r"^#{2,6}\s*Step\s+3:", content, re.IGNORECASE | re.MULTILINE)

            assert step1_match is not None, f"{file_path} に Step 1 が含まれていません"
            assert step2_match is not None, f"{file_path} に Step 2 が含まれていません"
            assert step3_match is not None, f"{file_path} に Step 3 が含まれていません"

            # 順序確認: Step 1 < Step 2 < Step 3
            assert step1_match.start() < step2_match.start(), (
                f"{file_path} で Step 1 が Step 2 より後に出現しています"
            )
            assert step2_match.start() < step3_match.start(), (
                f"{file_path} で Step 2 が Step 3 より後に出現しています"
            )

    def test_no_recommendation_wording_in_entire_file(self, file_contents):
        """異常系: ファイル全体で「推奨」が残っていないことを厳密にチェック（拡張版）"""
        for file_path, content in file_contents.items():
            # より広範囲に「推奨」を検索（前後100文字以内にCodex/委任/delegateが含まれる場合）
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "推奨" in line:
                    # 前後5行以内にCodex関連のキーワードがあるか確認
                    context_start = max(0, i - 5)
                    context_end = min(len(lines), i + 6)
                    context = "\n".join(lines[context_start:context_end])
                    if re.search(r"(Codex|委任|delegate)", context, re.IGNORECASE):
                        pytest.fail(
                            f"{file_path}:{i+1} に「推奨」が残っています（コンテキスト内にCodex関連キーワード検出）: {line}"
                        )

    def test_required_command_not_missing(self, file_contents):
        """異常系: where codex コマンドが欠落していないことを確認（表記ゆれ検出）"""
        for file_path, content in file_contents.items():
            # where codex 2>nul のパターンが正確に含まれているか
            # 表記ゆれ（スペース不足、typo等）を検出
            patterns_to_check = [
                r"where\s+codex\s+2>nul",  # 正規表現
                "where codex 2>nul",  # 文字列一致
            ]
            found = False
            for pattern in patterns_to_check:
                if isinstance(pattern, str) and pattern in content:
                    found = True
                    break
                elif re.search(pattern, content):
                    found = True
                    break

            assert found, f"{file_path} に `where codex 2>nul` コマンドが含まれていません（表記ゆれの可能性）"

    def test_required_headings_exist(self, file_contents):
        """境界値: 必須見出しセット（Step 1, 2, 3）が全て存在すること"""
        required_headings = [
            r"^#{2,6}\s*Step\s+1:\s*Codex\s+CLI存在確認",
            r"^#{2,6}\s*Step\s+2:.*?Codex委任",
            r"^#{2,6}\s*Step\s+3:",
        ]

        for file_path, content in file_contents.items():
            for heading_pattern in required_headings:
                assert re.search(heading_pattern, content, re.IGNORECASE | re.MULTILINE), (
                    f"{file_path} に必須見出し「{heading_pattern}」が含まれていません"
                )

    def test_step3_mentions_fallback(self, step_sections):
        """境界値: Step 3がフォールバック（Claude Code）に関する記述を含むこと"""
        for file_path, sections in step_sections.items():
            step3_content = sections["step3"]
            if step3_content:
                # Step 3内に「フォールバック」または「Claude Code」が含まれるか確認
                assert re.search(
                    r"(フォールバック|Claude\s+Code)", step3_content, re.IGNORECASE
                ), f"{file_path} の Step 3 にフォールバックに関する記述が含まれていません"

    def test_step1_semantic_content(self, step_sections):
        """テスト品質: Step 1セクション内に「原則」の説明文が含まれること（意味的検証）"""
        for file_path, sections in step_sections.items():
            step1_content = sections["step1"]
            assert step1_content is not None, f"{file_path} に Step 1 が存在しません"
            # Step 1内に「原則として、すべてのレビューはCodex CLIに委任すること」が含まれるか確認
            assert re.search(
                r"原則として.*Codex\s+CLI.*委任", step1_content, re.IGNORECASE | re.DOTALL
            ), f"{file_path} の Step 1 に「原則として...Codex CLI...委任」の説明文が含まれていません"

    def test_step2_semantic_content(self, step_sections):
        """テスト品質: Step 2セクション内にCodex委任の実行手順が含まれること（意味的検証）"""
        for file_path, sections in step_sections.items():
            step2_content = sections["step2"]
            assert step2_content is not None, f"{file_path} に Step 2 が存在しません"
            # Step 2内に「codex-delegate」または「Codex委任」が含まれるか確認
            assert re.search(
                r"codex-delegate|Codex委任", step2_content, re.IGNORECASE
            ), f"{file_path} の Step 2 にCodex委任の実行手順が含まれていません"

    def test_step3_semantic_content(self, step_sections):
        """テスト品質: Step 3セクション内にフォールバック条件が含まれること（意味的検証）"""
        for file_path, sections in step_sections.items():
            step3_content = sections["step3"]
            assert step3_content is not None, f"{file_path} に Step 3 が存在しません"
            # Step 3内に「Codex CLI利用不可条件」が含まれるか確認
            assert re.search(
                r"Codex\s+CLI利用不可条件", step3_content, re.IGNORECASE
            ), f"{file_path} の Step 3 にフォールバック条件の説明が含まれていません"
