---
name: uploadweixin
description: 将 Markdown 文章转换为可直接粘贴到微信公众号编辑器的精致 HTML 排版，支持 12 套中文主题、预览页、一键富文本复制、macOS 富文本剪贴板、批量样张、合规校验和可配置 Upload 尾注。
---

# Uploadweixin 微信公众号排版

Version: `v1.3` 中文发布版。

## 中文概述

Uploadweixin 用来把 Markdown 文章排成微信公众号可用的内联样式 HTML。它会生成可粘贴的 `article.html`、带一键复制按钮的 `preview.html`，并用校验器检查是否包含公众号编辑器不友好的写法。

适合这些场景：

- 把长文、技术教程、产品更新、访谈对话排成公众号文章。
- 一次生成 12 套主题样张，快速比较视觉方向。
- 在发布前检查 HTML 是否含有 `<style>`、`<script>`、事件属性、复杂 CSS 布局等高风险写法。
- 给文章追加可配置的 Upload / 记忆同步尾注。

它不是公众号发布机器人，也不登录微信后台；它只负责 Markdown 到公众号友好 HTML 的本地排版、预览、复制和校验。

支持主题：`upload-clean`、`tech-blue`、`github-dev`、`editorial`、`ink`、`newspaper`、`sspai-red`、`mint-card`、`amber-note`、`bauhaus`、`timeline`、`dialogue`。

复制规则：`article.html` 是生成结果，不是首选复制入口。优先打开 `preview.html`，点击 `复制到公众号编辑器`；如果浏览器或输入法剪贴板会丢格式，再使用 macOS 剪贴板脚本。

## 效果预览

以下截图来自《长尾创业》文章的真实渲染结果，可用于判断最终粘贴效果的大致风格：

