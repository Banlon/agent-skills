#!/usr/bin/env python3
"""Render Markdown into WeChat Official Account friendly HTML."""

from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from cli_feedback import check_input_file, fail, prepare_output_dir, theme_error


DEFAULT_FOOTER_TEXT = "多Agent记忆同步，请使用upload.one，支持GPT Claude。"
SUPPORTED_THEMES = (
    "upload-clean",
    "tech-blue",
    "github-dev",
    "editorial",
    "ink",
    "newspaper",
    "sspai-red",
    "mint-card",
    "amber-note",
    "bauhaus",
    "timeline",
    "dialogue",
)


THEMES = {
    "upload-clean": {
        "root": "max-width: 680px; margin: 0 auto; color: #1f2937; font-size: 16px; line-height: 1.85; background: #ffffff;",
        "h1": "margin: 0 0 24px; padding-bottom: 12px; border-bottom: 2px solid #0f766e; color: #111827; font-size: 26px; line-height: 1.35; font-weight: 700;",
        "h2": "margin: 32px 0 14px; padding-bottom: 8px; border-bottom: 1px solid #d1d5db; color: #111827; font-size: 22px; line-height: 1.45; font-weight: 700;",
        "h3": "margin: 26px 0 12px; color: #0f766e; font-size: 18px; line-height: 1.55; font-weight: 700;",
        "p": "margin: 0 0 18px; color: #374151; font-size: 16px; line-height: 1.85;",
        "blockquote": "margin: 22px 0; padding: 14px 16px; border-left: 4px solid #14b8a6; background: #f0fdfa; color: #334155; font-size: 15px; line-height: 1.8;",
        "ul": "margin: 0 0 18px; padding-left: 24px; color: #374151; font-size: 16px; line-height: 1.8;",
        "ol": "margin: 0 0 18px; padding-left: 24px; color: #374151; font-size: 16px; line-height: 1.8;",
        "li": "margin: 6px 0;",
        "pre": "margin: 20px 0; padding: 14px 16px; overflow-x: auto; border-radius: 6px; background: #f3f4f6; color: #111827; font-size: 14px; line-height: 1.7;",
        "code": "padding: 2px 5px; border-radius: 4px; background: #ecfdf5; color: #065f46; font-size: 0.92em;",
        "img": "display: block; max-width: 100%; height: auto; margin: 22px auto 8px;",
        "caption": "margin: 0 0 22px; color: #64748b; font-size: 13px; line-height: 1.7; text-align: center;",
        "hr": "margin: 30px 0; border: 0; border-top: 1px solid #d1d5db;",
        "strong": "font-weight: 700; color: #111827;",
        "a": "color: #0f766e; text-decoration: underline;",
        "footer": "margin-top: 32px; padding-top: 16px; border-top: 1px solid #d1d5db; color: #64748b; font-size: 14px; line-height: 1.8;",
    },
    "tech-blue": {
        "root": "max-width: 680px; margin: 0 auto; color: #172554; font-size: 16px; line-height: 1.86; background: #ffffff;",
        "h1": "margin: 0 0 24px; padding: 16px 18px; border-left: 5px solid #2563eb; background: #eff6ff; color: #1e3a8a; font-size: 27px; line-height: 1.35; font-weight: 800;",
        "h2": "margin: 34px 0 14px; padding: 0 0 8px; border-bottom: 2px solid #bfdbfe; color: #1d4ed8; font-size: 22px; line-height: 1.45; font-weight: 700;",
        "h3": "margin: 26px 0 12px; color: #1e40af; font-size: 18px; line-height: 1.55; font-weight: 700;",
        "p": "margin: 0 0 18px; color: #1f2937; font-size: 16px; line-height: 1.86;",
        "blockquote": "margin: 22px 0; padding: 14px 16px; border-left: 4px solid #60a5fa; background: #eff6ff; color: #1e3a8a; font-size: 15px; line-height: 1.82;",
        "ul": "margin: 0 0 18px; padding-left: 24px; color: #1f2937; font-size: 16px; line-height: 1.82;",
        "ol": "margin: 0 0 18px; padding-left: 24px; color: #1f2937; font-size: 16px; line-height: 1.82;",
        "li": "margin: 6px 0;",
        "pre": "margin: 20px 0; padding: 15px 16px; overflow-x: auto; border-radius: 6px; background: #0f172a; color: #dbeafe; font-size: 14px; line-height: 1.72;",
        "code": "padding: 2px 5px; border-radius: 4px; background: #dbeafe; color: #1e40af; font-size: 0.92em;",
        "img": "display: block; max-width: 100%; height: auto; margin: 22px auto 8px; border-radius: 6px;",
        "caption": "margin: 0 0 22px; color: #64748b; font-size: 13px; line-height: 1.7; text-align: center;",
        "hr": "margin: 30px 0; border: 0; border-top: 1px solid #bfdbfe;",
        "strong": "font-weight: 700; color: #1d4ed8;",
        "a": "color: #2563eb; text-decoration: underline;",
        "footer": "margin-top: 32px; padding: 14px 16px; border-top: 1px solid #bfdbfe; background: #eff6ff; color: #475569; font-size: 14px; line-height: 1.8;",
    },
    "github-dev": {
        "root": "max-width: 680px; margin: 0 auto; color: #24292f; font-size: 16px; line-height: 1.82; background: #ffffff; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif;",
        "h1": "margin: 0 0 22px; padding-bottom: 12px; border-bottom: 1px solid #d0d7de; color: #24292f; font-size: 28px; line-height: 1.35; font-weight: 700;",
        "h2": "margin: 32px 0 14px; padding-bottom: 7px; border-bottom: 1px solid #d0d7de; color: #24292f; font-size: 22px; line-height: 1.45; font-weight: 700;",
        "h3": "margin: 24px 0 10px; color: #24292f; font-size: 18px; line-height: 1.5; font-weight: 700;",
        "p": "margin: 0 0 16px; color: #24292f; font-size: 16px; line-height: 1.82;",
        "blockquote": "margin: 20px 0; padding: 0 16px; border-left: 4px solid #d0d7de; color: #57606a; font-size: 15px; line-height: 1.8;",
        "ul": "margin: 0 0 16px; padding-left: 24px; color: #24292f; font-size: 16px; line-height: 1.8;",
        "ol": "margin: 0 0 16px; padding-left: 24px; color: #24292f; font-size: 16px; line-height: 1.8;",
        "li": "margin: 5px 0;",
        "pre": "margin: 18px 0; padding: 16px; overflow-x: auto; border-radius: 6px; background: #f6f8fa; color: #24292f; font-size: 14px; line-height: 1.7;",
        "code": "padding: 2px 5px; border-radius: 4px; background: #eef2f7; color: #24292f; font-size: 0.92em;",
        "img": "display: block; max-width: 100%; height: auto; margin: 22px auto 8px; border: 1px solid #d0d7de; border-radius: 6px;",
        "caption": "margin: 0 0 22px; color: #57606a; font-size: 13px; line-height: 1.7; text-align: center;",
        "hr": "margin: 28px 0; border: 0; border-top: 1px solid #d8dee4;",
        "strong": "font-weight: 700; color: #24292f;",
        "a": "color: #0969da; text-decoration: underline;",
        "footer": "margin-top: 30px; padding-top: 14px; border-top: 1px solid #d0d7de; color: #57606a; font-size: 14px; line-height: 1.75;",
    },
    "editorial": {
        "root": "max-width: 680px; margin: 0 auto; color: #1f2937; font-size: 16px; line-height: 1.9; background: #ffffff; font-family: Georgia, Times New Roman, serif;",
        "h1": "margin: 0 0 28px; color: #111827; font-size: 30px; line-height: 1.3; font-weight: 800;",
        "h2": "margin: 36px 0 16px; color: #111827; font-size: 23px; line-height: 1.4; font-weight: 800;",
        "h3": "margin: 28px 0 12px; color: #111827; font-size: 19px; line-height: 1.5; font-weight: 700;",
        "p": "margin: 0 0 20px; color: #2f3742; font-size: 16px; line-height: 1.9;",
        "blockquote": "margin: 26px 0; padding: 4px 0 4px 18px; border-left: 3px solid #111827; color: #4b5563; font-size: 17px; line-height: 1.9;",
        "ul": "margin: 0 0 20px; padding-left: 24px; color: #2f3742; font-size: 16px; line-height: 1.9;",
        "ol": "margin: 0 0 20px; padding-left: 24px; color: #2f3742; font-size: 16px; line-height: 1.9;",
        "li": "margin: 7px 0;",
        "pre": "margin: 22px 0; padding: 16px 18px; overflow-x: auto; border-radius: 6px; background: #f5f5f4; color: #1f2937; font-size: 14px; line-height: 1.75; font-family: Menlo, Consolas, monospace;",
        "code": "padding: 2px 5px; border-radius: 4px; background: #f5f5f4; color: #111827; font-size: 0.92em; font-family: Menlo, Consolas, monospace;",
        "img": "display: block; max-width: 100%; height: auto; margin: 26px auto 8px;",
        "caption": "margin: 0 0 26px; color: #71717a; font-size: 13px; line-height: 1.75; text-align: center; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif;",
        "hr": "margin: 34px auto; width: 72px; border: 0; border-top: 2px solid #111827;",
        "strong": "font-weight: 800; color: #111827;",
        "a": "color: #111827; text-decoration: underline;",
        "footer": "margin-top: 36px; padding-top: 16px; border-top: 1px solid #d1d5db; color: #6b7280; font-size: 14px; line-height: 1.85; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif;",
    },
    "ink": {
        "root": "max-width: 680px; margin: 0 auto; color: #1c1917; font-size: 16px; line-height: 1.92; background: #fffdf8; font-family: Songti SC, SimSun, serif;",
        "h1": "margin: 0 0 26px; padding-bottom: 14px; border-bottom: 1px solid #1c1917; color: #1c1917; font-size: 29px; line-height: 1.35; font-weight: 700;",
        "h2": "margin: 34px 0 16px; color: #292524; font-size: 22px; line-height: 1.48; font-weight: 700;",
        "h3": "margin: 26px 0 12px; color: #57534e; font-size: 18px; line-height: 1.6; font-weight: 700;",
        "p": "margin: 0 0 19px; color: #292524; font-size: 16px; line-height: 1.92;",
        "blockquote": "margin: 24px 0; padding: 12px 16px; border-left: 3px solid #78716c; background: #fafaf9; color: #44403c; font-size: 16px; line-height: 1.9;",
        "ul": "margin: 0 0 19px; padding-left: 24px; color: #292524; font-size: 16px; line-height: 1.9;",
        "ol": "margin: 0 0 19px; padding-left: 24px; color: #292524; font-size: 16px; line-height: 1.9;",
        "li": "margin: 7px 0;",
        "pre": "margin: 22px 0; padding: 15px 16px; overflow-x: auto; border-radius: 4px; background: #292524; color: #fafaf9; font-size: 14px; line-height: 1.75; font-family: Menlo, Consolas, monospace;",
        "code": "padding: 2px 5px; border-radius: 4px; background: #e7e5e4; color: #1c1917; font-size: 0.92em; font-family: Menlo, Consolas, monospace;",
        "img": "display: block; max-width: 100%; height: auto; margin: 24px auto 8px;",
        "caption": "margin: 0 0 24px; color: #78716c; font-size: 13px; line-height: 1.7; text-align: center;",
        "hr": "margin: 32px auto; width: 88px; border: 0; border-top: 1px solid #78716c;",
        "strong": "font-weight: 700; color: #1c1917;",
        "a": "color: #57534e; text-decoration: underline;",
        "footer": "margin-top: 34px; padding-top: 15px; border-top: 1px solid #d6d3d1; color: #78716c; font-size: 14px; line-height: 1.85;",
    },
    "newspaper": {
        "root": "max-width: 680px; margin: 0 auto; color: #1f1f1f; font-size: 16px; line-height: 1.78; background: #fffaf0; font-family: Georgia, Times New Roman, serif;",
        "h1": "margin: 0 0 20px; padding: 12px 0; border-top: 3px double #1f1f1f; border-bottom: 3px double #1f1f1f; color: #111111; font-size: 31px; line-height: 1.25; font-weight: 800; text-align: center;",
        "h2": "margin: 32px 0 14px; padding-bottom: 6px; border-bottom: 1px solid #1f1f1f; color: #111111; font-size: 22px; line-height: 1.4; font-weight: 800;",
        "h3": "margin: 24px 0 10px; color: #3f3f3f; font-size: 18px; line-height: 1.5; font-weight: 700;",
        "p": "margin: 0 0 17px; color: #262626; font-size: 16px; line-height: 1.78;",
        "blockquote": "margin: 22px 0; padding: 12px 15px; border-top: 1px solid #a8a29e; border-bottom: 1px solid #a8a29e; color: #44403c; font-size: 17px; line-height: 1.82;",
        "ul": "margin: 0 0 17px; padding-left: 24px; color: #262626; font-size: 16px; line-height: 1.78;",
        "ol": "margin: 0 0 17px; padding-left: 24px; color: #262626; font-size: 16px; line-height: 1.78;",
        "li": "margin: 6px 0;",
        "pre": "margin: 20px 0; padding: 14px 16px; overflow-x: auto; border: 1px solid #a8a29e; background: #f5f5f4; color: #1f1f1f; font-size: 14px; line-height: 1.7; font-family: Menlo, Consolas, monospace;",
        "code": "padding: 2px 5px; border: 1px solid #d6d3d1; background: #f5f5f4; color: #111111; font-size: 0.92em; font-family: Menlo, Consolas, monospace;",
        "img": "display: block; max-width: 100%; height: auto; margin: 22px auto 8px; border: 1px solid #a8a29e;",
        "caption": "margin: 0 0 22px; color: #57534e; font-size: 13px; line-height: 1.65; text-align: center; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif;",
        "hr": "margin: 30px 0; border: 0; border-top: 3px double #1f1f1f;",
        "strong": "font-weight: 800; color: #111111;",
        "a": "color: #111111; text-decoration: underline;",
        "footer": "margin-top: 32px; padding-top: 12px; border-top: 3px double #a8a29e; color: #57534e; font-size: 14px; line-height: 1.75; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif;",
    },
    "sspai-red": {
        "root": "max-width: 680px; margin: 0 auto; color: #1f2937; font-size: 16px; line-height: 1.86; background: #ffffff;",
        "h1": "margin: 0 0 24px; padding-bottom: 12px; border-bottom: 3px solid #d71920; color: #111827; font-size: 28px; line-height: 1.32; font-weight: 800;",
        "h2": "margin: 34px 0 14px; color: #d71920; font-size: 22px; line-height: 1.45; font-weight: 800;",
        "h3": "margin: 26px 0 12px; color: #991b1b; font-size: 18px; line-height: 1.55; font-weight: 700;",
        "p": "margin: 0 0 18px; color: #374151; font-size: 16px; line-height: 1.86;",
        "blockquote": "margin: 22px 0; padding: 14px 16px; border-left: 4px solid #d71920; background: #fff1f2; color: #4b5563; font-size: 15px; line-height: 1.82;",
        "ul": "margin: 0 0 18px; padding-left: 24px; color: #374151; font-size: 16px; line-height: 1.82;",
        "ol": "margin: 0 0 18px; padding-left: 24px; color: #374151; font-size: 16px; line-height: 1.82;",
        "li": "margin: 6px 0;",
        "pre": "margin: 20px 0; padding: 15px 16px; overflow-x: auto; border-radius: 6px; background: #111827; color: #fecaca; font-size: 14px; line-height: 1.72;",
        "code": "padding: 2px 5px; border-radius: 4px; background: #fee2e2; color: #991b1b; font-size: 0.92em;",
        "img": "display: block; max-width: 100%; height: auto; margin: 22px auto 8px; border-radius: 6px;",
        "caption": "margin: 0 0 22px; color: #6b7280; font-size: 13px; line-height: 1.7; text-align: center;",
        "hr": "margin: 30px auto; width: 96px; border: 0; border-top: 2px solid #d71920;",
        "strong": "font-weight: 800; color: #d71920;",
        "a": "color: #d71920; text-decoration: underline;",
        "footer": "margin-top: 32px; padding: 14px 16px; border-top: 1px solid #fecaca; background: #fff1f2; color: #6b7280; font-size: 14px; line-height: 1.8;",
    },
    "mint-card": {
        "root": "max-width: 680px; margin: 0 auto; padding: 18px; border: 1px solid #a7f3d0; border-radius: 8px; color: #164e3f; font-size: 16px; line-height: 1.86; background: #f7fffb;",
        "h1": "margin: 0 0 22px; padding: 16px; border-radius: 8px; background: #d1fae5; color: #064e3b; font-size: 27px; line-height: 1.35; font-weight: 800;",
        "h2": "margin: 32px 0 14px; padding: 10px 12px; border-left: 4px solid #10b981; background: #ecfdf5; color: #065f46; font-size: 21px; line-height: 1.45; font-weight: 700;",
        "h3": "margin: 24px 0 10px; color: #047857; font-size: 18px; line-height: 1.55; font-weight: 700;",
        "p": "margin: 0 0 17px; color: #1f2937; font-size: 16px; line-height: 1.86;",
        "blockquote": "margin: 22px 0; padding: 14px 16px; border: 1px solid #a7f3d0; border-radius: 8px; background: #ffffff; color: #065f46; font-size: 15px; line-height: 1.82;",
        "ul": "margin: 0 0 17px; padding-left: 24px; color: #1f2937; font-size: 16px; line-height: 1.82;",
        "ol": "margin: 0 0 17px; padding-left: 24px; color: #1f2937; font-size: 16px; line-height: 1.82;",
        "li": "margin: 6px 0;",
        "pre": "margin: 20px 0; padding: 15px 16px; overflow-x: auto; border-radius: 8px; background: #064e3b; color: #d1fae5; font-size: 14px; line-height: 1.72;",
        "code": "padding: 2px 5px; border-radius: 4px; background: #d1fae5; color: #065f46; font-size: 0.92em;",
        "img": "display: block; max-width: 100%; height: auto; margin: 22px auto 8px; border-radius: 8px;",
        "caption": "margin: 0 0 22px; color: #047857; font-size: 13px; line-height: 1.7; text-align: center;",
        "hr": "margin: 30px 0; border: 0; border-top: 1px dashed #6ee7b7;",
        "strong": "font-weight: 800; color: #047857;",
        "a": "color: #059669; text-decoration: underline;",
        "footer": "margin-top: 32px; padding: 14px 16px; border: 1px solid #a7f3d0; border-radius: 8px; background: #ffffff; color: #047857; font-size: 14px; line-height: 1.8;",
    },
    "amber-note": {
        "root": "max-width: 680px; margin: 0 auto; padding: 18px; border: 1px solid #fde68a; border-radius: 8px; color: #422006; font-size: 16px; line-height: 1.86; background: #fffbeb;",
        "h1": "margin: 0 0 22px; padding: 16px; border-radius: 8px; background: #fef3c7; color: #78350f; font-size: 27px; line-height: 1.35; font-weight: 800;",
        "h2": "margin: 32px 0 14px; padding-bottom: 8px; border-bottom: 2px solid #fbbf24; color: #92400e; font-size: 22px; line-height: 1.45; font-weight: 700;",
        "h3": "margin: 24px 0 10px; color: #b45309; font-size: 18px; line-height: 1.55; font-weight: 700;",
        "p": "margin: 0 0 17px; color: #3f2d16; font-size: 16px; line-height: 1.86;",
        "blockquote": "margin: 22px 0; padding: 14px 16px; border-left: 4px solid #f59e0b; background: #ffffff; color: #78350f; font-size: 15px; line-height: 1.82;",
        "ul": "margin: 0 0 17px; padding-left: 24px; color: #3f2d16; font-size: 16px; line-height: 1.82;",
        "ol": "margin: 0 0 17px; padding-left: 24px; color: #3f2d16; font-size: 16px; line-height: 1.82;",
        "li": "margin: 6px 0;",
        "pre": "margin: 20px 0; padding: 15px 16px; overflow-x: auto; border-radius: 8px; background: #451a03; color: #fde68a; font-size: 14px; line-height: 1.72;",
        "code": "padding: 2px 5px; border-radius: 4px; background: #fef3c7; color: #92400e; font-size: 0.92em;",
        "img": "display: block; max-width: 100%; height: auto; margin: 22px auto 8px; border-radius: 8px;",
        "caption": "margin: 0 0 22px; color: #92400e; font-size: 13px; line-height: 1.7; text-align: center;",
        "hr": "margin: 30px 0; border: 0; border-top: 1px dashed #f59e0b;",
        "strong": "font-weight: 800; color: #92400e;",
        "a": "color: #b45309; text-decoration: underline;",
        "footer": "margin-top: 32px; padding: 14px 16px; border: 1px solid #fde68a; border-radius: 8px; background: #ffffff; color: #92400e; font-size: 14px; line-height: 1.8;",
    },
    "bauhaus": {
        "root": "max-width: 680px; margin: 0 auto; color: #111827; font-size: 16px; line-height: 1.8; background: #ffffff;",
        "h1": "margin: 0 0 22px; padding: 16px; border: 4px solid #111827; background: #facc15; color: #111827; font-size: 29px; line-height: 1.25; font-weight: 900;",
        "h2": "margin: 32px 0 14px; padding: 10px 12px; border-left: 8px solid #dc2626; background: #f3f4f6; color: #111827; font-size: 22px; line-height: 1.4; font-weight: 800;",
        "h3": "margin: 24px 0 10px; padding-left: 10px; border-left: 8px solid #2563eb; color: #111827; font-size: 18px; line-height: 1.5; font-weight: 800;",
        "p": "margin: 0 0 17px; color: #1f2937; font-size: 16px; line-height: 1.8;",
        "blockquote": "margin: 22px 0; padding: 14px 16px; border: 3px solid #111827; background: #fee2e2; color: #111827; font-size: 15px; line-height: 1.78;",
        "ul": "margin: 0 0 17px; padding-left: 24px; color: #1f2937; font-size: 16px; line-height: 1.78;",
        "ol": "margin: 0 0 17px; padding-left: 24px; color: #1f2937; font-size: 16px; line-height: 1.78;",
        "li": "margin: 6px 0;",
        "pre": "margin: 20px 0; padding: 15px 16px; overflow-x: auto; border: 3px solid #111827; background: #111827; color: #facc15; font-size: 14px; line-height: 1.7;",
        "code": "padding: 2px 5px; border: 1px solid #111827; background: #facc15; color: #111827; font-size: 0.92em;",
        "img": "display: block; max-width: 100%; height: auto; margin: 22px auto 8px; border: 3px solid #111827;",
        "caption": "margin: 0 0 22px; color: #4b5563; font-size: 13px; line-height: 1.65; text-align: center;",
        "hr": "margin: 30px 0; border: 0; border-top: 6px solid #111827;",
        "strong": "font-weight: 900; color: #dc2626;",
        "a": "color: #2563eb; text-decoration: underline;",
        "footer": "margin-top: 32px; padding: 14px 16px; border: 3px solid #111827; background: #dbeafe; color: #111827; font-size: 14px; line-height: 1.75;",
    },
    "timeline": {
        "root": "max-width: 680px; margin: 0 auto; color: #172033; font-size: 16px; line-height: 1.86; background: #ffffff;",
        "h1": "margin: 0 0 24px; padding: 0 0 12px 16px; border-left: 5px solid #7c3aed; border-bottom: 1px solid #ddd6fe; color: #2e1065; font-size: 27px; line-height: 1.35; font-weight: 800;",
        "h2": "margin: 34px 0 14px; padding: 10px 0 10px 14px; border-left: 5px solid #8b5cf6; background: #f5f3ff; color: #4c1d95; font-size: 22px; line-height: 1.45; font-weight: 700;",
        "h3": "margin: 24px 0 10px; padding-left: 12px; border-left: 4px solid #c4b5fd; color: #5b21b6; font-size: 18px; line-height: 1.55; font-weight: 700;",
        "p": "margin: 0 0 17px; color: #334155; font-size: 16px; line-height: 1.86;",
        "blockquote": "margin: 22px 0; padding: 14px 16px; border-left: 4px solid #8b5cf6; background: #f5f3ff; color: #4c1d95; font-size: 15px; line-height: 1.82;",
        "ul": "margin: 0 0 17px; padding-left: 24px; color: #334155; font-size: 16px; line-height: 1.82;",
        "ol": "margin: 0 0 17px; padding-left: 24px; color: #334155; font-size: 16px; line-height: 1.82;",
        "li": "margin: 6px 0;",
        "pre": "margin: 20px 0; padding: 15px 16px; overflow-x: auto; border-radius: 6px; background: #2e1065; color: #ede9fe; font-size: 14px; line-height: 1.72;",
        "code": "padding: 2px 5px; border-radius: 4px; background: #ede9fe; color: #5b21b6; font-size: 0.92em;",
        "img": "display: block; max-width: 100%; height: auto; margin: 22px auto 8px; border-radius: 6px;",
        "caption": "margin: 0 0 22px; color: #64748b; font-size: 13px; line-height: 1.7; text-align: center;",
        "hr": "margin: 30px 0; border: 0; border-top: 1px solid #ddd6fe;",
        "strong": "font-weight: 800; color: #5b21b6;",
        "a": "color: #7c3aed; text-decoration: underline;",
        "footer": "margin-top: 32px; padding: 14px 16px; border-left: 5px solid #8b5cf6; background: #f5f3ff; color: #64748b; font-size: 14px; line-height: 1.8;",
    },
    "dialogue": {
        "root": "max-width: 680px; margin: 0 auto; color: #1f2937; font-size: 16px; line-height: 1.88; background: #ffffff;",
        "h1": "margin: 0 0 24px; padding: 14px 16px; border-radius: 8px; background: #eef2ff; color: #312e81; font-size: 27px; line-height: 1.35; font-weight: 800;",
        "h2": "margin: 34px 0 14px; color: #4338ca; font-size: 22px; line-height: 1.45; font-weight: 700;",
        "h3": "margin: 24px 0 10px; color: #6366f1; font-size: 18px; line-height: 1.55; font-weight: 700;",
        "p": "margin: 0 0 17px; padding: 0; color: #374151; font-size: 16px; line-height: 1.88;",
        "blockquote": "margin: 22px 0; padding: 14px 16px; border-radius: 8px; border-left: 4px solid #6366f1; background: #eef2ff; color: #312e81; font-size: 15px; line-height: 1.84;",
        "ul": "margin: 0 0 17px; padding-left: 24px; color: #374151; font-size: 16px; line-height: 1.82;",
        "ol": "margin: 0 0 17px; padding-left: 24px; color: #374151; font-size: 16px; line-height: 1.82;",
        "li": "margin: 6px 0;",
        "pre": "margin: 20px 0; padding: 15px 16px; overflow-x: auto; border-radius: 8px; background: #312e81; color: #e0e7ff; font-size: 14px; line-height: 1.72;",
        "code": "padding: 2px 5px; border-radius: 4px; background: #e0e7ff; color: #4338ca; font-size: 0.92em;",
        "img": "display: block; max-width: 100%; height: auto; margin: 22px auto 8px; border-radius: 8px;",
        "caption": "margin: 0 0 22px; color: #6b7280; font-size: 13px; line-height: 1.7; text-align: center;",
        "hr": "margin: 30px 0; border: 0; border-top: 1px solid #c7d2fe;",
        "strong": "font-weight: 800; color: #4338ca;",
        "a": "color: #4338ca; text-decoration: underline;",
        "footer": "margin-top: 32px; padding: 14px 16px; border-radius: 8px; background: #f5f3ff; color: #6366f1; font-size: 14px; line-height: 1.8;",
    },
}


