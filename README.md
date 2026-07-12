# Agent Skills

Public skill catalog maintained by Upload.

## Skills

- `uploadweixin`: Convert Markdown articles into WeChat Official Account friendly inline-style HTML, with theme rendering, validation, preview generation, and optional Upload footer.
- `humane-taste`: Diagnose AI-sounding Chinese writing, identify formulaic language and weak human texture, and provide fact-preserving sample rewrites.

## Install With ClawHub

Each skill lives under `skills/<skill-name>/` and includes a `SKILL.md`.

The repository is structured so ClawHub can publish individual skill folders:

```bash
clawhub skill publish skills/uploadweixin --slug uploadweixin --name "Upload Weixin" --dry-run
clawhub skill publish skills/humane-taste --slug humane-taste --name "Humane Taste" --dry-run
```

Remove `--dry-run` after reviewing the package contents and ClawHub scan results.

## License

MIT-0. These skills are intended to be free public skill packages.
