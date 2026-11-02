#!/usr/bin/env python3
"""Builds the blog from content/ into public/.

    python build.py          build the site
    python build.py serve    build, serve on http://127.0.0.1:8000 and rebuild on changes
"""

import hashlib
import json
import os
import re
import shutil
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from email.utils import format_datetime
from functools import partial
from html import escape, unescape
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import markdown
import yaml

import heatmaps

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
ASSETS = ROOT / "assets"
STATIC = ROOT / "static"
OUT = ROOT / "public"

SITE = {
    "url": "https://shahar.blog",
    "title": "Shahar Glazner",
    "author": "Shahar Glazner",
    "description": "Thoughts and writings by Shahar Glazner on software, open source and building things.",
    "image": "/avatar.jpg",
    "github": "shahargl",
    "x": "shaharglazner",
    "linkedin": "https://www.linkedin.com/in/shahar-glazner-29294654/",
    "source": "https://github.com/shahargl/blog",
    "timezone": "Asia/Jerusalem",
    "per_page": 10,
    "feed_limit": 20,
    "nav": [("blog", "/"), ("about", "/about/")],
    "home_aliases": ["/en/", "/he/", "/posts/", "/en/posts/", "/he/posts/", "/page/1/"],
    "giscus": {
        "repo": "shahargl/blog",
        "repo-id": "R_kgDOPDwrew",
        "category": "Announcements",
        "category-id": "DIC_kwDOPDwre84CsM_C",
    },
}

HEATMAPS_MARKER = "<!-- heatmaps -->"

FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.S)

MD = markdown.Markdown(
    extensions=["fenced_code", "codehilite", "tables", "toc", "smarty", "footnotes", "sane_lists"],
    extension_configs={"codehilite": {"guess_lang": False, "css_class": "highlight"}},
)


@dataclass
class Page:
    source: Path
    kind: str
    slug: str
    title: str
    body: str
    html: str
    url: str
    date: datetime | None = None
    description: str = ""
    tags: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    rtl: bool = False
    comments: bool = True

    @property
    def summary(self):
        if self.description:
            return f"<p>{escape(self.description)}</p>"
        match = re.search(r"<p>.*?</p>", self.html, re.S)
        return match[0] if match else ""

    @property
    def markdown_url(self):
        return f"{self.url}index.md"


def abs_url(path):
    return SITE["url"] + path


def plain(text, limit=200):
    text = unescape(re.sub(r"<[^>]+>", "", text))
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rsplit(" ", 1)[0] + "…"


def slugify(value):
    return re.sub(r"[^\w-]+", "-", value.strip().lower()).strip("-")


def parse_date(value):
    if isinstance(value, datetime):
        result = value
    elif isinstance(value, date):
        result = datetime(value.year, value.month, value.day)
    else:
        result = datetime.fromisoformat(str(value))
    return result if result.tzinfo else result.replace(tzinfo=timezone.utc)


def long_date(d, weekday=False):
    text = f"{d:%B} {d.day}, {d.year}"
    return f"{d:%A}, {text}" if weekday else text


def render_markdown(text):
    MD.reset()
    return MD.convert(text)


def read_page(path, kind):
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER.match(text)
    meta, body = (yaml.safe_load(match[1]) or {}, match[2]) if match else ({}, text)
    if meta.get("draft"):
        return None

    slug = meta.get("slug") or path.stem
    page_date = parse_date(meta["date"]) if "date" in meta else None
    if kind == "post":
        if page_date is None:
            raise ValueError(f"{path}: posts need a date")
        url = f"/{page_date:%Y/%m/%d}/{slug}/"
    else:
        url = f"/{slug}/"

    return Page(
        source=path,
        kind=kind,
        slug=slug,
        title=meta.get("title", slug),
        body=body.strip(),
        html=render_markdown(body),
        url=url,
        date=page_date,
        description=meta.get("description", ""),
        tags=[str(tag) for tag in meta.get("tags", [])],
        aliases=meta.get("aliases", []),
        rtl=bool(meta.get("rtl")),
        comments=not meta.get("disable_comments", False),
    )


