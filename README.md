# my-website

Static personal site for `willhennessy.io`.

## What this is

- Single-file site in `index.html`
- GitHub Pages-ready via `CNAME` and `.nojekyll`
- Intended source repo visibility: private

## Local preview

Open `index.html` directly, or run:

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
