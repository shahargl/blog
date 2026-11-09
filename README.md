# shahar.blog

Source for [shahar.blog](https://shahar.blog). Markdown in, static HTML out,
built by a single script (`build.py`) and deployed to GitHub Pages.

## Usage

```bash
make serve                      # http://127.0.0.1:8000, rebuilds on save
make build                      # writes the site to public/
make post title="My new post"   # creates content/posts/my-new-post.md as a draft
```

Requires Python 3.10+. `make` creates a `.venv` with the dependencies from
`requirements.txt` on first run.

## Layout

- `content/posts/*.md` are blog posts, published at `/YYYY/MM/DD/<file-name>/`
- `content/*.md` are standalone pages such as `/about/`
- `assets/` holds the stylesheet and script, fingerprinted on build
- `static/` is copied into the site as-is
- Site settings (title, links, comments) live in `SITE` at the top of `build.py`

## Front matter

```yaml
---
title: "Post title"
date: 2026-11-01T12:00:00+02:00
description: "Shown on the blog index and in link previews"
image: /images/post.jpg  # link preview image from static/, defaults to the avatar
tags: ["python", "open-source"]
draft: true              # skipped by the build
rtl: true                # right-to-left layout for Hebrew posts
aliases: [/old/url/]     # old URLs that redirect here
disable_comments: true
---
```

Every page is also published as Markdown at `<url>/index.md`. Comments use
[giscus](https://giscus.app) backed by this repository's Discussions.

## Deployment

Pushing to `main` runs `.github/workflows/deploy.yml`, which builds the site and
publishes it to GitHub Pages. The custom domain is configured in the repository's
Pages settings.
