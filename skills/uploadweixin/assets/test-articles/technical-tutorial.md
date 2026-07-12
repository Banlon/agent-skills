# 用 Codex Skill 做一条稳定的公众号排版链路

这是一篇技术教程，用来验证 uploadweixin 的标题、正文、引用、代码块、列表、分割线、图片说明和 footer。

![Markdown 到公众号 HTML 的渲染流程示意](https://upload.one/assets/uploadweixin-flow.png)

## 准备输入文件

先把文章写成 Markdown。为了降低复制到公众号后台时的风险，最终输出必须是 inline style 的 HTML。

> 判断一条排版链路是否稳定，不看它在浏览器里多花哨，而看它粘贴到公众号编辑器之后是否还能保持结构。

### 最小命令

```bash
python3 scripts/render_wechat_article.py \
  --input article.md \
  --theme upload-clean \
  --output /tmp/wechat-output
```

## 核心检查项

- 不出现 `<style>` 和 `<script>`。
- 不使用 onclick 或任何事件属性。
- 不使用 display:flex、grid、position、animation、transform。
- 保留代码块、列表和引用的阅读层次。

## Python 示例

```python
def validate_theme(theme_name: str) -> str:
    if not theme_name:
        raise ValueError("missing theme")
    return f"{theme_name}: PASS"
```

---

完成渲染后，再运行 validator，并打开 preview.html 做肉眼检查。
