# WeChat HTML Rules

Generate conservative HTML intended for copy-paste into the WeChat Official Account editor.

## Allowed Shape

- Prefer conservative copy-stable tags: `section`, `p`, `strong`, `code`, `pre`, `img`, `br`, and `a`.
- Render headings, quotes, dividers, and list-like items with `section` / `p` plus inline styles instead of relying on `h1`, `h2`, `h3`, `blockquote`, `ul`, `ol`, `li`, or `hr`. WeChat may strip or normalize semantic tags during paste.
- Put styling inline on each generated element.
- Escape article text before adding inline Markdown formatting.
- Keep images as normal `<img>` tags with escaped `src` and `alt`; render non-empty image alt text as a caption paragraph.
- Keep output self-contained; do not depend on external CSS or JavaScript.

## Hard Blocks

Reject or avoid:

- `<script>`, `<style>`, `<iframe>`, `<form>`, `<input>`, and `<button>`.
- Event attributes such as `onclick`, `onload`, `onerror`, or any attribute beginning with `on`.
- External CSS or JavaScript references, including stylesheet links and script URLs.
- Layout CSS that WeChat may strip or distort: `position`, `display: grid`, `display: flex`, grid properties, flex properties, `z-index`, `animation`, and `transform`.

## Style Guidance

- Use spacing, borders, color, background, font size, line height, and text alignment.
- Avoid classes and ids unless a future version needs them; v1 should not.
- Do not use CSS grid, flexbox, positioning, animations, transforms, or JavaScript-driven copy behavior in `article.html`.
- `preview.html` may use browser-only UI because it is a local preview page, not the WeChat payload.
- Do not use cross-device clipboard sync or input-method clipboard sync for final paste; they commonly strip HTML/RTF and leave plain text only. Prefer same-device rich copy or the macOS clipboard script.