def load_content():
    posts = [read_page(path, "post") for path in sorted((CONTENT / "posts").glob("*.md"))]
    pages = [read_page(path, "page") for path in sorted(CONTENT.glob("*.md"))]
    posts = sorted(filter(None, posts), key=lambda post: post.date, reverse=True)
    return posts, list(filter(None, pages))


# Templates


def direction(page):
    return ' lang="he" dir="rtl"' if page and page.rtl else ""


def header(current):
    def link(name, url):
        marker = ' aria-current="page"' if name == current else ""
        return f'<li><a href="{url}"{marker}>{name}</a></li>'

    links = "".join(link(name, url) for name, url in SITE["nav"])
    return (
        '<header class="site-header">'
        f'<a class="site-title" href="/">{escape(SITE["title"])}</a>'
        f'<nav class="site-nav" aria-label="Main"><ul>{links}</ul></nav>'
        "</header>"
    )


def footer(page):
    actions = ""
    if page:
        actions = (
            '<p class="page-actions">'
            f'<button type="button" class="link" data-copy-markdown="{page.markdown_url}">copy as</button> / '
            f'<a href="{page.markdown_url}">view markdown</a></p>'
        )
    return (
        f'<footer class="site-footer">{actions}'
        f"<p>&copy; Copyright {datetime.now().year} by {escape(SITE['author'])}.</p>"
        "<p>Contact me via "
        f'<a href="https://x.com/{SITE["x"]}">x</a>, '
        f'<a href="https://github.com/{SITE["github"]}">github</a> or '
        f'<a href="{SITE["linkedin"]}">linkedin</a>. '
        'Subscribe via <a href="/feed.xml">rss</a>. '
        f'Source on <a href="{SITE["source"]}">github</a>.</p>'
        '<p class="theme-switch">Color scheme: '
        '<button type="button" class="link" data-theme-choice="auto">auto</button>, '
        '<button type="button" class="link" data-theme-choice="light">light</button>, '
        '<button type="button" class="link" data-theme-choice="dark">dark</button>.</p>'
        "</footer>"
    )


def layout(body, *, url, assets, title=None, description=None, current="blog", page=None):
    full_title = f"{title} | {SITE['title']}" if title else SITE["title"]
    description = escape(plain(description or SITE["description"]))
    is_post = page is not None and page.kind == "post"
    extra_head = ""
    if page:
        extra_head += f'<link rel="alternate" type="text/markdown" title="Markdown" href="{page.markdown_url}">'
    if is_post:
        extra_head += f'<meta property="article:published_time" content="{page.date.isoformat()}">'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(full_title)}</title>
<meta name="description" content="{description}">
<meta name="author" content="{escape(SITE['author'])}">
<link rel="canonical" href="{abs_url(url)}">
<meta property="og:title" content="{escape(title or SITE['title'])}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{abs_url(url)}">
<meta property="og:site_name" content="{escape(SITE['title'])}">
<meta property="og:type" content="{'article' if is_post else 'website'}">
<meta property="og:image" content="{abs_url(SITE['image'])}">
<meta name="twitter:card" content="summary">
<meta name="twitter:creator" content="@{SITE['x']}">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="{escape(SITE['title'])}" href="/feed.xml">
{extra_head}
<script>(function(){{var t=localStorage.getItem("theme");if(t==="light"||t==="dark")document.documentElement.dataset.theme=t;}})();</script>
<link rel="stylesheet" href="{assets['css']}">
<script src="{assets['js']}" defer></script>
</head>
<body>
<div class="page">
{header(current)}
<main id="content">
{body}
</main>
{footer(page)}
</div>
</body>
</html>
"""


def entry(post):
    return f"""<li class="entry"{direction(post)}>
