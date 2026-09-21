// js/textprov.js

/*
 * textprov.js: client-side provenance decorator
 * TextProv protocol: https://github.com/textprov/textprov
 *
 * Specification version 0.1 (see ../SPEC.md).
 * Registry version 0.1 (see ../mapping.json; the registry is embedded below as
 * SELECTORS and PUA_RANGES and is never loaded at runtime).
 *
 * Renders in-band provenance marks (selector or PUA encoding) as HTML spans
 * carrying a class and a data-prov attribute. No font is required to see the
 * marks; see textprov.css for optional visual styles.
 *
 * Usage:
 *   <script src="textprov.js"></script>
 *   <script>textprov.render(document.body);</script>
 *
 * Options (all optional, passed to both runs() and render()):
 *   strip           default false  Remove selectors from run text; state is
 *                                  still reported via data-prov.
 *   merge_whitespace default true  Whitespace between two runs of the same
 *                                  state joins them into one run. This is the
 *                                  specification spelling; mergeWhitespace is an
 *                                  accepted alias.
 *   prefix          default "prov" Class prefix, e.g. "prov" -> "prov prov-STATE".
 */
(function (global) {
  "use strict";

  // Tables from mapping.json. The registry is not loaded at runtime; these
  // constants are checked against it by check_fixtures.mjs.
  var REGISTRY_VERSION = "0.1";
  var SELECTORS = {
    human: 0xe0100,
    ai: 0xe0101,
    mixed: 0xe0102,
    edited: 0xe0103,
    unknown: 0xe0104,
  };
  var PUA_AI = 0x100000; // ai plane: PUA_AI(cp) = 0x100000 + cp
  // Allocated PUA code points, inclusive ranges. Anything else in the plane is
  // not a mark. v1: U+0021-U+00FF minus Zs, Cc, Cf; every entry is state ai.
  var PUA_RANGES = [
    [0x100021, 0x10007e],
    [0x1000a1, 0x1000ac],
    [0x1000ae, 0x1000ff],
  ];
  var VS = {};
  for (var selName in SELECTORS) VS[SELECTORS[selName]] = selName;
  function inPua(cp) {
    for (var i = 0; i < PUA_RANGES.length; i++) {
      if (cp >= PUA_RANGES[i][0] && cp <= PUA_RANGES[i][1]) return true;
    }
    return false;
  }
  var seg = new Intl.Segmenter(undefined, { granularity: "grapheme" });

  function resolveOptions(opts) {
    opts = opts || {};
    var merge = opts.merge_whitespace !== undefined ? opts.merge_whitespace : opts.mergeWhitespace;
    return {
      strip: !!opts.strip,
      mergeWhitespace: merge !== false,
      prefix: typeof opts.prefix === "string" && opts.prefix.length ? opts.prefix : "prov",
    };
  }

  // text -> [{state, text}], whitespace between equal states is absorbed
  // (unless mergeWhitespace is false).
  function runs(text, opts) {
    var o = resolveOptions(opts);
    var items = [];
    var iter = seg.segment(text);
    var it, done;
    for (it = iter[Symbol.iterator](); !(done = it.next()).done;) {
      var segment = done.value.segment;
      var cps = Array.from(segment);
      var last = cps[cps.length - 1].codePointAt(0);
      var cp0 = cps[0].codePointAt(0);
      var state = null,
        out = segment;
      if (VS[last] !== undefined && cps.length > 1) {
        state = VS[last];
        if (o.strip) out = cps.slice(0, -1).join("");
      } else if (cps.length === 1 && inPua(cp0)) {
        state = "ai";
        // PUA is unreadable without the font; re-emit as base + selector encoding.
        out =
          String.fromCodePoint(cp0 - PUA_AI) + (o.strip ? "" : String.fromCodePoint(SELECTORS.ai));
      } else if (/^\s+$/.test(segment)) {
        state = "ws";
      }
      var prev = items[items.length - 1];
      if (prev && prev.state === state) prev.text += out;
      else items.push({ state: state, text: out });
    }
    // absorb whitespace between two runs of the same non-null state
    var merged = [];
    for (var i = 0; i < items.length; i++) {
      var cur = items[i],
        mp = merged[merged.length - 1],
        next = items[i + 1];
      if (cur.state === "ws") {
        if (o.mergeWhitespace && mp && next && mp.state === next.state && mp.state) {
          mp.text += cur.text;
          continue;
        }
        cur.state = null;
      }
      if (mp && mp.state === cur.state) mp.text += cur.text;
      else merged.push(cur);
    }
    return merged;
  }

  function render(root, opts) {
    var o = resolveOptions(opts);
    root = root || document.body;
    var provClass = o.prefix;
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        return /[\u{E0100}-\u{E0104}\u{100000}-\u{10FFFF}]/u.test(n.nodeValue) &&
          !n.parentNode.closest("script,style,textarea,." + provClass)
          ? NodeFilter.FILTER_ACCEPT
          : NodeFilter.FILTER_REJECT;
      },
    });
    var nodes = [];
    var n;
    while ((n = walker.nextNode())) nodes.push(n);
    var count = 0;
    for (var i = 0; i < nodes.length; i++) {
      var node = nodes[i];
      var frag = document.createDocumentFragment();
      var rs = runs(node.nodeValue, o);
      for (var j = 0; j < rs.length; j++) {
        var r = rs[j];
        if (!r.state) {
          frag.appendChild(document.createTextNode(r.text));
          continue;
        }
        var span = document.createElement("span");
        span.className = provClass + " " + provClass + "-" + r.state;
        span.dataset.prov = r.state;
        span.textContent = r.text;
        frag.appendChild(span);
        count++;
      }
      node.parentNode.replaceChild(frag, node);
    }
    return count;
  }

  var textprov = {
    runs: runs,
    render: render,
    specVersion: "0.1",
    registryVersion: REGISTRY_VERSION,
    mapping: { version: REGISTRY_VERSION, selectors: SELECTORS, puaRanges: PUA_RANGES },
  };

  if (typeof module === "object" && module.exports) {
    module.exports = textprov;
  } else {
    global.textprov = textprov;
  }
})(typeof window !== "undefined" ? window : this);
