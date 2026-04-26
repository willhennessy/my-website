#!/usr/bin/env python3
"""
Build static HTML for willhennessy.io.

Reads markdown source from `posts/`, renders each into `writing/<slug>.html`
using `templates/post.html`, and regenerates the writing list in `index.html`
from `templates/index.html`.

Usage:  python3 build.py

Frontmatter keys (all optional except title, slug, date):
    title         e.g. "The *shape* of a good PRD"   (markdown allowed)
    slug          e.g. "the-shape-of-a-good-prd"
    date          YYYY-MM-DD (publish date)
    updated       YYYY-MM-DD (optional)
    read_time     "6 min read"  (auto-estimated if omitted)
    category      "Product"
    description   plain-text meta description (used for SEO)
    lede          one-paragraph subhead under the title (markdown allowed)
    tags          comma-separated, e.g. "PRD, Product, Strategy"

Dependency:  pip3 install markdown
"""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.stderr.write(
        "Missing dependency: install with `pip3 install --user markdown`\n"
    )
    sys.exit(1)


ROOT = Path(__file__).resolve().parent
POSTS_DIR = ROOT / "posts"
WRITING_DIR = ROOT / "writing"
TEMPLATES_DIR = ROOT / "templates"

POST_TEMPLATE = (TEMPLATES_DIR / "post.html").read_text()
INDEX_TEMPLATE = (TEMPLATES_DIR / "index.html").read_text()


# ──────────────────────────────────────────────────────────────────────────────
# Frontmatter parsing
# ──────────────────────────────────────────────────────────────────────────────

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse simple `key: value` YAML-ish frontmatter. No nesting, no lists."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    meta: dict[str, str] = {}
    for line in block.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return meta, body


# ──────────────────────────────────────────────────────────────────────────────
# Inline markdown for the title (used in <h1> and the writing list)
#
# Supports just the inline subset we need:
#   *italic*  →  <em>italic</em>
#   _italic_  →  <em>italic</em>
#   **bold**  →  <strong>bold</strong>
#   `code`    →  <code>code</code>
# ──────────────────────────────────────────────────────────────────────────────

def render_inline(text: str) -> str:
    """Render a single line of markdown to inline HTML (no block elements)."""
    out = text
    # Escape & first so we don't double-escape later replacements.
    out = out.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", out)
    out = re.sub(r"(?<!\w)_([^_\n]+)_(?!\w)", r"<em>\1</em>", out)
    return out


def strip_markdown(text: str) -> str:
    """Strip inline markdown so we have a plain-text version (for <title>)."""
    out = re.sub(r"`([^`]+)`", r"\1", text)
    out = re.sub(r"\*\*([^*]+)\*\*", r"\1", out)
    out = re.sub(r"\*([^*\n]+)\*", r"\1", out)
    out = re.sub(r"_([^_\n]+)_", r"\1", out)
    return out


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def estimate_read_time(body: str) -> str:
    words = len(re.findall(r"\w+", body))
    minutes = max(1, round(words / 220))
    return f"{minutes} min read"


def format_month_year(date_str: str) -> str:
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return date_str
    return d.strftime("%b %Y")


def format_long_date(date_str: str) -> str:
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return date_str
    return d.strftime("%b %d, %Y")


def render_body(md_text: str) -> str:
    md = markdown.Markdown(
        extensions=[
            "extra",          # tables, fenced_code, def_lists, footnotes, attr_list
            "sane_lists",
            "smarty",
        ],
        extension_configs={
            "smarty": {"smart_dashes": True, "smart_quotes": False},
        },
    )
    return md.convert(md_text)


def render_tags(tags_csv: str) -> str:
    if not tags_csv:
        return ""
    items = [t.strip() for t in tags_csv.split(",") if t.strip()]
    if not items:
        return ""
    pills = "\n      ".join(
        f'<a class="article-tag" href="#">{t}</a>' for t in items
    )
    return f'<div class="article-tags">\n      {pills}\n    </div>'


def render_nav(prev: dict | None, nxt: dict | None) -> str:
    if not prev and not nxt:
        return ""
    parts = ['<nav class="article-nav" aria-label="More writing">']
    if prev:
        parts.append(
            f'  <a class="article-nav-link prev" href="{prev["slug"]}.html">'
            f'<span class="article-nav-label">← Previous</span>'
            f'<p class="article-nav-title">{strip_markdown(prev["title"])}</p></a>'
        )
    else:
        parts.append('  <span></span>')
    if nxt:
        parts.append(
            f'  <a class="article-nav-link next" href="{nxt["slug"]}.html">'
            f'<span class="article-nav-label">Next →</span>'
            f'<p class="article-nav-title">{strip_markdown(nxt["title"])}</p></a>'
        )
    else:
        parts.append('  <span></span>')
    parts.append('</nav>')
    return "\n  ".join(parts)


