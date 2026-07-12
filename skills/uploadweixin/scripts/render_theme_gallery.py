#!/usr/bin/env python3
"""Render one Markdown article into all uploadweixin themes and build a gallery."""

from __future__ import annotations

import argparse
import html
import os
from dataclasses import dataclass
from pathlib import Path

from cli_feedback import check_input_file, fail, prepare_output_dir
from make_preview import build_preview
from render_wechat_article import DEFAULT_FOOTER_TEXT, SUPPORTED_THEMES, render_article
from validate_wechat_html import validate_html


@dataclass
class ThemeResult:
    theme: str
    article_path: Path
    preview_path: Path
    validate_path: Path
    passed: bool
    message: str


def resolve_expect_footer(footer: str, expect_footer: str) -> str:
    if expect_footer != "auto":
        return expect_footer
    return "enabled" if footer == "enabled" else "disabled"


def write_validate_result(path: Path, errors: list[str]) -> tuple[bool, str]:
    if errors:
        message = "FAIL\n" + "\n".join(f"- {error}" for error in errors) + "\n"
        path.write_text(message, encoding="utf-8")
        return False, message.strip()
    message = "PASS\n"
    path.write_text(message, encoding="utf-8")
    return True, "PASS"


def build_gallery(input_path: Path, output_dir: Path, results: list[ThemeResult]) -> str:
    nav_items = []
    panels = []
    for result in results:
        rel_preview = html.escape(os.path.relpath(result.preview_path, output_dir))
        rel_article = html.escape(os.path.relpath(result.article_path, output_dir))
        rel_validate = html.escape(os.path.relpath(result.validate_path, output_dir))
        status_color = "#047857" if result.passed else "#b91c1c"
        status_text = "PASS" if result.passed else "FAIL"
        nav_items.append(
            f'<a href="#{html.escape(result.theme)}" style="display: inline-block; margin: 0 8px 8px 0; padding: 6px 10px; border: 1px solid #d1d5db; border-radius: 999px; color: #111827; text-decoration: none; font-size: 13px;">{html.escape(result.theme)}</a>'
        )
        panels.append(
            f"""
    <section id="{html.escape(result.theme)}" style="margin: 0 0 34px; padding: 18px; border: 1px solid #d1d5db; border-radius: 10px; background: #ffffff;">
      <h2 style="margin: 0 0 10px; color: #111827; font-size: 20px; line-height: 1.35;">{html.escape(result.theme)}</h2>
      <p style="margin: 0 0 14px; color: {status_color}; font-size: 14px;">validate: {status_text} · <a href="{rel_article}" style="color: #2563eb;">article.html</a> · <a href="{rel_preview}" style="color: #2563eb;">preview.html</a> · <a href="{rel_validate}" style="color: #2563eb;">validate.txt</a></p>
      <iframe src="{rel_preview}" title="{html.escape(result.theme)} preview" style="width: 100%; height: 760px; border: 1px solid #e5e7eb; border-radius: 8px; background: #ffffff;"></iframe>
    </section>"""
        )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>uploadweixin Theme Gallery</title>
</head>
<body style="margin: 0; padding: 28px; background: #f3f4f6; color: #111827; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif;">
  <main style="max-width: 1120px; margin: 0 auto;">
    <h1 style="margin: 0 0 8px; font-size: 28px; line-height: 1.3;">uploadweixin Theme Gallery</h1>
    <p style="margin: 0 0 18px; color: #4b5563; font-size: 14px; line-height: 1.7;">Input: {html.escape(str(input_path))}</p>
    <nav style="margin: 0 0 24px;">{"".join(nav_items)}</nav>
{"".join(panels)}
  </main>
</body>
</html>
"""


def render_all_themes(input_path: Path, output_dir: Path, footer: str, footer_text: str, expect_footer: str) -> list[ThemeResult]:
    results: list[ThemeResult] = []
    resolved_expect_footer = resolve_expect_footer(footer, expect_footer)

    for theme in SUPPORTED_THEMES:
        theme_dir = output_dir / theme
        theme_dir.mkdir(parents=True, exist_ok=True)
        article_path = theme_dir / "article.html"
        preview_path = theme_dir / "preview.html"
        validate_path = theme_dir / "validate.txt"

        article_html = render_article(input_path, theme, footer, footer_text)
        article_path.write_text(article_html + "\n", encoding="utf-8")
        preview_path.write_text(build_preview(article_html), encoding="utf-8")
        errors = validate_html(article_html, resolved_expect_footer, footer_text)
        passed, message = write_validate_result(validate_path, errors)
        results.append(ThemeResult(theme, article_path, preview_path, validate_path, passed, message))

    gallery_path = output_dir / "gallery.html"
    gallery_path.write_text(build_gallery(input_path, output_dir, results), encoding="utf-8")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Render one Markdown file into all uploadweixin themes.")
    parser.add_argument("--input", required=True, help="Markdown input file.")
    parser.add_argument("--output", required=True, help="Output directory for all theme samples.")
    parser.add_argument("--footer", choices=("enabled", "disabled"), default="enabled", help="Append Upload footer.")
    parser.add_argument("--footer-text", default=DEFAULT_FOOTER_TEXT, help="Footer copy.")
    parser.add_argument(
        "--expect-footer",
        choices=("auto", "any", "enabled", "disabled"),
        default="auto",
        help="Footer assertion for validation. auto follows --footer.",
    )
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    input_suggestions = check_input_file(input_path, "Markdown 输入文件")
    if input_suggestions:
        return fail("Markdown 输入文件不存在。", input_suggestions)

    output_dir = Path(args.output).expanduser().resolve()
    ok, output_suggestions = prepare_output_dir(output_dir)
    if not ok:
        return fail("批量主题输出目录不可用。", output_suggestions)

    results = render_all_themes(input_path, output_dir, args.footer, args.footer_text, args.expect_footer)

    for result in results:
        print(f"{'PASS' if result.passed else 'FAIL'} {result.theme} article={result.article_path} preview={result.preview_path} validate={result.validate_path}")
    print(f"PASS gallery={output_dir / 'gallery.html'}")

    if not all(result.passed for result in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
