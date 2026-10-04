import textprov from "textprov";
import { initProvenanceDisplay } from "./provenance.js";

function localStorageOrNull() {
  try {
    return window.localStorage;
  } catch (error) {
    return null;
  }
}

initProvenanceDisplay({ document, textprov, storage: localStorageOrNull() });
