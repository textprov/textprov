# Proposal website

The homepage introduces the proposal and places a bounded VS demonstration beside the ℗ switch. The switch reveals the embedded labels. Generated proposal pages have their own switch for the marked Markdown prose. The earlier human/AI decoder does not implement the proposed voice-reference model. `node mark-markdown.js` labels unmarked prose in the proposal documents as an AI demo; existing labels are preserved. Markdown syntax, URLs, and code stay intact.

`build-proposal.js` publishes the canonical proposal documents as fourteen individual HTML pages with document and section contents lists. `proposal.html` is their contents page; generated output is ignored. No special fonts are needed. The sun/moon button switches between light and dark. The first visit follows the system preference; a saved override applies to every page.

```sh
cd site
npm ci
npm test
npm run build
npm run dev
```

The renderer and its display styles are retained experimental code in `../js/`. The tests check proposal rendering and toggle behavior. Deployment is managed by `.github/workflows/pages.yml`; building locally does not publish the site.