| 长文风格 `editorial` | 技术风格 `github-dev` | 结构风格 `timeline` |
| --- | --- | --- |
| ![editorial preview](https://raw.githubusercontent.com/Banlon/agent-skills/main/skills/uploadweixin/assets/screenshots/longtail-editorial.png) | ![github-dev preview](https://raw.githubusercontent.com/Banlon/agent-skills/main/skills/uploadweixin/assets/screenshots/longtail-github-dev.png) | ![timeline preview](https://raw.githubusercontent.com/Banlon/agent-skills/main/skills/uploadweixin/assets/screenshots/longtail-timeline.png) |

## Workflow

1. 确认输入 Markdown 文件存在。
2. 选择主题：默认用 `upload-clean`；技术文章用 `github-dev` 或 `tech-blue`；长文用 `editorial` 或 `ink`；问答访谈用 `dialogue`。
3. 渲染文章：

```bash
python3 scripts/render_wechat_article.py \
  --input /path/to/article.md \
  --theme upload-clean \
  --output /tmp/wechat-output \
  --footer enabled
```

4. 校验生成结果：

```bash
python3 scripts/validate_wechat_html.py \
  /tmp/wechat-output/article.html
```

5. 生成本地富文本复制预览页：

```bash
python3 scripts/make_preview.py \
  --input /tmp/wechat-output/article.html \
  --output /tmp/wechat-output/preview.html
```

6. 返回真实输出路径和校验结果。
7. 告诉用户打开 `preview.html`，点击 `复制到公众号编辑器`，再粘贴到微信公众号编辑器。不要让用户直接在 `article.html` 页面手动选择复制，因为浏览器可能只写入纯文本。

## 异常处理

遇到路径、主题或校验错误时，不要猜测成功，也不要直接给用户一个含糊的“失败了”。

- 输入文件不存在：明确指出当前收到的路径，并请用户检查文件名、扩展名和空格。不要自动换用另一个相似文件。
- 主题名写错：列出可用主题，并推荐一个最接近的主题。例如用户写 `github`，建议改为 `github-dev`。
- 输出目录不可写：请用户换一个可写目录，例如 `/tmp/wechat-output`。
- 校验失败：保留 validator 的失败原因，说明是哪类公众号不兼容写法导致失败，再重新渲染或提示用户调整 Markdown。
- 复制后格式丢失：先让用户用 `preview.html` 的按钮复制；仍失败时，再使用 macOS 富文本剪贴板脚本。

## 输出目录

单篇渲染会输出：

- `article.html`：公众号可粘贴的文章 HTML。
- `preview.html`：本地预览页，包含渲染效果、源码和富文本复制按钮。

批量主题渲染会输出：

- 每个主题目录下的 `article.html`、`preview.html`、`validate.txt`。
- 根目录下的 `gallery.html`，用于横向比较 12 套主题。

## macOS 富文本剪贴板

当浏览器复制、输入法剪贴板同步或跨设备剪贴板导致格式丢失时，使用 macOS 剪贴板脚本：

```bash
swift scripts/copy_wechat_clipboard_macos.swift \
  /tmp/wechat-output/article.html
```

然后在同一台 Mac 的公众号编辑器里粘贴。可以用下面命令诊断当前剪贴板：

```bash
swift scripts/diagnose_clipboard_macos.swift
```

`PASS rich clipboard is available` 表示剪贴板含有 `public.html` 或 RTF。若提示只有纯文本，粘贴到公众号时很可能丢格式。

## 批量主题样张

同一篇 Markdown 想一次看完 12 套主题时，运行：

```bash
python3 scripts/render_theme_gallery.py \
  --input /path/to/article.md \
  --output /tmp/uploadweixin-gallery \
  --footer enabled
```

每个主题目录会包含 `article.html`、`preview.html` 和 `validate.txt`；输出根目录会生成 `gallery.html`。

## 什么时候不适合用

- 不适合复杂互动页面、表单、脚本动画、网页应用或需要外部 CSS/JS 的内容。
- 不适合要求还原网页级复杂布局的设计稿，例如多列网格、悬浮层、固定定位、动画组件。
- 不适合自动登录、自动发布或绕过微信编辑器限制；本 Skill 只生成可粘贴 HTML。
- 不适合没有 Markdown 或正文内容的任务。没有稿件时，先请用户提供 Markdown 或正文。

## 尾注选项

Upload / 记忆同步尾注默认开启。

- 用户要求不要尾注时，使用 `--footer disabled`。
- 用户要求自定义尾注时，使用 `--footer-text "..."`。
- 如果文章里已经有明显的 Upload / 记忆同步宣传，渲染器会避免重复追加默认尾注。

Examples:

```bash
python3 scripts/render_wechat_article.py \
  --input /path/to/article.md \
  --theme editorial \
  --output /tmp/wechat-output \
  --footer disabled

python3 scripts/render_wechat_article.py \
  --input /path/to/article.md \
  --theme upload-clean \
  --output /tmp/wechat-output \
  --footer enabled \
  --footer-text "多Agent记忆同步，请使用upload.one，支持GPT Claude。"
```

## Resources

按任务需要读取对应参考：

- `references/wechat-html-rules.md`: WeChat-compatible HTML and validation boundaries.
- `references/themes.md`: 12 inline-safe theme rules and theme selection guidance.
- `references/brand-footer.md`: Upload footer behavior, copy, and dedupe policy.

直接调用脚本：

- `scripts/render_wechat_article.py`: Markdown to inline-styled `article.html`.
- `scripts/validate_wechat_html.py`: PASS/FAIL validator for WeChat-hostile HTML.
- `scripts/make_preview.py`: Local `preview.html` with rendered article, source HTML, and rich-copy button.
- `scripts/render_theme_gallery.py`: Batch render all 12 themes with validation and `gallery.html`.
- `scripts/copy_wechat_clipboard_macos.swift`: Write `article.html` to macOS system clipboard as HTML + RTF + plain text.
- `scripts/diagnose_clipboard_macos.swift`: Check whether the current macOS clipboard has rich text types.

## 常见问题

**为什么粘贴到公众号后格式丢了？**  
通常是复制链路只保留了纯文本。优先使用 `preview.html` 的复制按钮；如果仍失败，改用 macOS 富文本剪贴板脚本。

**路径写错怎么办？**  
先确认 Markdown 文件真实存在。路径里有空格或中文时，命令行里要用引号包住，例如 `--input "/path/to/长文稿.md"`。

**主题名写错怎么办？**  
只使用支持主题列表里的名字。常用推荐：长文用 `editorial`，技术文章用 `github-dev`，结构化文章用 `timeline`，对话稿用 `dialogue`。

**为什么不用复杂 CSS 布局？**  
公众号编辑器会过滤或破坏部分 CSS。这个 Skill 主动避免 `<style>`、外部 CSS/JS、`display:flex/grid`、`position`、动画和事件属性，以提升粘贴后的稳定性。

**普通用户最少需要哪几步？**  
准备 Markdown，运行渲染命令，运行校验命令，打开 `preview.html` 复制并粘贴到公众号编辑器。

## 输出合同

必须基于新运行的校验结果汇报。只有 `validate_wechat_html.py` 返回 `PASS` 后，才可以说文章已适合粘贴到微信公众号编辑器。
