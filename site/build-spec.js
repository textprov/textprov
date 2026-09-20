import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { marked } from "marked";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, "..");
const specPath = resolve(repoRoot, "SPEC.md");
const templatePath = resolve(here, "spec.template.html");
const outPath = resolve(here, "spec.html");

const source = readFileSync(specPath, "utf8");

// Strip the leading "# TextProv protocol specification" heading — the page
// chrome supplies its own title.
const body = source.replace(/^# [^\n]*\n+/, "");

const renderer = new marked.Renderer();

// Build the ToC while rendering the headings.
const toc = [];
const slugCounts = new Map();
function slug(text) {
  const base = text
    .toLowerCase()
    .replace(/[^\w\s.-]/g, "")
    .trim()
    .replace(/\s+/g, "-");
  const count = slugCounts.get(base) ?? 0;
  slugCounts.set(base, count + 1);
  return count === 0 ? base : `${base}-${count}`;
}

const counters = [0, 0, 0, 0, 0, 0];
function sectionNumber(level) {
  const idx = level - 2; // h2 -> 0, h3 -> 1, ...
  if (idx < 0) return "";
  counters[idx] += 1;
  for (let i = idx + 1; i < counters.length; i += 1) counters[i] = 0;
  return counters.slice(0, idx + 1).join(".");
}

renderer.heading = ({ tokens, depth }) => {
  const text = tokens.map((t) => t.raw ?? t.text ?? "").join("");
  const id = slug(text);
  const inner = marked.parser(tokens);
  if (depth === 1) {
    return `<h1 id="${id}">${inner}</h1>\n`;
  }
  const number = sectionNumber(depth);
  toc.push({ id, text, depth, number });
  const numberSpan = number
    ? `<span class="spec-section-number" aria-hidden="true">${number}</span> `
    : "";
  const anchor = `<a class="spec-anchor" href="#${id}" aria-label="Permalink to this section">#</a>`;
  return `<h${depth} id="${id}">${numberSpan}${inner} ${anchor}</h${depth}>\n`;
};

marked.setOptions({ renderer, mangle: false, headerIds: false });

const rendered = marked.parse(body);

function renderToc(items) {
  if (items.length === 0) return "";
  const root = { depth: 1, children: [] };
  const stack = [root];
  for (const item of items) {
    while (stack.length > 1 && stack[stack.length - 1].depth >= item.depth) {
      stack.pop();
    }
    const node = { ...item, children: [] };
    stack[stack.length - 1].children.push(node);
    stack.push(node);
  }
  function walk(node) {
    if (node.children.length === 0) return "";
    const items = node.children
      .map(
        (child) =>
          `<li><a href="#${child.id}"><span class="spec-toc-num">${child.number}</span> <span class="spec-toc-text">${child.text}</span></a>${walk(child)}</li>`,
      )
      .join("");
    return `<ol class="spec-toc-list spec-toc-depth-${node.depth}">${items}</ol>`;
  }
  return walk(root);
}

const tocHtml = renderToc(toc);

const template = readFileSync(templatePath, "utf8");
const html = template
  .replace("<!-- TOC -->", tocHtml)
  .replace("<!-- SPEC -->", rendered);

writeFileSync(outPath, html);
console.log(`Wrote ${outPath}`);
