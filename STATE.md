# STATE

Last updated: 2026-04-23

## Current Objective

Launch the personal website on GitHub Pages at `willhennessy.io`.

## Current Phase

Hosting setup

## Current Task

- [ ] Set up GitHub hosting and custom domain for the site

### Current Task Details

- **Goal**: Prepare the repo for GitHub Pages and publish it behind `willhennessy.io`.
- **Why now**: The site already exists as a static page, so hosting is the fastest path to getting it live.
- **Files in play**:
  - `index.html`
  - `STATE.md`
  - `README.md`
  - `CNAME`
  - `.nojekyll`
  - `.gitignore`
- **Constraints**:
  - GitHub Free does not support GitHub Pages from a private repository.
  - The desired custom domain is the apex domain `willhennessy.io`.
  - `willhennessy.io` DNS is currently managed outside GitHub and still points at Namecheap parking.
- **Acceptance Criteria**:
  - [x] The project is in git with a clean first commit.
  - [x] The source repository exists on GitHub as a private repo.
  - [x] The repo contains the files needed for GitHub Pages custom-domain setup.
  - [x] A public GitHub Pages repository exists and is configured for `willhennessy.io`.
  - [ ] DNS records for `willhennessy.io` point at GitHub Pages and the live site resolves correctly.
- **Status**: In Progress

## Blockers / Open Questions

- `willhennessy.io` still resolves to Namecheap parking instead of GitHub Pages.
- `www.willhennessy.io` still points to `parkingpage.namecheap.com`.
- DNS access is needed to finish the cutover and enable HTTPS on the custom domain.

## Up Next

- [ ] Update Namecheap DNS for `willhennessy.io` and `www`
- [ ] Wait for DNS to propagate
- [ ] Turn on HTTPS enforcement in GitHub Pages once eligible

## Completed

- [x] Confirmed GitHub auth is available locally as `willhennessy`
- [x] Verified the current GitHub account plan is `free`
- [x] Verified the current DNS for `willhennessy.io` is still pointed at Namecheap parking
- [x] Created the private GitHub repo `willhennessy/my-website`
- [x] Confirmed GitHub Pages is blocked on the current plan for that private repo
- [x] Replaced the About section copy in `index.html` with lorem ipsum
- [x] Created the public GitHub repo `willhennessy/personal-website`
- [x] Enabled GitHub Pages for `willhennessy/personal-website`
- [x] Wired the Pages site to the custom domain `willhennessy.io` on the GitHub side

## Notes for Next Session

There are now two remotes for this local repo: the private source repo `origin` (`willhennessy/my-website`) and the public Pages repo `public` (`willhennessy/personal-website`). GitHub Pages is enabled on the public repo with `main` as the source and `willhennessy.io` as the configured custom domain. The remaining work is DNS cutover at Namecheap and then HTTPS enforcement.
