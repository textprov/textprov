import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { marked } from "marked";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
export const documents = [
  ["model", "Model", "docs/model.md"],
  ["requirements", "Requirements", "docs/requirements.md"],
  ["encodings", "Encoding candidates", "docs/encodings/README.md"],
  ["vs", "Experimental variation selectors", "docs/encodings/vs.md"],
  ["additive-pua", "Private-use markers", "docs/encodings/additive-pua.md"],
  ["annotations", "Interlinear annotations", "docs/encodings/annotations.md"],
  ["tags", "Tag characters", "docs/encodings/tags.md"],
  ["run-delimiters", "Run delimiters", "docs/encodings/run-delimiters.md"],
  ["other-controls", "Other controls", "docs/encodings/other-controls.md"],
  ["joiners-combining", "Joiners and combining marks", "docs/encodings/joiners-combining.md"],
  ["external-metadata", "External metadata", "docs/encodings/external-metadata.md"],
  ["unicode", "Standardized mechanism proposal", "docs/proposals/unicode.md"],
  ["decisions", "Open decisions", "docs/decisions.md"],
  ["evaluation", "Evaluation", "docs/evaluation.md"],
];
const escape = (value) => value.replace(/[&<>"']/g, c => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"})[c]);
export function slug(value) {
  return value.replace(/[\u{E0100}\u{E0101}]/gu, "").toLowerCase().replace(/[^\p{L}\p{N}\s_-]/gu, "").trim().replace(/\s/g, "-");
}

export function renderDocument(source, path, id, entries = documents) {
  const renderer = new marked.Renderer();
  const headings = new Map();
  renderer.heading = function ({ tokens, depth }) {
    const inline = this.parser.parseInline(tokens);
    const text = tokens.map(t => t.text ?? t.raw ?? "").join("");
    const base = slug(text);
    const count = headings.get(base) ?? 0;
    headings.set(base, count + 1);
    const headingId = `${id}--${base}${count ? `-${count}` : ""}`;
    // Sections supply the document anchor; retain the source H1 fragment as well.
    const level = depth;
    const result = `<h${level} id="${escape(headingId)}">${inline}<a class="heading-link" href="#${escape(headingId)}" aria-label="Link to this section">#</a></h${level}>\n`;
    return result;
  };
  renderer.link = function (token) {
    const href = token.href;
    let target = href;
    if (!/^[a-z][a-z0-9+.-]*:/i.test(href) && !href.startsWith("//")) {
      const [file, fragment] = href.split("#");
      const absolute = file ? resolve(root, dirname(path), file) : resolve(root, path);
      const entry = entries.find(e => resolve(root, e[2]) === absolute);
      if (entry) target = `./${entry[0]}.html${fragment ? `#${entry[0]}--${fragment}` : ""}`;
      else target = `https://github.com/textprov/textprov/blob/main/${relative(root, absolute).split("/").map(encodeURIComponent).join("/")}${fragment ? `#${fragment}` : ""}`;
    }
    return marked.Renderer.prototype.link.call(this, { ...token, href: target });
  };
  return `<section id="${escape(id)}">${marked.parse(source, { renderer })}</section>`;
}

export const licenseFooter = `<footer><p>TextProv is a proposal under development. Documentation: <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. Code: <a href="https://www.apache.org/licenses/LICENSE-2.0">Apache 2.0</a>.</p></footer>`;

function contents(entries, current) {
  return `<nav class="proposal-toc" aria-label="Proposal contents"><p><strong>Contents</strong></p><ul>${entries.map(([id, title]) => `<li><a href="./${id}.html"${id === current ? ' aria-current="page"' : ''}>${escape(title)}</a></li>`).join("\n")}</ul></nav>`;
}

function page(title, body) {
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="TextProv proposal: source attribution, encoding candidates, open decisions, and evaluation."><title>${escape(title)} — TextProv</title><script type="module" src="app.js"></script><script src="/theme.js"></script><link rel="stylesheet" href="styles.css"></head>
<body><a class="skip-link" href="#main">Skip to content</a><header class="site-header"><a class="wordmark" href="./">TextProv</a><div class="header-controls"><button type="button" class="theme-toggle" data-theme-toggle hidden aria-label="Switch color theme">🌙</button><nav aria-label="Primary navigation"><a href="https://github.com/textprov/textprov">GitHub</a></nav></div></header><main id="main">${body}</main>${licenseFooter}</body></html>`;
}

export function renderProposal(sources, entries = documents) {
  return page("Proposal", `<h1>TextProv proposal</h1><p class="lead">Source attribution and its possible representations. The model, requirements, and encoding alternatives remain under discussion.</p>${contents(entries)}<p>The <a href="./#experiment">homepage VS demonstration</a> uses an earlier encoding. The proposal documents below define the voice-reference model and explore its open choices.</p>`);
}

export function renderPage(source, entry, entries = documents) {
  const [id, title, path] = entry;
  let body = renderDocument(source, path, id, entries);
  const titleHeading = body.match(/<h1\b[\s\S]*?<\/h1>/)?.[0] ?? "";
  body = body.replace(titleHeading, "");
  const headings = [...body.matchAll(/<h([2-6]) id="([^"]+)">([\s\S]*?)<a class="heading-link"/g)];
  const localToc = headings.length ? `<nav class="section-toc" aria-label="On this page"><p><strong>On this page</strong></p><ul>${headings.map(([, , anchor, label]) => `<li><a href="#${escape(anchor)}">${label}</a></li>`).join("\n")}</ul></nav>` : "";
  return page(title, `<p class="eyebrow"><a href="./proposal.html">Proposal</a> · Draft proposal</p><div class="document-layout">${contents(entries, id)}<article class="proposal-content" id="proposal-text" data-prov-document><div class="title-row">${titleHeading}<span class="provenance-controls"><button type="button" class="prov-toggle" role="switch" aria-checked="true" aria-label="Show embedded provenance labels" aria-controls="proposal-text" data-prov-toggle hidden><span class="prov-toggle-knob" aria-hidden="true">℗</span></button><span class="info-tip"><button type="button" class="info-button" aria-label="About the provenance toggle" aria-describedby="prov-tip">ⓘ</button><span class="tooltip" id="prov-tip" role="tooltip">Reveal the embedded VS demo labels. Turning the display off leaves the labels in the text. Copying preserves them where supported. These demo labels do not verify authorship.</span></span></span></div>${localToc}${body}<p class="note">Source: <a href="https://github.com/textprov/textprov/blob/main/${path}">${path}</a></p></article></div>`);
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const sources = Object.fromEntries(documents.map(([, , path]) => [path, readFileSync(resolve(root, path), "utf8")]));
  writeFileSync(resolve(here, "proposal.html"), renderProposal(sources));
  for (const entry of documents) writeFileSync(resolve(here, `${entry[0]}.html`), renderPage(sources[entry[2]], entry));
  console.log(`Generated proposal contents and ${documents.length} Markdown pages`);
}
