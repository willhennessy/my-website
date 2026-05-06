#!/usr/bin/env python3
"""
Publish willhennessy.io from the local writing repo.

Source of truth lives at /Users/will/code/writing/publish/. This script:
  1. Recursively scans that tree for `*.md` files with required frontmatter
     (`title`, `slug`, `date`). Files without all three are skipped silently.
  2. For each qualifying source, copies the markdown into `posts/<slug>.md`
     and copies any referenced images into `assets/posts/<slug>/`, rewriting
     image paths in the markdown so they resolve from `writing/<slug>.html`.
  3. Renders each post into `writing/<slug>.html`.
  4. Syncs titles for existing writing-list links in `index.html`.

`index.html` writing-list membership/order is hand-maintained. Titles for
existing linked posts are synced from post frontmatter.

Posts in `posts/` whose slugs don't appear in the source tree are left alone
(non-destructive). To remove one, delete it manually.

Usage:  python3 publish.py

Frontmatter keys (all optional except title, slug, date):
    title         e.g. "The *shape* of a good PRD"   (markdown allowed)
    slug          e.g. "the-shape-of-a-good-prd"
    date          YYYY-MM-DD (publish date)
    updated       YYYY-MM-DD (optional)
    read_time     "6 min read"  (auto-estimated if omitted)
    category      "Product"
    description   plain-text meta description (used for SEO)
    lede          one-paragraph subhead under the title (markdown allowed)

Dependency:  pip3 install markdown

Vimeo embeds: paste Vimeo's iframe embed into markdown. The publisher
normalizes player.vimeo.com iframes into responsive embeds and loads Vimeo's
player script once per post.
"""

from __future__ import annotations

import re
import shutil
import sys
from datetime import datetime
from html import escape, unescape
from pathlib import Path
from urllib.parse import urlparse

try:
    import markdown
except ImportError:
    sys.stderr.write(
        "Missing dependency: install with `pip3 install --user markdown`\n"
    )
    sys.exit(1)


# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────

SOURCE_DIR = Path("/Users/will/code/writing/publish")  # external source of truth

ROOT = Path(__file__).resolve().parent
INDEX_PATH = ROOT / "index.html"
POSTS_DIR = ROOT / "posts"                # markdown snapshots (derived)
WRITING_DIR = ROOT / "writing"            # rendered HTML (derived)
ASSETS_POSTS_DIR = ROOT / "assets" / "posts"  # post images (derived)
TEMPLATES_DIR = ROOT / "templates"

POST_TEMPLATE = (TEMPLATES_DIR / "post.html").read_text()


# ──────────────────────────────────────────────────────────────────────────────
# Frontmatter parsing
# ──────────────────────────────────────────────────────────────────────────────

