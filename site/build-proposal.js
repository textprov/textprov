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
  return value.toLowerCase().replace(/[^\p{L}\p{N}\s_-]/gu, "").trim().replace(/\s/g, "-");
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
    const level = Math.min(depth + 1, 6);
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
      if (entry) target = `#${entry[0]}${fragment ? `--${fragment}` : ""}`;
      else target = `https://github.com/textprov/textprov/blob/main/${relative(root, absolute).split("/").map(encodeURIComponent).join("/")}${fragment ? `#${fragment}` : ""}`;
    }
    return marked.Renderer.prototype.link.call(this, { ...token, href: target });
  };
  return `<section id="${escape(id)}">${marked.parse(source, { renderer })}</section>`;
}

export function renderProposal(sources, entries = documents) {
  const toc = entries.map(([id, title]) => `<li><a href="#${id}">${escape(title)}</a></li>`).join("\n");
  const body = entries.map(([id, , path]) => renderDocument(sources[path], path, id, entries)).join("\n");
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="TextProv proposal: source attribution, encoding candidates, open decisions, and evaluation."><title>Proposal — TextProv</title><link rel="stylesheet" href="styles.css"></head>
<body><a class="skip-link" href="#main">Skip to content</a><header class="site-header"><a class="wordmark" href="./">TextProv</a><nav aria-label="Primary navigation"><a href="https://github.com/textprov/textprov">GitHub</a></nav></header><main id="main"><h1>TextProv proposal</h1><p class="lead">Source attribution and its possible representations. The model, requirements, and encoding alternatives remain under discussion.</p><p>These pages publish the proposal documents maintained in the repository. The <a href="./#experiment">homepage VS example</a> demonstrates an earlier encoding; it does not implement the voice-reference model.</p><nav class="proposal-toc" aria-label="Proposal contents"><ul>${toc}</ul></nav><article class="proposal-content">${body}</article></main><footer><p>Proposal under development. <a href="https://github.com/textprov/textprov/blob/main/LICENSE">MIT License</a>.</p></footer></body></html>`;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const sources = Object.fromEntries(documents.map(([, , path]) => [path, readFileSync(resolve(root, path), "utf8")]));
  writeFileSync(resolve(here, "proposal.html"), renderProposal(sources));
  console.log("Generated proposal.html from canonical documents");
}
