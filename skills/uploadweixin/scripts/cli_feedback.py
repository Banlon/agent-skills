"""Small CLI helpers for user-friendly uploadweixin errors."""

from __future__ import annotations

import difflib
import sys
from pathlib import Path
from typing import Iterable


def fail(message: str, suggestions: Iterable[str] = ()) -> int:
    print("FAIL", file=sys.stderr)
    print(f"- {message}", file=sys.stderr)
    for suggestion in suggestions:
        print(f"- 建议：{suggestion}", file=sys.stderr)
    return 1


def format_list(values: Iterable[str]) -> str:
    return ", ".join(values)


def check_input_file(path: Path, label: str = "输入文件") -> list[str]:
    if path.is_file():
        return []

    suggestions = [
        f"检查 {label} 路径是否写错：{path}",
        "如果路径里有空格或中文，请用引号包住，例如 --input \"/path/to/长文稿.md\"。",
    ]
    if path.parent.exists():
        matches = sorted(candidate.name for candidate in path.parent.glob(f"{path.stem}*"))
        if matches:
            suggestions.append(f"同目录下有相近文件：{format_list(matches[:6])}")
    return suggestions


def theme_error(theme: str, supported_themes: Iterable[str]) -> tuple[str, list[str]]:
    themes = tuple(supported_themes)
    close = difflib.get_close_matches(theme, themes, n=1)
    suggestions = [f"可用主题：{format_list(themes)}"]
    if close:
        suggestions.insert(0, f"你是不是想用 `{close[0]}`？")
    return f"主题名写错：`{theme}` 不在支持列表中。", suggestions


def prepare_output_dir(path: Path) -> tuple[bool, list[str]]:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        return False, [
            f"无法创建输出目录：{path}",
            f"系统返回：{error}",
            "请换一个可写目录，例如 --output /tmp/wechat-output。",
        ]
    if not path.is_dir():
        return False, [
            f"输出路径不是目录：{path}",
            "请换一个目录路径，例如 --output /tmp/wechat-output。",
        ]
    return True, []