@dataclass
class Block:
    kind: str
    text: str = ""
    level: int = 0
    ordered: bool = False
    items: list[str] | None = None
    alt: str = ""
    src: str = ""


def parse_markdown(markdown: str) -> list[Block]:
    markdown = re.sub(r"<!--[\s\S]*?-->", "", markdown)
    lines = markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    blocks: list[Block] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    list_ordered = False
    quote: list[str] = []
    in_code = False
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            blocks.append(Block("paragraph", " ".join(line.strip() for line in paragraph)))
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items, list_ordered
        if list_items:
            blocks.append(Block("list", ordered=list_ordered, items=list_items))
            list_items = []
            list_ordered = False

    def flush_quote() -> None:
        nonlocal quote
        if quote:
            blocks.append(Block("quote", "\n".join(quote).strip()))
            quote = []

    def flush_open_blocks() -> None:
        flush_paragraph()
        flush_list()
        flush_quote()

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code:
                blocks.append(Block("code", "\n".join(code_lines)))
                code_lines = []
                in_code = False
            else:
                flush_open_blocks()
                in_code = True
                code_lines = []
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not stripped:
            flush_open_blocks()
            continue

        if re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", stripped):
            flush_open_blocks()
            blocks.append(Block("hr"))
            continue

        heading = re.match(r"^(#{1,3})\s+(.+)$", stripped)
        if heading:
            flush_open_blocks()
            blocks.append(Block("heading", heading.group(2).strip(), level=len(heading.group(1))))
            continue

        image = re.match(r"^!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)$", stripped)
        if image:
            flush_open_blocks()
            blocks.append(Block("image", alt=image.group(1).strip(), src=image.group(2).strip()))
            continue

        unordered = re.match(r"^[-*+]\s+(.+)$", stripped)
        ordered = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if unordered or ordered:
            flush_paragraph()
            flush_quote()
            current_ordered = bool(ordered)
            item = (ordered or unordered).group(1).strip()
            if list_items and list_ordered != current_ordered:
                flush_list()
            list_ordered = current_ordered
            list_items.append(item)
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            flush_list()
            quote.append(stripped.lstrip(">").strip())
            continue

        flush_list()
        flush_quote()
        paragraph.append(stripped)

    if in_code:
        blocks.append(Block("code", "\n".join(code_lines)))
    flush_open_blocks()
    return blocks