def split_frontmatter(text: str) -> tuple[str, str]:
    """Return (header, body) where header includes the trailing `---`."""
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 3)
    if end == -1:
        return "", text
    header = text[: end + 4]
    body = text[end + 4 :].lstrip("\n")
    return header, body


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse simple `key: value` YAML-ish frontmatter. No nesting, no lists."""
    header, body = split_frontmatter(text)
    if not header:
        return {}, body
    block = header[3:-4].strip()  # strip leading "---" and trailing "\n---"
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
# ──────────────────────────────────────────────────────────────────────────────

def render_inline(text: str) -> str:
    out = text
    out = out.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", out)
    out = re.sub(r"(?<!\w)_([^_\n]+)_(?!\w)", r"<em>\1</em>", out)
    return out


def strip_markdown(text: str) -> str:
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


# An italic-only line immediately after an image becomes the image's caption.
# Tolerates one optional blank line between the two for readability.
MD_IMAGE_LINE_RE = re.compile(
    r"^\s*!\[([^\]]*)\]\(\s*(.+?)(?:\s+\"([^\"]*)\")?\s*\)(?:\{([^}]*)\})?\s*$"
)
ITALIC_LINE_RE = re.compile(
    r"^\s*(?:\*([^*\n]+?)\*|_([^_\n]+?)_)\s*$"
)
_CLASS_TOKEN_RE = re.compile(r"^[A-Za-z_][\w-]*$")


def _parse_attr_classes(raw: str | None) -> str:
    if not raw:
        return ""
    classes = [
        t[1:] for t in raw.split()
        if t.startswith(".") and len(t) > 1 and _CLASS_TOKEN_RE.match(t[1:])
    ]
    return " ".join(classes)


def attach_image_captions(md_text: str) -> str:
    lines = md_text.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        img = MD_IMAGE_LINE_RE.match(lines[i])
        if img:
            alt = img.group(1).replace('"', '&quot;')
            src = img.group(2)
            title = img.group(3)
            classes = _parse_attr_classes(img.group(4))
            title_attr = f' title="{title}"' if title else ""
            class_attr = f' class="{classes}"' if classes else ""

            j = i + 1
            if j < len(lines) and lines[j].strip() == "":
                j += 1
            cap = ITALIC_LINE_RE.match(lines[j]) if j < len(lines) else None

            if cap:
                caption = cap.group(1) or cap.group(2)
                if out and out[-1].strip():
                    out.append("")
                out.append(
                    f'<figure>'
                    f'<img src="{src}" alt="{alt}"{title_attr}{class_attr}>'
                    f'<figcaption>{render_inline(caption)}</figcaption>'
                    f'</figure>'
                )
                out.append("")
                i = j + 1
                continue

            if classes:
                if out and out[-1].strip():
                    out.append("")
                out.append(f'<img src="{src}" alt="{alt}"{title_attr}{class_attr}>')
                out.append("")
                i += 1
                continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


VIMEO_PLAYER_SCRIPT = (
    '<script src="https://player.vimeo.com/api/player.js"></script>'
)
VIMEO_PLAYER_SCRIPT_RE = re.compile(
    r"\s*<script\s+src=([\"'])https://player\.vimeo\.com/api/player\.js\1\s*>\s*</script>\s*",
    re.IGNORECASE,
)
VIMEO_EMBED_RE = re.compile(
    r"(?:<div\b[^>]*>\s*)?"
    r"<iframe\b(?P<attrs>[^>]*)>\s*</iframe>"
    r"\s*(?:</div>)?"
    r"(?:\s*<script\s+src=([\"'])https://player\.vimeo\.com/api/player\.js\2\s*>\s*</script>)?",
    re.IGNORECASE | re.DOTALL,
)
HTML_ATTR_RE = re.compile(
    r"([A-Za-z_:][\w:.-]*)\s*=\s*(?:\"([^\"]*)\"|'([^']*)')"
)


def _parse_html_attrs(raw: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for match in HTML_ATTR_RE.finditer(raw):
        attrs[match.group(1).lower()] = unescape(match.group(2) or match.group(3) or "")
    return attrs


def _is_vimeo_player_src(src: str) -> bool:
    parsed = urlparse(src)
    return (
        parsed.scheme == "https"
        and parsed.netloc == "player.vimeo.com"
        and parsed.path.startswith("/video/")
    )


def _render_vimeo_embed(attrs: dict[str, str]) -> str:
    iframe_attrs = {
        "src": attrs["src"],
        "frameborder": attrs.get("frameborder", "0"),
        "allow": attrs.get(
            "allow",
            "autoplay; fullscreen; picture-in-picture; clipboard-write; "
            "encrypted-media; web-share",
        ),
        "referrerpolicy": attrs.get(
            "referrerpolicy",
            "strict-origin-when-cross-origin",
        ),
        "style": "position:absolute;top:0;left:0;width:100%;height:100%;",
        "title": attrs.get("title", "Vimeo video"),
    }
    attr_text = " ".join(
        f'{name}="{escape(value, quote=True)}"'
        for name, value in iframe_attrs.items()
        if value
    )
    return (
        '<div class="vimeo-embed" '
        'style="padding:56.25% 0 0 0;position:relative;">'
        f"<iframe {attr_text}></iframe>"
        "</div>"
    )


def normalize_vimeo_embeds(md_text: str) -> str:
    found = False

    def _sub(match: re.Match) -> str:
        nonlocal found
        attrs = _parse_html_attrs(match.group("attrs"))
        src = attrs.get("src", "")
        if not _is_vimeo_player_src(src):
            return match.group(0)
        found = True
        return _render_vimeo_embed(attrs)

    out = VIMEO_EMBED_RE.sub(_sub, md_text)
    if found:
        out = VIMEO_PLAYER_SCRIPT_RE.sub("\n", out)
        out = out.rstrip() + f"\n\n{VIMEO_PLAYER_SCRIPT}\n"
    return out


def render_body(md_text: str) -> str:
    md_text = attach_image_captions(md_text)
    md_text = normalize_vimeo_embeds(md_text)
    md = markdown.Markdown(
        extensions=["extra", "sane_lists", "smarty"],
        extension_configs={"smarty": {"smart_dashes": True, "smart_quotes": False}},
    )
    return md.convert(md_text)


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
# Image handling
# ──────────────────────────────────────────────────────────────────────────────

REMOTE_PREFIXES = ("http://", "https://", "data:", "//")

# Path group is non-greedy so paths with spaces (common from Typora's
# absolute paths into ~/Library/Application Support/...) match correctly.
MD_IMAGE_RE = re.compile(
    r"!\[([^\]]*)\]\(\s*(.+?)(?:\s+\"([^\"]*)\")?\s*\)"
)
HTML_IMG_RE = re.compile(
    r"<img\s+[^>]*?src=([\"'])([^\"']+)\1[^>]*?>", re.IGNORECASE
)


def _is_remote(src: str) -> bool:
    return src.startswith(REMOTE_PREFIXES)


def copy_assets_and_rewrite(body: str, src_md: Path, slug: str) -> str:
    """Copy referenced images into assets/posts/<slug>/ and rewrite paths."""
    src_dir = src_md.parent
    asset_dest = ASSETS_POSTS_DIR / slug

    # Per-slug clean: remove stale images from a previous run.
    if asset_dest.exists():
        shutil.rmtree(asset_dest)

    copied: dict[str, str] = {}  # original src → new relative path

    def _resolve_and_copy(src: str) -> str | None:
        if _is_remote(src):
            return None
        if src in copied:
            return copied[src]
        # Absolute filesystem paths (e.g. Typora's auto-inserted
        # ~/Library/Application Support/typora-user-images/...) are taken
        # as-is. Relative paths resolve against the source markdown's folder.
        if src.startswith("/"):
            candidate = Path(src)
        else:
            candidate = (src_dir / src).resolve()
        if not candidate.is_file():
            sys.stderr.write(
                f"WARN: image not found: {src!r} referenced in "
                f"{src_md.relative_to(SOURCE_DIR)}\n"
            )
            return None
        asset_dest.mkdir(parents=True, exist_ok=True)
        # Flatten to basename. If two posts share the same image filename
        # they live in different slug folders, so no collision across posts.
        # Within one post, two distinct paths with the same basename would
        # collide — disambiguate with a numeric suffix.
        name = candidate.name
        target = asset_dest / name
        if target.exists() and target.read_bytes() != candidate.read_bytes():
            stem, suffix = candidate.stem, candidate.suffix
            i = 2
            while (asset_dest / f"{stem}-{i}{suffix}").exists():
                i += 1
            name = f"{stem}-{i}{suffix}"
            target = asset_dest / name
        shutil.copy2(candidate, target)
        new_path = f"../assets/posts/{slug}/{name}"
        copied[src] = new_path
        return new_path

    def _md_sub(match: re.Match) -> str:
        alt, src, title = match.group(1), match.group(2), match.group(3)
        new = _resolve_and_copy(src)
        if new is None:
            return match.group(0)
        if title:
            return f'![{alt}]({new} "{title}")'
        return f"![{alt}]({new})"

    def _html_sub(match: re.Match) -> str:
        full = match.group(0)
        src = match.group(2)
        new = _resolve_and_copy(src)
        if new is None:
            return full
        return full.replace(src, new, 1)

    body = MD_IMAGE_RE.sub(_md_sub, body)
    body = HTML_IMG_RE.sub(_html_sub, body)
    return body


# ──────────────────────────────────────────────────────────────────────────────
# Source → posts/ snapshot
# ──────────────────────────────────────────────────────────────────────────────

def collect_sources() -> list[Path]:
    if not SOURCE_DIR.exists():
        sys.stderr.write(f"ERR: source dir does not exist: {SOURCE_DIR}\n")
        sys.exit(1)
    return sorted(SOURCE_DIR.rglob("*.md"))


def snapshot_post(src_md: Path) -> dict | None:
    """Copy one source markdown into posts/<slug>.md with rewritten image paths.

    Returns the parsed post dict, or None if the file lacks required frontmatter.
    """
    raw = src_md.read_text()
    meta, body = parse_frontmatter(raw)
    if not all(k in meta for k in ("title", "slug", "date")):
        return None

    slug = meta["slug"]
    new_body = copy_assets_and_rewrite(body, src_md, slug)

    header, _ = split_frontmatter(raw)
    new_md = (header + "\n\n" + new_body) if header else new_body
    (POSTS_DIR / f"{slug}.md").write_text(new_md)

    return {"src": src_md, "meta": meta, "body": new_body}


# ──────────────────────────────────────────────────────────────────────────────
# Render
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

    meta_line_parts = [post["read_time"]]
    if post.get("category"):
        meta_line_parts.append(post["category"])
    meta_line = " · ".join(meta_line_parts)

    byline_meta = format_long_date(post['date'])
    if post.get("updated") and post["updated"] != post["date"]:
        byline_meta += f" · Updated {format_long_date(post['updated'])}"

    html = fill(POST_TEMPLATE, {
        "title": title_text,
        "title_html": title_html,
        "description": description.replace('"', '&quot;'),
        "lede": lede_html,
        "meta_line": meta_line,
        "byline_meta": byline_meta,
        "nav_block": render_nav(prev, nxt),
        "body": body_html,
    })

    out_path = WRITING_DIR / f"{post['slug']}.html"
    out_path.write_text(html)
    return out_path


# ──────────────────────────────────────────────────────────────────────────────
# Home page sync
# ──────────────────────────────────────────────────────────────────────────────

WRITING_LINK_RE = re.compile(
    r"(<a\b"
    r"(?=[^>]*\bclass=[\"'][^\"']*\bwriting-link\b[^\"']*[\"'])"
    r"(?=[^>]*\bhref=[\"']writing/([^\"']+)\.html[\"'])"
    r"[^>]*>)(.*?)(</a>)",
    re.DOTALL,
)
WRITING_TITLE_RE = re.compile(
    r"(<p\b[^>]*\bclass=[\"'][^\"']*\bwriting-title\b[^\"']*[\"'][^>]*>)"
    r"(.*?)(</p>)",
    re.DOTALL,
)


def sync_index_writing_titles(posts: list[dict]) -> int:
    """Update homepage writing titles for links that already exist there."""
    if not INDEX_PATH.exists():
        return 0

    titles_by_slug = {
        post["slug"]: render_inline(post["title"])
        for post in posts
    }
    html = INDEX_PATH.read_text()
    updated = 0

    def _replace_link(match: re.Match) -> str:
        nonlocal updated
        open_tag, slug, body, close_tag = match.groups()
        title = titles_by_slug.get(slug)
        if title is None:
            return match.group(0)

        def _replace_title(title_match: re.Match) -> str:
            nonlocal updated
            before, current, after = title_match.groups()
            if current != title:
                updated += 1
            return f"{before}{title}{after}"

        new_body = WRITING_TITLE_RE.sub(_replace_title, body, count=1)
        return f"{open_tag}{new_body}{close_tag}"

    new_html = WRITING_LINK_RE.sub(_replace_link, html)
    if new_html != html:
        INDEX_PATH.write_text(new_html)
    return updated


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    POSTS_DIR.mkdir(exist_ok=True)
    WRITING_DIR.mkdir(exist_ok=True)

    sources = collect_sources()
    snapshotted = 0
    skipped = 0
    for src_md in sources:
        result = snapshot_post(src_md)
        if result is None:
            skipped += 1
            continue
        rel = src_md.relative_to(SOURCE_DIR)
        print(f"  snapshot {rel} → posts/{result['meta']['slug']}.md")
        snapshotted += 1

    print(
        f"  {snapshotted} post{'s' if snapshotted != 1 else ''} snapshotted, "
        f"{skipped} skipped (missing frontmatter)"
    )

    posts = load_posts()
    if not posts:
        print("No publishable posts found.")
        return

    synced_titles = sync_index_writing_titles(posts)
    if synced_titles:
        print(
            f"  synced {synced_titles} index.html writing "
            f"title{'s' if synced_titles != 1 else ''}"
        )
    else:
        print("  index.html writing titles already current")

    for i, post in enumerate(posts):
        # posts are date-desc; "previous" in reading order is older = next index.
        nxt = posts[i - 1] if i > 0 else None
        prev = posts[i + 1] if i + 1 < len(posts) else None
        out = build_post(post, prev=prev, nxt=nxt)
        print(f"  wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
