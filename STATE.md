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
  - The source repo should be private.
- **Acceptance Criteria**:
  - [x] The project is in git with a clean first commit.
  - [x] The source repository exists on GitHub as a private repo.
  - [x] The repo contains the files needed for GitHub Pages custom-domain setup.
  - [ ] The remaining publish path is documented clearly enough to finish without guesswork.
- **Status**: Blocked

## Blockers / Open Questions

- GitHub Pages cannot publish directly from a private repo on the current `GitHub Free` personal plan.
- GitHub's Pages API returns `422 Your current plan does not support GitHub Pages for this repository` for `willhennessy/my-website`.
- Decide between upgrading the account to GitHub Pro or using a separate public deploy repository while keeping this source repo private.

## Up Next

- [ ] Choose the final publish path for the private-source requirement
- [ ] Configure GitHub Pages in the chosen publish repo
- [ ] Switch DNS from Namecheap parking to the final GitHub Pages target

## Completed

- [x] Confirmed GitHub auth is available locally as `willhennessy`
- [x] Verified the current GitHub account plan is `free`
- [x] Verified the current DNS for `willhennessy.io` is still pointed at Namecheap parking
- [x] Created the private GitHub repo `willhennessy/my-website`
- [x] Confirmed GitHub Pages is blocked on the current plan for that private repo

## Notes for Next Session

The source repo is now live at `https://github.com/willhennessy/my-website`. GitHub Pages cannot publish directly from it on the current plan, so the next move is either an account upgrade to GitHub Pro or a two-repo setup with this private source repo plus a public Pages deploy repo.
