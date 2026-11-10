# STATE

Last updated: 2026-11-09

## Current Objective

Maintain the personal website and project portfolio for `willhennessy.io` on GitHub Pages.

## Current Phase

Release and deployment

## Current Task

- [ ] Merge and deploy the portfolio updates.

### Current Task Details

- **Goal**: Merge the Sierra portfolio and theme updates into main and verify the live GitHub Pages site.
- **Why now**: Will approved release and deployment of the reviewed updates.
- **Files in play**:
  - `index.html`
  - `site.css`
  - `assets/projects/retention-agents.jpg`
  - `STATE.md`
- **Constraints**:
  - Preserve the requested copy and light-mode appearance.
  - Use the existing GitHub Pages deployment from main.
- **Acceptance Criteria**:
  - [x] Static checks pass for copy, project tags, local image assets, JPEG validity, and whitespace.
  - [ ] Release PR is merged into main.
  - [ ] GitHub Pages deployment succeeds for the merge commit.
  - [ ] Live HTTPS homepage, styles, and thumbnail serve the updates.
- **Status**: In Progress

## Blockers / Open Questions

- GitHub CLI and Git push credentials are expired; the connected GitHub app has write access and is being used for publication.

## Up Next

- [ ] Merge the release PR.
- [ ] Wait for the GitHub Pages build and verify the live site.
- [ ] Backfill more posts (`posts/*.md`) when requested.

## Completed

- [x] Added a Magnet-only dark-mode blue base to reduce the white cast while preserving light mode.
- [x] Decoupled project thumbnail gradient bases from the dark sidebar color and verified light-mode gradients remain identical.
- [x] Applied all six browser copy comments and updated the homepage meta description for Sierra positioning.
- [x] Added Retention Agents first in the projects grid with the Sierra Accelerators thumbnail, purple colors, and responsive preview verification.
- [x] Synced homepage writing titles from post frontmatter and added `publish.py` automation for existing writing-list links

## Notes for Next Session

`site.css` now sets `--thumb-base: #F6F5F0` on `.project-thumb`, matching the light sidebar color in both themes by default. Magnet overrides that base to `#8BBDE0` only in dark mode, using its project URL as the selector. Per-card accent colors and radial overlays still apply. Dark-theme accent tokens can still differ slightly from light-theme accents; the default pale base is fixed, with the intentional Magnet dark-mode exception. The latest gradient adjustment passed direct CSS equivalence checks but was not visually verified in the browser.

The home page is hand-maintained in `index.html`, including the projects grid and writing-list membership/order. Retention Agents is the first project, uses the existing card styles, and shares a singular Agent tag with Architect. The homepage now positions Will as building long-horizon agents at Sierra and describes Architect in the past tense. Its local thumbnail is Sierra's original social image, downloaded at 1200 × 630 from `https://cdn.sanity.io/images/ca4jck6w/production/78a871ab7a1c63c02afc931c3e3113eaae79c113-2400x1260.png?w=1200`. Verified locally at desktop and 390px mobile widths; changes have not been committed or deployed. `publish.py` syncs posts from `/Users/will/code/writing/publish` into `posts/`, renders `writing/*.html`, normalizes pasted Vimeo iframe embeds, and syncs titles for existing homepage writing links from post frontmatter. The HTTPS production URL responds successfully from GitHub Pages as of this release session; the earlier DNS parking notes are historical.

Latest copy edit: Retention Agents now reads “Long-horizon agents to increase retention for subscription companies.”

Hero subtitle now reads “PM at Sierra.”