def fill(template: str, vars_: dict[str, str]) -> str:
    out = template
    for key, value in vars_.items():
        out = out.replace("{{" + key + "}}", value)
    return out


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def load_posts() -> list[dict]:
    posts: list[dict] = []
    for md_path in sorted(POSTS_DIR.glob("*.md")):
        raw = md_path.read_text()
        meta, body = parse_frontmatter(raw)
        if "title" not in meta or "slug" not in meta or "date" not in meta:
            sys.stderr.write(
                f"WARN: {md_path.name} missing required frontmatter "
                f"(title/slug/date) — skipping\n"
            )
            continue
        post = dict(meta)
        post["body_md"] = body
        post["source"] = md_path
        if "read_time" not in post:
            post["read_time"] = estimate_read_time(body)
        posts.append(post)
    posts.sort(key=lambda p: p.get("date", ""), reverse=True)
    return posts


def build_post(post: dict, prev: dict | None, nxt: dict | None) -> Path:
    body_html = render_body(post["body_md"])
    title_text = strip_markdown(post["title"])
    title_html = render_inline(post["title"])
    lede_html = render_inline(post.get("lede", post.get("description", "")))
    description = post.get("description", strip_markdown(post.get("lede", "")))

    meta_line_parts = [format_month_year(post["date"]), post["read_time"]]
    if post.get("category"):
        meta_line_parts.append(post["category"])
    meta_line = " · ".join(meta_line_parts)

    byline_meta = f"Published {format_long_date(post['date'])}"
    if post.get("updated") and post["updated"] != post["date"]:
        byline_meta += f" · Updated {format_long_date(post['updated'])}"

    html = fill(POST_TEMPLATE, {
        "title": title_text,
        "title_html": title_html,
        "description": description.replace('"', '&quot;'),
        "lede": lede_html,
        "meta_line": meta_line,
        "byline_meta": byline_meta,
        "tags_block": render_tags(post.get("tags", "")),
        "nav_block": render_nav(prev, nxt),
        "body": body_html,
    })

    out_path = WRITING_DIR / f"{post['slug']}.html"
    out_path.write_text(html)
    return out_path


def build_writing_list(posts: list[dict]) -> str:
    if not posts:
        return '      <li class="writing-empty"><p>More writing coming soon.</p></li>'
    rows = []
    for post in posts:
        meta_parts = [post["read_time"]]
        if post.get("category"):
            meta_parts.append(post["category"])
        meta_line = " · ".join(meta_parts)
        rows.append(
            f'      <li class="writing-item">\n'
            f'        <a class="writing-link" href="writing/{post["slug"]}.html">\n'
            f'          <span class="writing-date">{format_month_year(post["date"])}</span>\n'
            f'          <div>\n'
            f'            <p class="writing-title">{render_inline(post["title"])}</p>\n'
            f'            <p class="writing-meta">{meta_line}</p>\n'
            f'          </div>\n'
            f'          <svg class="writing-arrow" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17 17 7M9 7h8v8"/></svg>\n'
            f'        </a>\n'
            f'      </li>'
        )
    return "\n".join(rows)


def build_index(posts: list[dict]) -> Path:
    html = fill(INDEX_TEMPLATE, {"writing_list": build_writing_list(posts)})
    out_path = ROOT / "index.html"
    out_path.write_text(html)
    return out_path


def main() -> None:
    WRITING_DIR.mkdir(exist_ok=True)
    posts = load_posts()
    if not posts:
        print("No posts found in posts/.")
    for i, post in enumerate(posts):
        # posts are date-desc; "previous" in the reading sense is older = next index.
        nxt = posts[i - 1] if i > 0 else None
        prev = posts[i + 1] if i + 1 < len(posts) else None
        out = build_post(post, prev=prev, nxt=nxt)
        print(f"  wrote {out.relative_to(ROOT)}")
    out = build_index(posts)
    print(f"  wrote {out.relative_to(ROOT)}  ({len(posts)} post{'s' if len(posts) != 1 else ''})")


if __name__ == "__main__":
    main()
