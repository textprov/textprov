# Proposal website

The homepage introduces the proposal and includes VS-marked prose and a mixed human/AI demonstration beside the ℗ switch. The switch reveals the embedded labels. Generated proposal pages have their own switch for the marked Markdown prose. The earlier human/AI decoder does not implement the proposed voice-reference model. `node mark-markdown.js` labels unmarked prose in the proposal documents as an AI demo; existing labels are preserved. Markdown syntax, URLs, and code stay intact. `node mark-html.js` applies the same AI demo labels to homepage prose, preserving the example’s existing labels. HTML attributes, controls, code, and the SVG diagram stay intact.

`build-proposal.js` publishes the canonical proposal documents as fourteen individual HTML pages with document and section contents lists. `proposal.html` is their contents page; generated output is ignored. No special fonts are needed. The sun/moon button switches between light and dark. The first visit follows the system preference; a saved override applies to every page.

```sh
cd site
npm ci
npm test
npm run build
npm run dev
```

The ℗ switch hides the labels. Append `?prov-display-version=v0.3.0-bracket&prov-display-tier=quiet` to switch on the candidate display version for evaluation; it replaces the passage/exact selector with a Latent / Quiet / Loud control, both choices are remembered in the browser, and `?prov-display-version=` returns to the recommendation. See [display versions](../docs/development/display-versions.md).

The renderer and its display styles are retained experimental code in `../js/`. The tests check proposal rendering and toggle behavior. Deployment is managed by `.github/workflows/pages.yml`; building locally does not publish the site.
