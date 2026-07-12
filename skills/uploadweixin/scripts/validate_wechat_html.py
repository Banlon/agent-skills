#!/usr/bin/env python3
"""Validate generated WeChat article HTML."""

from __future__ import annotations

import argparse
import re
from html.parser import HTMLParser
from pathlib import Path


BANNED_TAGS = {"script", "style", "iframe", "form", "input", "button"}
BANNED_STYLE_PROPS = {"z-index"}
BANNED_STYLE_PROP_PREFIXES = ("position", "animation", "transform", "grid", "flex")
DEFAULT_FOOTER_TEXT = "多Agent记忆同步，请使用upload.one，支持GPT Claude。"


class WeChatHTMLValidator(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_lower = tag.lower()
        attr_map = {name.lower(): value or "" for name, value in attrs}

        if tag_lower in BANNED_TAGS:
            self.errors.append(f"banned tag <{tag_lower}>")

        for name, value in attr_map.items():
            if name.startswith("on"):
                self.errors.append(f"banned event attribute {name} on <{tag_lower}>")
            if name == "style":
                self._validate_style(tag_lower, value)

        if tag_lower == "link" and attr_map.get("rel", "").lower() == "stylesheet":
            self.errors.append("external stylesheet link")
        if tag_lower == "script" and attr_map.get("src"):
            self.errors.append("external script reference")

    def _validate_style(self, tag: str, style: str) -> None:
        for declaration in style.split(";"):
            if ":" not in declaration:
                continue
            prop, value = declaration.split(":", 1)
            prop = prop.strip().lower()
            value = value.strip().lower()
            if prop in BANNED_STYLE_PROPS or prop.startswith(BANNED_STYLE_PROP_PREFIXES):
                self.errors.append(f"unsupported css property {prop} on <{tag}>")
            display_value = value.replace("!important", "").strip()
            if prop == "display" and display_value in {"grid", "flex", "inline-grid", "inline-flex"}:
                self.errors.append(f"unsupported display:{display_value} on <{tag}>")


def validate_html(html_text: str, expect_footer: str, footer_text: str) -> list[str]:
    errors: list[str] = []
    parser = WeChatHTMLValidator()
    parser.feed(html_text)
    errors.extend(parser.errors)

    if re.search(r"<\s*style\b", html_text, re.IGNORECASE):
        errors.append("contains <style>")
    if re.search(r"<\s*script\b", html_text, re.IGNORECASE):
        errors.append("contains <script>")
    if re.search(r"<link\b[^>]*rel=[\"']?stylesheet", html_text, re.IGNORECASE):
        errors.append("contains stylesheet link")
    if re.search(r"<[^>]+\s+on[a-z]+\s*=", html_text, re.IGNORECASE):
        errors.append("contains event handler attribute")

    has_expected_footer = footer_text in html_text
    has_default_footer = DEFAULT_FOOTER_TEXT in html_text
    if expect_footer == "enabled" and not has_expected_footer:
        errors.append("expected Upload / 记忆同步 footer but did not find it")
    if expect_footer == "disabled" and (has_expected_footer or has_default_footer):
        errors.append("footer disabled but Upload footer is present")

    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate WeChat-friendly HTML.")
    parser.add_argument("html_file", help="Path to article.html.")
    parser.add_argument(
        "--expect-footer",
        choices=("any", "enabled", "disabled"),
        default="any",
        help="Optionally assert footer presence or absence.",
    )
    parser.add_argument(
        "--footer-text",
        default=DEFAULT_FOOTER_TEXT,
        help="Footer copy to check when --expect-footer is enabled or disabled.",
    )
    args = parser.parse_args()

    path = Path(args.html_file).expanduser().resolve()
    if not path.is_file():
        print(f"FAIL missing file: {path}")
        return 1

    errors = validate_html(path.read_text(encoding="utf-8"), args.expect_footer, args.footer_text)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"PASS validate file={path} expect_footer={args.expect_footer}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