def protect_code_spans(text: str) -> tuple[str, list[str]]:
    code_spans: list[str] = []

    def replace(match: re.Match[str]) -> str:
        code_spans.append(html.escape(match.group(1), quote=False))
        return f"\u0000CODE{len(code_spans) - 1}\u0000"

    return re.sub(r"`([^`]+)`", replace, text), code_spans


def render_inline(text: str, theme: dict[str, str]) -> str:
    protected, code_spans = protect_code_spans(text)
    escaped = html.escape(protected, quote=False)

    def link_repl(match: re.Match[str]) -> str:
        label = match.group(1)
        url = html.escape(match.group(2), quote=True)
        return f'<a href="{url}" style="{theme["a"]}">{label}</a>'

    escaped = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", link_repl, escaped)
    escaped = re.sub(
        r"\*\*([^*]+)\*\*",
        lambda match: f'<strong style="{theme["strong"]}">{match.group(1)}</strong>',
        escaped,
    )
    escaped = re.sub(
        r"__([^_]+)__",
        lambda match: f'<strong style="{theme["strong"]}">{match.group(1)}</strong>',
        escaped,
    )

    for index, code in enumerate(code_spans):
        escaped = escaped.replace(
            html.escape(f"\u0000CODE{index}\u0000", quote=False),
            f'<code style="{theme["code"]}">{code}</code>',
        )
    return escaped


