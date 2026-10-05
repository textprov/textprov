# Proposal website

The homepage introduces the proposal and retains one explicitly bounded VS demonstration. The ℗ switch changes only that example’s display. The earlier human/AI decoder does not implement the proposed voice-reference model.

`build-proposal.js` publishes the canonical proposal documents as `proposal.html`; generated output is ignored. No special fonts are needed.

```sh
cd site
npm ci
npm test
npm run build
npm run dev
```

The renderer and its display styles are retained experimental code in `../js/`. The tests check proposal rendering and toggle behavior. Deployment is managed by `.github/workflows/pages.yml`; building locally does not publish the site.
