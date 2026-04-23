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
  - [ ] The project is in git with a clean first commit.
  - [ ] The source repository exists on GitHub as a private repo.
  - [ ] The repo contains the files needed for GitHub Pages custom-domain setup.
  - [ ] The remaining publish path is documented clearly enough to finish without guesswork.
- **Status**: In Progress

## Blockers / Open Questions

- GitHub Pages cannot publish directly from a private repo on the current `GitHub Free` personal plan.
- Decide between upgrading the account to GitHub Pro or using a separate public deploy repository while keeping this source repo private.

## Up Next

- [ ] Initialize git and create the private source repository
- [ ] Add GitHub Pages support files and deployment notes
- [ ] Choose the final publish path for the private-source requirement

## Completed

- [x] Inspected the current repo and confirmed the site is a single static `index.html`
- [x] Confirmed GitHub auth is available locally as `willhennessy`
- [x] Verified the current GitHub account plan is `free`
- [x] Verified the current DNS for `willhennessy.io` is still pointed at Namecheap parking

## Notes for Next Session

The source repo can be private, but the current account plan blocks direct GitHub Pages publishing from that repo. The likely next step is either an account upgrade or a two-repo setup with a private source repo and a public Pages deploy repo.
