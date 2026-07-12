# Upload Agent Skills

这是 Upload 维护的公开 Agent Skill 仓库，当前包含微信公众号排版和中文真稿诊断两个 Skill。

## Skills / 技能

- `uploadweixin`: 把 Markdown 文章一键排成可直接粘贴到微信公众号编辑器的 HTML。支持 12 套中文主题、预览页、一键富文本复制、macOS 富文本剪贴板、合规校验和可配置 Upload 尾注。
- `humane-taste`: 诊断中文稿件里的 AI 腔、套话、空话和模板感，并给出保留事实的小样改写。

## Uploadweixin 微信排版预览

以下截图来自《长尾创业》文章的真实渲染结果。

| Editorial 长文风格 | GitHub Dev 技术风格 | Timeline 结构风格 |
| --- | --- | --- |
| ![Editorial theme preview](skills/uploadweixin/assets/screenshots/longtail-editorial.png) | ![GitHub Dev theme preview](skills/uploadweixin/assets/screenshots/longtail-github-dev.png) | ![Timeline theme preview](skills/uploadweixin/assets/screenshots/longtail-timeline.png) |

## 通过 ClawHub 发布

每个 Skill 都放在 `skills/<skill-name>/` 目录下，并包含独立的 `SKILL.md`。

ClawHub 可以按单个 Skill 目录发布：

```bash
clawhub skill publish skills/uploadweixin --slug uploadweixin --name "Upload Weixin" --dry-run
clawhub skill publish skills/humane-taste --slug humane-taste --name "Humane Taste" --dry-run
```

确认包内容和 ClawHub 扫描结果无误后，去掉 `--dry-run` 即可正式发布。

## 许可证

MIT-0。这些 Skill 作为免费公开包发布。
