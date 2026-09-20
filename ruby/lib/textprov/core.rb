# ruby/lib/textprov/core.rb
#
# frozen_string_literal: true

require "cgi"
require "json"

module Textprov
  CONTRACT_VERSION = 1
  GENERATED_STATES = %w[human ai mixed].freeze
  PROPOSED_STATES  = %w[edited unknown].freeze

  MAPPING_PATH = File.expand_path("mapping.json", __dir__)

  ZWJ  = 0x200D
  VS15 = 0xFE0E
  VS16 = 0xFE0F
  SKIN_TONES = (0x1F3FB..0x1F3FF)
  REGIONAL   = (0x1F1E6..0x1F1FF)

  # Categories Mn/Mc/Me: extracted from Unicode data. Ruby's regexp \p{Mn} etc.
  # covers this; using a regex avoids shipping our own category table.
  COMBINING_RE = /[\p{Mn}\p{Mc}\p{Me}]/

  module_function

  def is_combining(char)
    !!(char =~ COMBINING_RE)
  end

  # A cluster is a base character plus everything that visually belongs to it:
  # combining marks, VS15/VS16, skin-tone modifiers, ZWJ joins, and the second
  # half of a regional-indicator pair. A provenance selector always ends the
  # cluster.
  def cluster_end(chars, start, sel_cps)
    index = start + 1
    if REGIONAL.include?(chars[start].ord) &&
       index < chars.length &&
       REGIONAL.include?(chars[index].ord)
      index += 1
    end
    while index < chars.length
      cp = chars[index].ord
      break if sel_cps.include?(cp)

      if cp == ZWJ
        index += (index + 1 < chars.length ? 2 : 1)
        next
      end
      if cp == VS15 || cp == VS16 || SKIN_TONES.include?(cp) || is_combining(chars[index])
        index += 1
        next
      end
      break
    end
    index
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

  def _runs(text, selectors, pua2base, strip: false, merge_whitespace: true)
    sel_cps = selectors.values.to_set
    sel2name = selectors.each_with_object({}) { |(name, cp), h| h[cp] = name }
    chars = text.chars
    items = []
    index = 0
    while index < chars.length
      char = chars[index]
      cp = char.ord
      if pua2base.key?(cp)
        base_cp, state = pua2base[cp]
        out = strip ? base_cp.chr(Encoding::UTF_8) : base_cp.chr(Encoding::UTF_8) + selectors[state].chr(Encoding::UTF_8)
        index += 1
      elsif char.match?(/\s/)
        state = "ws"
        out = char
        index += 1
      else
        endi = cluster_end(chars, index, sel_cps)
        cluster = chars[index...endi].join
        state = nil
        out = cluster
        index = endi
        if index < chars.length && sel_cps.include?(chars[index].ord)
          state = sel2name[chars[index].ord]
          out += chars[index] unless strip
          index += 1
        end
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

  # Public API accepts either merge_whitespace (contract spelling) or
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
