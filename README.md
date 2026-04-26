# my-website

Static personal site for `willhennessy.io`.

## What this is

- Static site, GitHub Pages-ready via `CNAME` and `.nojekyll`
- Design implemented from a Claude Design handoff bundle (Instrument Sans/Serif, light + dark themes, ochre accent)
- Markdown-driven blog: write `posts/*.md`, run the build, commit the generated HTML

## Repo layout

```
index.html               # generated — site landing page
tokens.css, site.css     # design tokens + styles (hand-edit these)
assets/                  # images
posts/                   # blog posts in markdown (write here)
writing/                 # generated HTML for each post
templates/
  index.html             # source template for index.html
  post.html              # source template for each post
build.py                 # markdown → HTML build
```

## Writing a new post

1. Create `posts/<slug>.md` with frontmatter:

   ```markdown
   ---
   title: The *shape* of a good PRD
   slug: the-shape-of-a-good-prd
   date: 2026-03-15
   read_time: 6 min read
   category: Product
   description: One-sentence SEO blurb.
   lede: Subhead under the title (markdown allowed).
   ---

   Body in markdown.
   ```

   Required: `title`, `slug`, `date`. Everything else has sensible defaults
   (e.g. `read_time` is auto-estimated).

2. Run the build:

   ```bash
   pip3 install --user markdown   # one-time
   python3 build.py
   ```

3. Commit `posts/<slug>.md`, the generated `writing/<slug>.html`, and the
   updated `index.html`.

## Local preview

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## GitHub Pages notes

This repo is prepared for the custom domain `willhennessy.io`.

Important constraint:

- GitHub’s current docs say Pages can publish from private repositories only on `GitHub Pro`, `GitHub Team`, `GitHub Enterprise Cloud`, or `GitHub Enterprise Server`.
- On a personal `GitHub Free` plan, the source repo can stay private, but the published Pages site needs a different path.

Current options:

1. Upgrade the account to `GitHub Pro` and publish this repo directly with GitHub Pages.
2. Keep this repo private and deploy the static site to a separate public Pages repo.

## Custom domain DNS

For the apex domain `willhennessy.io`, GitHub’s current docs list these `A` records:

- `185.199.108.153`
- `185.199.109.153`
- `185.199.110.153`
- `185.199.111.153`

Recommended companion record:

- `www` `CNAME` -> `willhennessy.github.io`

Recommended hardening:

- Verify `willhennessy.io` in GitHub Pages account settings before or during domain setup.
- Avoid wildcard DNS records like `*.willhennessy.io`.

Relevant docs:

- `https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site`
- `https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages`

## Current DNS status

As of `2026-04-23`:

- `willhennessy.io` resolves to `192.64.119.50`
- `www.willhennessy.io` points to `parkingpage.namecheap.com`

That means DNS still needs to be switched before GitHub Pages can serve the site.
