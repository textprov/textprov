// Embed VS demo labels in HTML prose without changing markup or attributes.
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { markMarkdown } from "./mark-markdown.js";

const excluded = new Set(["head", "script", "style", "svg", "code", "pre", "button", "textarea"]);
const voidElements = new Set(["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"]);

export function markHtml(source) {
  const stack = [];
  return source.split(/(<!--[\s\S]*?-->|<![^>]*>|<\/?[a-z][^>"']*(?:(?:"[^"]*"|'[^']*')[^>"']*)*>)/gi).map(part => {
    if (part.startsWith("<")) {
      const tag = part.match(/^<(\/)?([a-z][\w:-]*)\b/i);
      if (tag) {
        const name = tag[2].toLowerCase();
        if (tag[1]) {
          const index = stack.lastIndexOf(name);
          if (index >= 0) stack.length = index;
        } else if (!voidElements.has(name) && !/\/\s*>$/.test(part)) stack.push(name);
      }
      return part;
    }
    if (!stack.some(name => name === "main" || name === "footer") || stack.some(name => excluded.has(name))) return part;
    return markMarkdown(part);
  }).join("");
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const path = fileURLToPath(new URL("./index.html", import.meta.url));
  writeFileSync(path, markHtml(readFileSync(path, "utf8")));
}
