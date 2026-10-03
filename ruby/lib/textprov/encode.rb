# ruby/lib/textprov/encode.rb
#
# frozen_string_literal: true

require_relative "core"

module Textprov
  module_function

  # Attach the selector for `state` after every markable cluster. Whitespace,
  # control-break clusters, clusters ending in a provenance selector, lone selectors, and
  # PUA provenance characters are left alone, so the operation is idempotent.
  def _mark(text, state, mode, selectors, pua2base, base2pua)
    raise ArgumentError, "invalid provenance state: #{state.inspect}" unless GENERATED_STATES.include?(state)

    sel_cps = selectors.values.to_set
    selector = selectors[state].chr(Encoding::UTF_8)
    out = String.new(encoding: "UTF-8")
    segments(text).each do |cluster|
      first = cluster[0].ord
      last = cluster[-1].ord
      single = cluster.length == 1
      if sel_cps.include?(last) || (single && pua2base.key?(first)) || blank?(cluster) ||
         Grapheme.control_like?(last)
        out << cluster
      elsif mode == "pua" && state == "ai" && single && base2pua.key?(first)
        out << base2pua[first].chr(Encoding::UTF_8)
      else
        out << cluster << selector
      end
    end
    out
  end

  # `old_text` and `new_text` are code-point-wise compared via chars, matching
  # the Python impl (Python indexes by code point).
  def _mark_added(old_text, new_text, state, mode, selectors, pua2base, base2pua)
    return _mark(new_text, state, mode, selectors, pua2base, base2pua) if old_text.empty?

    old_chars = old_text.chars
    new_chars = new_text.chars
    pre = 0
    while pre < [old_chars.length, new_chars.length].min && old_chars[pre] == new_chars[pre]
      pre += 1
    end
    suf = 0
    while suf < [old_chars.length,
                 new_chars.length].min - pre && old_chars[-1 - suf] == new_chars[-1 - suf]
      suf += 1
    end
    endi = new_chars.length - suf
    middle = new_chars[pre...endi].join
    middle_marked = _mark(middle, state, mode, selectors, pua2base, base2pua)
    new_chars[0...pre].join + middle_marked + new_chars[endi...new_chars.length].join
  end

  def _convert(text, from_mode, to_mode, selectors, pua2base, base2pua)
    return text if from_mode == to_mode

    vs_ai = selectors["ai"]
    out = String.new(encoding: "UTF-8")
    if from_mode == "vs"
      # Per cluster, not per code point: a base that shares its cluster with
      # anything but its own selector has no PUA counterpart.
      segments(text).each do |cluster|
        if cluster.length == 2 && cluster[1].ord == vs_ai && base2pua.key?(cluster[0].ord)
          out << base2pua[cluster[0].ord].chr(Encoding::UTF_8)
        else
          out << cluster
        end
      end
      return out
    end
    text.each_char do |char|
      entry = pua2base[char.ord]
      if entry && entry[1] == "ai"
        out << entry[0].chr(Encoding::UTF_8)
        out << vs_ai.chr(Encoding::UTF_8)
      else
        out << char
      end
    end
    out
  end

  def _inspect(text, selectors, pua2base)
    sel2name = selectors.each_with_object({}) { |(name, cp), h| h[cp] = name }
    counts = { "unmarked" => 0, "human" => 0, "ai_vs" => 0, "ai_pua" => 0,
               "whitespace" => 0 }
    unrecognised_selectors = []
    unrecognised_pua = []

    chars = text.chars
    segments(text).each do |cluster|
      cp = cluster[0].ord
      last = cluster[-1].ord
      if cluster.length == 1
        if sel2name.key?(cp) || cp.between?(0xE0100, 0xE01EF)
          unrecognised_selectors << cp # a selector with no base in front of it
        elsif pua2base.key?(cp)
          counts["ai_pua"] += 1
        elsif cp.between?(0x100000, 0x10FFFD)
          unrecognised_pua << cp
        elsif blank?(cluster)
          counts["whitespace"] += 1
        else
          counts["unmarked"] += 1
        end
      elsif sel2name.key?(last) && blank?(cluster[0...-1])
        counts["whitespace"] += 1 # whitespace cannot carry a mark
        unrecognised_selectors << last
      elsif sel2name.key?(last)
        name = sel2name[last]
        counts[name == "ai" ? "ai_vs" : name] += 1
      elsif blank?(cluster)
        counts["whitespace"] += 1
      else
        counts["unmarked"] += 1
      end
    end

    lines = ["characters: #{chars.length}"]
    %w[unmarked human ai_vs ai_pua whitespace].each do |key|
      lines << "#{key}: #{counts[key]}"
    end
    sels = unrecognised_selectors.uniq.sort.map { |cp| format("U+%04X", cp) }.join(" ")
    puas = unrecognised_pua.uniq.sort.map { |cp| format("U+%04X", cp) }.join(" ")
    lines << "unrecognised_selectors: #{sels.empty? ? "-" : sels}"
    lines << "unrecognised_pua: #{puas.empty? ? "-" : puas}"
    "#{lines.join("\n")}\n"
  end

  def mark(text, state: "ai", mode: "vs", mapping: nil)
    m = mapping || default_mapping
    _mark(text, state, mode, m.selectors, m.pua2base, m.base2pua)
  end

  def mark_added(old_text, new_text, state: "ai", mode: "vs", mapping: nil)
    m = mapping || default_mapping
    _mark_added(old_text, new_text, state, mode, m.selectors, m.pua2base, m.base2pua)
  end

  def convert(text, from_mode, to_mode, mapping: nil)
    m = mapping || default_mapping
    _convert(text, from_mode, to_mode, m.selectors, m.pua2base, m.base2pua)
  end

  # Named inspect_text to avoid shadowing Kernel#inspect / Object#inspect.
  def inspect_text(text, mapping: nil)
    m = mapping || default_mapping
    _inspect(text, m.selectors, m.pua2base)
  end
end
