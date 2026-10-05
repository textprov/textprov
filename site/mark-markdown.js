// Mark prose in the existing VS demo profile, preserving Markdown syntax and URLs.
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";
import { marked } from "marked";
import { documents } from "./build-proposal.js";
const textprov = createRequire(import.meta.url)("../js/textprov.js");
export const stripDemo = text => text.replace(/[\u{E0100}\u{E0101}]/gu, "");

function markText(text, selector) {
  // Entities remain literal Markdown syntax, not marked letter sequences.
  return text.split(/(&(?:#\d+|#x[\da-f]+|[a-z]+);)/gi).map((part, i) => i % 2 ? part : textprov.segments(part).map(cluster => {
    if (/[\u{E0100}\u{E0101}]/u.test(cluster) || !/[\p{L}\p{N}]/u.test(cluster)) return cluster;
    return cluster + selector;
  }).join("")).join("");
}

function inline(source, selector) {
  return marked.Lexer.lexInline(source).map(token => {
    if (token.type === "text") return markText(token.raw, selector);
    // Fenced/inline code, HTML, escapes, and autolink destinations stay intact.
    if (!token.tokens || (token.type === "link" && token.raw === token.href)) return token.raw;
    const start = token.raw.indexOf(token.text);
    if (start < 0) throw new Error(`Unable to locate inline text in ${token.type}`);
    return token.raw.slice(0, start) + inline(token.text, selector) + token.raw.slice(start + token.text.length);
  }).join("");
}

export function markMarkdown(source, state = "ai") {
  if (!["ai", "human"].includes(state)) throw new Error("Use ai or human for the demo label");
  const selector = String.fromCodePoint(state === "ai" ? 0xe0101 : 0xe0100);
  let fence = null;
  return source.split(/(?<=\n)/).map(line => {
    const boundary = line.match(/^\s{0,3}(`{3,}|~{3,})/);
    if (boundary) {
      if (!fence) fence = boundary[1];
      else if (boundary[1][0] === fence[0] && boundary[1].length >= fence.length) fence = null;
      return line;
    }
    if (fence || /^ {4}|^\t|^\s{0,3}\[[^\]]+\]:/.test(line)) return line;
    const prefix = line.match(/^(?:\s{0,3}(?:#{1,6}\s+|>\s*|(?:[-+*]|\d+[.)])\s+))?(?:\[[ xX]\]\s+)?/)?.[0] ?? "";
    return prefix + inline(line.slice(prefix.length), selector);
  }).join("");
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const paths = process.argv.slice(2);
  const root = fileURLToPath(new URL("../", import.meta.url));
  for (const path of paths.length ? paths : ["README.md", ...documents.map(e => e[2])]) {
    const absolute = resolve(root, path);
    const source = readFileSync(absolute, "utf8");
    const encoded = markMarkdown(source);
    if (stripDemo(encoded) !== stripDemo(source)) throw new Error(`Visible content changed: ${path}`);
    if (stripDemo(marked.parse(encoded)) !== stripDemo(marked.parse(source))) throw new Error(`Markdown structure changed: ${path}`);
    writeFileSync(absolute, encoded);
  }
}
