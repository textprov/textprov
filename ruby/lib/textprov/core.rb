# ruby/lib/textprov/core.rb
#
# frozen_string_literal: true

require "cgi"
require "json"
require "set"

require_relative "grapheme"

module Textprov
  SPEC_VERSION = "0.2"
  UNICODE_VERSION = UCD::UNICODE_VERSION
  GENERATED_STATES = %w[human ai mixed].freeze
  PROPOSED_STATES  = %w[edited unknown].freeze

  MAPPING_PATH = File.expand_path("mapping.json", __dir__)

  module_function

  # Split `text` into extended grapheme clusters, the units a selector marks.
  def segments(text)
    Grapheme.segments(text)
  end

  class Mapping
    attr_reader :raw, :version, :selectors, :pua2base, :base2pua

    def initialize(raw:, version:, selectors:, pua2base:, base2pua:)
      @raw = raw
      @version = version
      @selectors = selectors
      @pua2base = pua2base
      @base2pua = base2pua
    end

    def self.load(path = MAPPING_PATH)
      raw = JSON.parse(File.read(path, encoding: "UTF-8"))
      selectors = {}
      raw["variation_selectors"].each do |name, value|
        selectors[name] = Integer(value.sub(/^U\+/, ""), 16)
      end
      pua2base = {}
      base2pua = {}
      raw["pua"].each do |pua_string, entry|
        pua  = Integer(pua_string.sub(/^U\+/, ""), 16)
        base = Integer(entry["base"].sub(/^U\+/, ""), 16)
        state = entry["provenance"] || "ai"
        pua2base[pua] = [base, state]
        base2pua[base] = pua if state == "ai"
      end
      new(raw: raw, version: raw["version"], selectors: selectors,
          pua2base: pua2base, base2pua: base2pua)
    end
  end

  @default_mapping = nil

  def default_mapping
    @default_mapping ||= Mapping.load
  end

  class << self
    attr_writer :default_mapping
  end

  # Whitespace only, by Unicode's White_Space property (Ruby's \\s is ASCII
  # only); matches Python's str.isspace and JavaScript's \\s.
  def blank?(text)
    text.match?(/\A[[:space:]]+\z/)
  end

  # `text` is a String; we work over its per-codepoint characters. Ruby's
  # String#chars yields one Unicode scalar per element, which is what the
  # Python port iterates.
  def _strip(text, selectors, pua2base)
    sel_cps = selectors.values.to_set
    out = String.new(encoding: "UTF-8")
    text.each_char do |char|
      cp = char.ord
      next if sel_cps.include?(cp)

      entry = pua2base[cp]
      out << (entry ? entry[0].chr(Encoding::UTF_8) : char)
    end
    out
  end

  # Implements the decoder algorithm in SPEC.md version 0.2: segment into
  # extended grapheme clusters, classify each cluster, then merge.
  def _runs(text, selectors, pua2base, strip: false, merge_whitespace: true)
    sel2name = selectors.each_with_object({}) { |(name, cp), h| h[cp] = name }
    items = []
    segments(text).each do |cluster|
      last = cluster[-1].ord
      state = nil
      out = cluster
      if sel2name.key?(last) && cluster.length > 1
        # Whitespace cannot carry a mark; a selector after it is inert.
        unless blank?(cluster[0...-1])
          state = sel2name[last]
          out = cluster[0...-1] if strip
        end
      elsif cluster.length == 1 && pua2base.key?(cluster.ord)
        base_cp, state = pua2base[cluster.ord]
        out = base_cp.chr(Encoding::UTF_8)
        out += selectors[state].chr(Encoding::UTF_8) unless strip
      elsif blank?(cluster)
        state = "ws"
      end
      if !items.empty? && items.last[0] == state
        items.last[1] << out
      else
        items << [state, out.dup]
      end
    end

    merged = []
    items.each_with_index do |(state, out), position|
      following = position + 1 < items.length ? items[position + 1][0] : nil
      if merge_whitespace && state == "ws" && !merged.empty? && merged.last[0] && merged.last[0] == following
        merged.last[1] << out
        next
      end
      state = nil if state == "ws"
      if !merged.empty? && merged.last[0] == state
        merged.last[1] << out
      else
        merged << [state, out.dup]
      end
    end
    merged.map { |state, out| [state, out] }
  end

  def _to_html(text, selectors, pua2base, strip: false, merge_whitespace: true,
               class_prefix: "prov")
    parts = []
    _runs(text, selectors, pua2base, strip: strip,
                                     merge_whitespace: merge_whitespace).each do |state, out|
      escaped = CGI.escapeHTML(out)
      if state
        parts << %(<span class="#{class_prefix} #{class_prefix}-#{state}" data-prov="#{state}">#{escaped}</span>)
      else
        parts << escaped
      end
    end
    parts.join
  end

  # Public API accepts either merge_whitespace (specification spelling) or
  # mergeWhitespace (camelCase alias per SPEC's cross-language rule).
  def runs(text, mapping: nil, strip: false, merge_whitespace: nil, mergeWhitespace: nil)
    mw = if merge_whitespace.nil?
           mergeWhitespace.nil? || mergeWhitespace
         else
           merge_whitespace
         end
    m = mapping || default_mapping
    _runs(text, m.selectors, m.pua2base, strip: strip, merge_whitespace: mw)
  end

  def to_html(text, mapping: nil, strip: false, merge_whitespace: nil, mergeWhitespace: nil,
              class_prefix: "prov")
    mw = if merge_whitespace.nil?
           mergeWhitespace.nil? || mergeWhitespace
         else
           merge_whitespace
         end
    m = mapping || default_mapping
    _to_html(text, m.selectors, m.pua2base, strip: strip, merge_whitespace: mw,
                                            class_prefix: class_prefix)
  end

  def strip_marks(text, mapping: nil)
    m = mapping || default_mapping
    _strip(text, m.selectors, m.pua2base)
  end
end
