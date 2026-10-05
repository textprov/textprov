import textprov from "textprov";
import { initProvenanceDisplay } from "./provenance.js";

const passage = document.getElementById("sample-passage");
// Save the original code-point sequence before the display decorator runs.
const sampleText = passage?.textContent;
let storage = null;
try { storage = window.localStorage; } catch { /* A page-local preference still works. */ }
initProvenanceDisplay({ document, textprov, storage });

const copyButton = document.getElementById("sample-copy-button");
if (copyButton && passage && navigator.clipboard?.writeText) {
  copyButton.hidden = false;
  copyButton.addEventListener("click", async () => {
    const status = document.getElementById("sample-copy-status");
    try {
      await navigator.clipboard.writeText(sampleText);
      status.textContent = "Copied with experimental VS marks.";
    } catch {
      status.textContent = "Select the example and copy it with your keyboard.";
    }
  });
}
