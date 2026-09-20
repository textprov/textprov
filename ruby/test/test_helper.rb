# frozen_string_literal: true

$LOAD_PATH.unshift File.expand_path("../lib", __dir__)

require "minitest/autorun"
require "json"
require "textprov"

ROOT = File.expand_path("../..", __dir__)
FIXTURES_PATH = File.join(ROOT, "fixtures.json")
REGISTRY_PATH = File.join(ROOT, "mapping.json")

MAPPING   = Textprov.default_mapping
SELECTORS = MAPPING.selectors
PUA2BASE  = MAPPING.pua2base
AI    = SELECTORS["ai"].chr(Encoding::UTF_8)
HUMAN = SELECTORS["human"].chr(Encoding::UTF_8)

FLAG   = "\u{1F1E8}\u{1F1E6}"
FAMILY = "\u{1F468}‍\u{1F469}‍\u{1F467}"
TONE   = "\u{1F44D}\u{1F3FD}"

def span(state, text, prefix: "prov")
  %(<span class="#{prefix} #{prefix}-#{state}" data-prov="#{state}">#{text}</span>)
end