def render_blocks(blocks: Iterable[Block], theme_name: str) -> str:
    theme = THEMES[theme_name]
    rendered: list[str] = [f'<section style="{theme["root"]}">']

    for block in blocks:
        if block.kind == "heading":
            tag = f"h{block.level}"
            rendered.append(f'<section style="{theme[tag]}">{render_inline(block.text, theme)}</section>')
        elif block.kind == "paragraph":
            rendered.append(f'<p style="{theme["p"]}">{render_inline(block.text, theme)}</p>')
        elif block.kind == "quote":
            parts = [render_inline(part, theme) for part in block.text.split("\n") if part.strip()]
            rendered.append(f'<section style="{theme["blockquote"]}">' + "<br>".join(parts) + "</section>")
        elif block.kind == "list":
            for index, item in enumerate(block.items or [], start=1):
                marker = f"{index}. " if block.ordered else "• "
                rendered.append(
                    f'<p style="{theme["p"]}"><span style="{theme["strong"]}">{marker}</span>{render_inline(item, theme)}</p>'
                )
        elif block.kind == "code":
            code = html.escape(block.text, quote=False)
            rendered.append(f'<pre style="{theme["pre"]}"><code>{code}</code></pre>')
        elif block.kind == "image":
            alt = html.escape(block.alt, quote=True)
            src = html.escape(block.src, quote=True)
            rendered.append(f'<p style="margin: 0;"><img src="{src}" alt="{alt}" style="{theme["img"]}"></p>')
            if block.alt:
                rendered.append(f'<p style="{theme["caption"]}">{render_inline(block.alt, theme)}</p>')
        elif block.kind == "hr":
            rendered.append(f'<section style="{theme["hr"]}"></section>')

    rendered.append("</section>")
    return "\n".join(rendered)


