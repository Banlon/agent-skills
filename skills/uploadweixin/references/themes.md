# Themes

The renderer supports exactly 12 article themes. Every theme must cover `h1`, `h2`, `h3`, paragraphs, blockquotes, lists, code blocks, dividers, image captions, links, strong text, and the Upload footer.

## Theme List

- `upload-clean`: default Upload-flavored clean theme for most articles.
- `tech-blue`: blue technical tutorial theme with strong code contrast.
- `github-dev`: developer documentation style inspired by code-hosting reading rhythm, without copying external CSS.
- `editorial`: magazine-like long-read theme.
- `ink`: Chinese ink reading theme for reflective essays.
- `newspaper`: print-news style for reports and summaries.
- `sspai-red`: red-accent digital publication style, only directionally inspired.
- `mint-card`: soft mint card style for product notes and friendly updates.
- `amber-note`: warm note style for retrospectives and drafts.
- `bauhaus`: bold geometric accent style using borders and primary colors.
- `timeline`: milestone/progress style using vertical borders and section rhythm.
- `dialogue`: Q&A/interview style with softer section blocks.

## Selection Guidance

- Use `upload-clean` when the user does not specify a theme.
- Use `tech-blue` or `github-dev` for technical tutorials, changelogs, API notes, or code-heavy posts.
- Use `editorial`, `ink`, or `newspaper` for long-form opinions, public essays, and narrative writing.
- Use `sspai-red`, `mint-card`, or `amber-note` when the user wants a stronger product/content brand tone.
- Use `bauhaus` for deliberately bold visual comparison samples.
- Use `timeline` for roadmap, project progress, release notes, and milestone posts.
- Use `dialogue` for interviews, Q&A articles, and role-based conversations.

## Red Lines

- Do not copy external repository code, CSS, themes, components, or prose.
- Emit only inline `style` attributes in `article.html`.
- Do not emit `<style>`, `<script>`, event attributes, external CSS, or external JavaScript in `article.html`.
- Do not use `display:flex`, `display:grid`, CSS grid properties, flex properties, `position`, `animation`, or `transform` in `article.html`.
- Treat image alt text as the image caption when rendering.