<h2 class="entry-title"><a href="{post.url}">{escape(post.title)}</a></h2>
<p class="meta">written on <time datetime="{post.date:%Y-%m-%d}">{long_date(post.date)}</time></p>
<div class="summary">{post.summary}</div>
<p class="more"><a href="{post.url}">continue reading &rarr;</a></p>
</li>"""


def pagination(number, total):
    if total <= 1:
        return ""
    def page_url(n):
        return "/" if n == 1 else f"/page/{n}/"
    newer = f'<a href="{page_url(number - 1)}" rel="prev">&larr; newer</a>' if number > 1 else "<span></span>"
    older = f'<a href="{page_url(number + 1)}" rel="next">older &rarr;</a>' if number < total else "<span></span>"
    return (
        f'<nav class="pagination" aria-label="Pagination">{newer}'
        f'<span class="meta">page {number} of {total}</span>{older}</nav>'
    )


def comments(page):
    term = f"posts/{page.slug}/"
    attrs = {
        **SITE["giscus"],
        "mapping": "specific",
        "term": term,
        "strict": "1",
        "reactions-enabled": "1",
        "emit-metadata": "0",
        "input-position": "bottom",
        "lang": "en",
        "loading": "lazy",
    }
    data = " ".join(f'data-{key}="{escape(value)}"' for key, value in attrs.items())
    return (
        f'<section class="comments" id="comments" {data}>'
        '<noscript><p class="meta">Comments require JavaScript.</p></noscript></section>'
    )


def article(page):
    meta = ""
    tags = ""
    if page.kind == "post":
        meta = (
            f'<p class="meta">written on <time datetime="{page.date:%Y-%m-%d}">'
            f"{long_date(page.date, weekday=True)}</time></p>"
        )
        if page.tags:
            links = ", ".join(f'<a href="/tags/{slugify(tag)}/">{escape(tag)}</a>' for tag in page.tags)
            tags = f'<p class="meta tags">This entry was tagged {links}</p>'
    body = (
        f'<article class="article"{direction(page)}>'
        f"<h1>{escape(page.title)}</h1>{meta}"
        f'<div class="prose">{page.html}</div>{tags}</article>'
    )
    if page.kind == "post" and page.comments:
        body += comments(page)
    return body


def archive_list(posts):
    items = "".join(
        f'<li><time class="meta" datetime="{post.date:%Y-%m-%d}">{post.date:%b} {post.date.day}, {post.date.year}</time>'
        f'<a href="{post.url}">{escape(post.title)}</a></li>'
        for post in posts
    )
    return f'<ul class="archive">{items}</ul>'


def redirect(target):
    return (
        f'<!doctype html><html lang="en"><head><title>{abs_url(target)}</title>'
        f'<link rel="canonical" href="{abs_url(target)}"><meta name="robots" content="noindex">'
        f'<meta charset="utf-8"><meta http-equiv="refresh" content="0; url={target}"></head></html>'
    )


def page_markdown(page):
    lines = ["---", f"title: {json.dumps(page.title, ensure_ascii=False)}"]
    if page.date:
        lines.append(f"date: {page.date:%Y-%m-%d}")
    if page.tags:
        lines.append(f"tags: {json.dumps(page.tags, ensure_ascii=False)}")
    lines += [f"url: {abs_url(page.url)}", "---", "", f"# {page.title}", "", page.body, ""]
    return "\n".join(lines)


def feed(posts):
    items = "".join(
        f"<item><title>{escape(post.title)}</title><link>{abs_url(post.url)}</link>"
        f"<guid>{abs_url(post.url)}</guid><pubDate>{format_datetime(post.date)}</pubDate>"
        f"<description>{escape(post.html)}</description></item>"
        for post in posts[: SITE["feed_limit"]]
    )
    updated = f"<lastBuildDate>{format_datetime(posts[0].date)}</lastBuildDate>" if posts else ""
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
        f"<title>{escape(SITE['title'])}</title><link>{abs_url('/')}</link>"
        f"<description>{escape(SITE['description'])}</description><language>en-us</language>{updated}"
        f'<atom:link href="{abs_url("/feed.xml")}" rel="self" type="application/rss+xml"/>'
        f"{items}</channel></rss>"
    )


def sitemap(urls):
    entries = "".join(f"<url><loc>{abs_url(url)}</loc></url>" for url in urls)
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{entries}</urlset>'
    )


# Build


def write(path, content):
    target = OUT / path.lstrip("/")
    if path.endswith("/"):
        target = target / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        target.write_bytes(content)
    else:
        target.write_text(content, encoding="utf-8")


def fingerprint(relative):
    data = (ASSETS / relative).read_bytes()
    digest = hashlib.sha256(data).hexdigest()[:10]
    path = Path(relative)
    url = f"/{path.parent.as_posix()}/{path.stem}.{digest}{path.suffix}"
    write(url, data)
    return url


def load_env():
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        key, sep, value = line.strip().partition("=")
        if sep and not key.startswith("#"):
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def build():
    posts, pages = load_content()
    if any(HEATMAPS_MARKER in page.html for page in posts + pages):
        section = heatmaps.render(heatmaps.load(SITE["github"], SITE["timezone"]), SITE["github"])
        for page in posts + pages:
            page.html = page.html.replace(HEATMAPS_MARKER, section)
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(STATIC, OUT)
    assets = {"css": fingerprint("css/main.css"), "js": fingerprint("js/main.js")}
    urls = []

    per_page = SITE["per_page"]
    chunks = [posts[i : i + per_page] for i in range(0, len(posts), per_page)] or [[]]
    for number, chunk in enumerate(chunks, start=1):
        url = "/" if number == 1 else f"/page/{number}/"
        items = "".join(entry(post) for post in chunk)
        body = f'<ol class="entries">{items}</ol>' if items else '<p class="empty">Nothing here yet.</p>'
        write(url, layout(body + pagination(number, len(chunks)), url=url, assets=assets))
        urls.append(url)
    for alias in SITE["home_aliases"]:
        write(alias, redirect("/"))

    for page in posts + pages:
        current = "blog" if page.kind == "post" else page.slug
        description = page.description or page.summary
        write(page.url, layout(article(page), url=page.url, assets=assets, title=page.title,
                               description=description, current=current, page=page))
        write(page.markdown_url, page_markdown(page))
        for alias in page.aliases:
            write(alias, redirect(page.url))
        urls.append(page.url)

    tags = {}
    for post in posts:
        for tag in post.tags:
            tags.setdefault(slugify(tag), (tag, []))[1].append(post)
    for slug, (name, tagged) in sorted(tags.items()):
        url = f"/tags/{slug}/"
        body = f"<h1>Entries tagged &ldquo;{escape(name)}&rdquo;</h1>{archive_list(tagged)}"
        body += '<p class="meta"><a href="/tags/">all tags</a></p>'
        write(url, layout(body, url=url, assets=assets, title=name))
        urls.append(url)
    cloud = "".join(
        f'<li><a href="/tags/{slug}/">{escape(name)}</a> <span class="meta">({len(tagged)})</span></li>'
        for slug, (name, tagged) in sorted(tags.items())
    )
    write("/tags/", layout(f'<h1>Tags</h1><ul class="tag-cloud">{cloud}</ul>', url="/tags/", assets=assets, title="Tags"))

    not_found = (
        '<article class="article"><h1>Not Found</h1><div class="prose">'
        "<p>The page you were looking for does not exist. Maybe it moved, maybe it never existed.</p>"
        '<p><a href="/">Back to the blog &rarr;</a></p></div></article>'
    )
    write("/404.html", layout(not_found, url="/404.html", assets=assets, title="Not Found", current=None))

    write("/feed.xml", feed(posts))
    write("/sitemap.xml", sitemap(urls))
    write("/robots.txt", f"User-agent: *\nSitemap: {abs_url('/sitemap.xml')}\n")
    print(f"built {len(posts)} posts and {len(pages)} pages into {OUT.relative_to(ROOT)}/")


def snapshot():
    files = [ROOT / "build.py", ROOT / "heatmaps.py", *CONTENT.rglob("*"), *ASSETS.rglob("*"), *STATIC.rglob("*")]
    return {path: path.stat().st_mtime for path in files if path.is_file()}


def serve(port=8000):
    build()

    def watch():
        last = snapshot()
        while True:
            time.sleep(0.5)
            current = snapshot()
            if current != last:
                last = current
                try:
                    build()
                except Exception as error:
                    print(f"build failed: {error}")

    threading.Thread(target=watch, daemon=True).start()
    handler = partial(SimpleHTTPRequestHandler, directory=OUT)
    print(f"serving on http://127.0.0.1:{port}/")
    ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()


if __name__ == "__main__":
    load_env()
    if sys.argv[1:2] == ["serve"]:
        serve(int(sys.argv[2]) if len(sys.argv) > 2 else 8000)
    else:
        build()
