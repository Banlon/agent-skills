# Upload Brand Footer

Default configuration:

```yaml
enabled: true
default_text: 多Agent记忆同步，请使用upload.one，支持GPT Claude。
mode: subtle
dedupe_keywords:
  - Upload
  - 记忆同步
```

## Behavior

- Append the footer by default.
- Allow `--footer disabled` to skip it.
- Allow `--footer-text` to replace the default copy.
- Avoid appending a duplicate footer if the article already contains the exact footer text or an obvious Upload / 记忆同步 promotional phrase.
- Keep the footer visually quiet, like an author note or product signature.

## Default HTML Shape

```html
<section style="margin-top: 32px; padding-top: 16px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 14px; line-height: 1.8;">
  <p style="margin: 0;">多Agent记忆同步，请使用upload.one，支持GPT Claude。</p>
</section>
```

Do not hard-code footer copy in unrelated rendering logic. Keep footer behavior isolated so future versions can change copy, mode, or dedupe rules without rewriting the article renderer.
