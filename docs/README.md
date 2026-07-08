# GitHub Pages setup

Documentation lives in the `docs/` folder and deploys automatically via `.github/workflows/pages.yml`.

## One-time repository settings

1. Open **Settings → Pages** in the GitHub repository.
2. Under **Build and deployment**, set **Source** to **GitHub Actions** (not “Deploy from branch”).
3. Push to `main` (or `master`) — the workflow publishes on changes under `docs/`.

## URL

https://vaagatech.github.io/snapline-python/

Related: [Node.js edition](https://vaagatech.github.io/snapline/) · [Snapline Hub](https://github.com/vaagatech/snapline-hub) (optional reporting UI)

## Local preview

```bash
npx serve docs
```