def should_add_footer(markdown: str, footer_text: str) -> bool:
    compact = re.sub(r"\s+", "", markdown)
    compact_footer = re.sub(r"\s+", "", footer_text)
    if compact_footer and compact_footer in compact:
        return False
    has_upload = "upload" in markdown.lower()
    promotional_patterns = (
        "请使用",
        "使用 Upload",
        "使用Upload",
        "了解 Upload",
        "了解Upload",
        "试试 Upload",
        "试试Upload",
    )
    if has_upload and any(pattern in markdown for pattern in promotional_patterns):
        return False
    return True


def append_footer(article_html: str, theme_name: str, footer_text: str) -> str:
    theme = THEMES[theme_name]
    footer = (
        f'<section style="{theme["footer"]}">\n'
        f'  <p style="margin: 0;">{html.escape(footer_text, quote=False)}</p>\n'
        "</section>"
    )
    before, sep, after = article_html.rpartition("\n</section>")
    if not sep:
        return f"{article_html}\n{footer}"
    return f"{before}\n{footer}{sep}{after}"


def render_article(input_path: Path, theme_name: str, footer: str, footer_text: str) -> str:
    markdown = input_path.read_text(encoding="utf-8")
    article_html = render_blocks(parse_markdown(markdown), theme_name)
    if footer == "enabled" and should_add_footer(markdown, footer_text):
        article_html = append_footer(article_html, theme_name, footer_text)
    return article_html


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Markdown into WeChat-friendly HTML.")
    parser.add_argument("--input", required=True, help="Markdown input file.")
    parser.add_argument("--theme", default="upload-clean", help="Theme name.")
    parser.add_argument("--output", required=True, help="Output directory.")
    parser.add_argument("--footer", choices=("enabled", "disabled"), default="enabled", help="Append Upload footer.")
    parser.add_argument("--footer-text", default=DEFAULT_FOOTER_TEXT, help="Custom footer copy.")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    input_suggestions = check_input_file(input_path, "Markdown 输入文件")
    if input_suggestions:
        return fail("Markdown 输入文件不存在。", input_suggestions)

    if args.theme not in SUPPORTED_THEMES:
        message, suggestions = theme_error(args.theme, SUPPORTED_THEMES)
        return fail(message, suggestions)

    output_dir = Path(args.output).expanduser().resolve()
    ok, output_suggestions = prepare_output_dir(output_dir)
    if not ok:
        return fail("输出目录不可用。", output_suggestions)

    article_html = render_article(input_path, args.theme, args.footer, args.footer_text)
    article_path = output_dir / "article.html"
    try:
        article_path.write_text(article_html + "\n", encoding="utf-8")
    except OSError as error:
        return fail(
            "写入 article.html 失败。",
            [
                f"目标路径：{article_path}",
                f"系统返回：{error}",
                "请确认输出目录可写，或改用 --output /tmp/wechat-output。",
            ],
        )
    print(f"PASS render article={article_path} theme={args.theme} footer={args.footer}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
