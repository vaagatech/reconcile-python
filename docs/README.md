# GitHub Pages setup

Documentation lives in the `docs/` folder and deploys automatically via `.github/workflows/pages.yml`.

## One-time repository settings

1. Open **Settings → Pages** in the GitHub repository.
2. Under **Build and deployment**, set **Source** to **GitHub Actions** (not “Deploy from branch”).
3. Push to `main` (or `master`) — the workflow publishes on changes under `docs/`.

## URL

https://vaagatech.github.io/snapline-python/

## Site structure

| Page | Contents |
|------|----------|
| [index.html](index.html) | Overview, install, reconciliation pipeline |
| [architecture.html](architecture.html) | Package layers including **messaging-adapters** |
| [guide.html](guide.html) | End-to-end workflow including **queue → poll** |
| [reference.html](reference.html) | API reference including `publishAndPoll` |

Styling: [assets/style.css](assets/style.css) — Inter font, sticky sidebar, responsive layout.

Related: [Node.js edition](https://vaagatech.github.io/snapline/) · [Snapline Hub](https://vaagatech.github.io/snapline-hub/)

## Local preview

```bash
npx serve docs
```
