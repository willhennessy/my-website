# STATE

Last updated: 2026-05-06

## Current Objective

Launch the personal website on GitHub Pages at `willhennessy.io`.

## Current Phase

Design implementation + content workflow

## Current Task

- [ ] Verify the new design + markdown build pipeline end-to-end and finish DNS cutover.

### Current Task Details

- **Goal**: Ship the redesigned site (from the Claude Design handoff) with a working markdown → HTML build, then complete the GitHub Pages DNS cutover.
- **Why now**: Design is in, the build script works locally, and DNS is the only remaining blocker for the live site.
- **Files in play**:
  - `index.html` (hand-maintained home page)
  - `tokens.css`, `site.css`, `assets/headshot.jpg`
  - `templates/post.html`
  - `posts/*.md`, `writing/*.html`
  - `publish.py`
- **Constraints**:
  - Must be a static site (GitHub Pages).
  - `willhennessy.io` DNS still managed at Namecheap and pointed at parking.
- **Acceptance Criteria**:
  - [x] Repo contains the redesigned static site (tokens, styles, hero, writing list, projects, footer).
  - [x] `publish.py` renders markdown posts into `writing/*.html`.
  - [x] At least one real post renders end-to-end and is linked from the index.
  - [ ] DNS records for `willhennessy.io` point at GitHub Pages and the live site resolves correctly.
  - [ ] HTTPS enforced on the custom domain.
- **Status**: In Progress

## Blockers / Open Questions

- `willhennessy.io` still resolves to Namecheap parking instead of GitHub Pages.
- `www.willhennessy.io` still points to `parkingpage.namecheap.com`.

## Up Next

- [ ] Update Namecheap DNS for `willhennessy.io` and `www`
- [ ] Wait for DNS to propagate
- [ ] Turn on HTTPS enforcement in GitHub Pages once eligible
- [ ] Backfill more posts (`posts/*.md`) and rerun `python3 publish.py`

## Completed

- [x] Synced homepage writing titles from post frontmatter and added `publish.py` automation for existing writing-list links
- [x] Added Vimeo embed support to `publish.py` and published the Architect demo video in `introducing-architect`
- [x] Implemented the Claude Design handoff: `tokens.css`, `site.css`, hero, writing list, projects, footer
- [x] Stripped design-time tooling (tweaks panel, React/Babel CDN) from production HTML
- [x] Wired GitHub Pages to the custom domain `willhennessy.io`

## Notes for Next Session

The home page is hand-maintained in `index.html`, including the projects grid and writing-list membership/order. `publish.py` syncs posts from `/Users/will/code/writing/publish` into `posts/`, renders `writing/*.html`, normalizes pasted Vimeo iframe embeds, and now syncs titles for existing homepage writing links from post frontmatter. The remaining blocker is DNS at Namecheap.
