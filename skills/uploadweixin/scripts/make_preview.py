#!/usr/bin/env python3
"""Create a local preview page for generated WeChat article HTML."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from cli_feedback import check_input_file, fail, prepare_output_dir


def build_preview(article_html: str) -> str:
    escaped_source = html.escape(article_html)
    article_json = json.dumps(article_html, ensure_ascii=False)
    template = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>WeChat Article Rich Copy</title>
  <style>
    body {
      margin: 0;
      padding: 28px;
      background: #f3f4f6;
      color: #111827;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    main {
      max-width: 920px;
      margin: 0 auto;
    }
    .panel {
      margin-bottom: 24px;
      padding: 24px;
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      background: #ffffff;
    }
    h1 {
      margin: 0 0 16px;
      font-size: 18px;
      line-height: 1.4;
    }
    .toolbar {
      margin-bottom: 18px;
      padding: 16px;
      border: 1px solid #dbeafe;
      border-radius: 8px;
      background: #eff6ff;
    }
    button {
      appearance: none;
      border: 0;
      border-radius: 6px;
      padding: 10px 14px;
      background: #2563eb;
      color: #ffffff;
      font-size: 14px;
      font-weight: 700;
      cursor: pointer;
    }
    .hint {
      margin: 10px 0 0;
      color: #475569;
      font-size: 13px;
      line-height: 1.6;
    }
    .status {
      margin-left: 10px;
      color: #047857;
      font-size: 13px;
    }
    #richArticle {
      outline: 0;
    }
    textarea {
      width: 100%;
      min-height: 360px;
      box-sizing: border-box;
      padding: 14px;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      color: #111827;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 13px;
      line-height: 1.6;
    }
  </style>
</head>
<body>
  <main>
    <section class="toolbar">
      <button type="button" id="copyRich">复制到公众号编辑器</button>
      <span class="status" id="copyStatus"></span>
      <p class="hint">先点这个按钮，再去公众号编辑器粘贴。不要直接框选 article.html 复制；不要经过跨设备剪贴板或输入法同步，它们通常只保留纯文本。</p>
      <p class="hint">如果粘贴后仍是纯文本，请在同一台 Mac 上运行 skill 的 macOS 富文本剪贴板脚本，把 article.html 直接写入系统剪贴板。</p>
    </section>
    <section class="panel">
      <h1>Preview</h1>
      <section id="richArticle" contenteditable="true">
        %%ARTICLE_HTML%%
      </section>
    </section>
    <section class="panel">
      <h1>Source HTML</h1>
      <textarea readonly>%%ESCAPED_SOURCE%%</textarea>
    </section>
  </main>
  <script>
    const articleHtml = %%ARTICLE_JSON%%;
    const statusEl = document.getElementById('copyStatus');
    const richArticle = document.getElementById('richArticle');

    function selectRichArticle() {
      const range = document.createRange();
      range.selectNodeContents(richArticle);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
    }

    async function copyRichArticle() {
      try {
        if (navigator.clipboard && window.ClipboardItem) {
          const htmlBlob = new Blob([articleHtml], { type: 'text/html' });
          const textBlob = new Blob([richArticle.innerText], { type: 'text/plain' });
          await navigator.clipboard.write([
            new ClipboardItem({
              'text/html': htmlBlob,
              'text/plain': textBlob
            })
          ]);
          statusEl.textContent = '已复制富文本，可去公众号粘贴';
          return;
        }
      } catch (error) {
        // Fall through to selection-based copy.
      }

      selectRichArticle();
      const copied = document.execCommand('copy');
      statusEl.textContent = copied
        ? '已复制富文本，可去公众号粘贴'
        : '已选中正文，请按 Cmd+C 后再去公众号粘贴';
    }

    document.getElementById('copyRich').addEventListener('click', copyRichArticle);
  </script>
</body>
</html>
"""
    return (
        template
        .replace("%%ARTICLE_HTML%%", article_html)
        .replace("%%ESCAPED_SOURCE%%", escaped_source)
        .replace("%%ARTICLE_JSON%%", article_json)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Create local preview HTML.")
    parser.add_argument("--input", required=True, help="Input article.html path.")
    parser.add_argument("--output", required=True, help="Output preview.html path.")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    input_suggestions = check_input_file(input_path, "article.html 输入文件")
    if input_suggestions:
        return fail("article.html 输入文件不存在。", input_suggestions)

    output_path = Path(args.output).expanduser().resolve()
    ok, output_suggestions = prepare_output_dir(output_path.parent)
    if not ok:
        return fail("preview.html 输出目录不可用。", output_suggestions)

    preview_html = build_preview(input_path.read_text(encoding="utf-8"))
    try:
        output_path.write_text(preview_html, encoding="utf-8")
    except OSError as error:
        return fail(
            "写入 preview.html 失败。",
            [
                f"目标路径：{output_path}",
                f"系统返回：{error}",
                "请确认输出目录可写，或改用 --output /tmp/wechat-output/preview.html。",
            ],
        )
    print(f"PASS preview={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
