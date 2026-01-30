"""
プロジェクトパス正規化モジュール

Claude Codeのプロジェクトパス形式（D--projects-P010）とWindowsパス形式の相互変換を行う。
"""

import re
from pathlib import Path
from typing import Union

# 定数定義
_DRIVE_SEPARATOR = "--"  # ドライブレター後の区切り文字（例: "D:" → "D--"）
_PATH_SEPARATOR = "-"    # パス区切り文字（例: "\\" → "-"）
_HEURISTIC_SPLIT_INDEX = 3  # パス復元時の分割位置


def normalize_path(path: Union[str, Path]) -> str:
    r"""
    Windowsパスを Claude Code 形式に正規化する

    Args:
        path: Windowsパス（文字列またはPathlibのPath）

    Returns:
        正規化されたパス（例: "D--projects-P010"）

    Raises:
        ValueError: パスが空の場合、または不正なパスの場合

    Examples:
        >>> normalize_path(r"D:\projects\P010")
        'D--projects-P010'
        >>> normalize_path(r"D:\projects\P010\worktrees\issue-105")
        'D--projects-P010-worktrees-issue-105'
    """
    if not path:
        raise ValueError("Path cannot be empty")

    path_str = str(path)

    # セキュリティチェック: /区切りは許可しない
    if "/" in path_str:
        raise ValueError("Forward slashes are not allowed. Use backslashes instead.")

    # セキュリティチェック: UNCパスは許可しない
    if path_str.startswith("\\\\"):
        raise ValueError("UNC paths are not allowed")

    # セキュリティチェック: 相対パス成分（.. または .）は許可しない
    path_parts = path_str.split("\\")
    if ".." in path_parts or "." in path_parts:
        raise ValueError("Relative path components (. or ..) are not allowed")

    # 連続するバックスラッシュを正規化
    path_str = re.sub(r'\\+', r'\\', path_str)

    # ドライブレター部分を変換（":\\" → "--"）
    path_str = path_str.replace(":\\", _DRIVE_SEPARATOR)

    # パス区切りを変換（"\\" → "-"）
    path_str = path_str.replace("\\", _PATH_SEPARATOR)

    return path_str


def denormalize_path(normalized_path: str) -> Path:
    """
    Claude Code 形式のパスを Windowsパスに変換する

    注意: ディレクトリ名に含まれる "-" とパス区切りの "-" を
    区別できないため、ヒューリスティックで推測します。
    実在するパスは自動検出されます。

    Args:
        normalized_path: 正規化されたパス（例: "D--projects-P010"）

    Returns:
        WindowsパスのPathオブジェクト

    Raises:
        ValueError: パスが空の場合、または不正なフォーマットの場合

    Examples:
        >>> denormalize_path("D--projects-P010")
        WindowsPath('D:/projects/P010')
    """
    if not normalized_path:
        raise ValueError("Path cannot be empty")

    _validate_format(normalized_path)

    drive_letter = normalized_path[0]
    segments_str = normalized_path[3:]

    if not segments_str:
        return Path(f"{drive_letter}:\\")

    segments = segments_str.split(_PATH_SEPARATOR)

    # 実在するパスを検索
    existing_path = _find_existing_path(drive_letter, segments)
    if existing_path:
        return existing_path

    # 存在しない場合はヒューリスティックで構築
    reconstructed_segments = _reconstruct_segments(segments)
    return _build_windows_path(drive_letter, reconstructed_segments)


def _validate_format(normalized_path: str) -> None:
    """
    正規化パスのフォーマットを検証する

    Args:
        normalized_path: 検証対象のパス

    Raises:
        ValueError: フォーマットが不正な場合
    """
    if len(normalized_path) < 3 or normalized_path[1:3] != _DRIVE_SEPARATOR:
        raise ValueError("Invalid normalized path format")

    # ドライブレターの検証（大文字A-Zのみ許可）
    drive_letter = normalized_path[0]
    if not drive_letter.isupper() or not drive_letter.isalpha():
        raise ValueError(f"Invalid drive letter: {drive_letter}. Only uppercase A-Z are allowed.")

    # セグメントの検証
    segments_str = normalized_path[3:]
    if segments_str:
        segments = segments_str.split(_PATH_SEPARATOR)

        # 空セグメントの検証
        if any(seg == "" for seg in segments):
            raise ValueError("Empty path segments are not allowed")

        # パス逸脱の検証（. または ..）
        if ".." in segments or "." in segments:
            raise ValueError("Path traversal components (. or ..) are not allowed")


def _find_existing_path(drive: str, segments: list[str]) -> Path | None:
    """
    実在するパスを検索する

    Args:
        drive: ドライブレター
        segments: パスセグメントのリスト

    Returns:
        実在するパス、または None
    """
    candidates = _generate_path_candidates(drive, segments)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def _generate_path_candidates(drive: str, segments: list[str]) -> list[Path]:
    """
    パス候補を生成する

    Args:
        drive: ドライブレター
        segments: パスセグメントのリスト

    Returns:
        候補パスのリスト
    """
    candidates = []

    # 最も単純なケース: すべて独立したセグメント
    candidates.append(_build_windows_path(drive, segments))

    # 5個以上のセグメントがある場合、結合パターンを試す
    if len(segments) >= 5:
        for split_idx in range(3, len(segments)):
            merged_segments = segments[:split_idx] + [
                _PATH_SEPARATOR.join(segments[split_idx:])
            ]
            candidates.append(_build_windows_path(drive, merged_segments))

    return candidates


def _reconstruct_segments(segments: list[str]) -> list[str]:
    """
    ヒューリスティックでセグメントを再構築する

    最初の3つのセグメントは独立したディレクトリとして扱い、
    それ以降は結合して単一のセグメントとする。

    Args:
        segments: 元のセグメントリスト

    Returns:
        再構築されたセグメントリスト
    """
    if len(segments) <= _HEURISTIC_SPLIT_INDEX:
        return segments

    return (
        segments[:_HEURISTIC_SPLIT_INDEX]
        + [_PATH_SEPARATOR.join(segments[_HEURISTIC_SPLIT_INDEX:])]
    )


def _build_windows_path(drive: str, segments: list[str]) -> Path:
    """
    Windowsパスを構築する

    Args:
        drive: ドライブレター
        segments: パスセグメントのリスト

    Returns:
        構築されたWindowsパス
    """
    return Path(f"{drive}:\\{'\\'.join(segments)}")
