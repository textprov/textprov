# frozen_string_literal: true

require_relative "core"

module Textprov
  module_function

  def _mark(text, state, mode, selectors, pua2base, base2pua)
    sel_cps = selectors.values.to_set
    selector = selectors[state].chr(Encoding::UTF_8)
    chars = text.chars
    out = String.new(encoding: "UTF-8")
    index = 0
    while index < chars.length
      char = chars[index]
      cp = char.ord
      if sel_cps.include?(cp) || pua2base.key?(cp) || char.match?(/\s/)
        out << char
        index += 1
        next
      end
      start = index
      index = cluster_end(chars, index, sel_cps)
      cluster = chars[start...index]
      if index < chars.length && sel_cps.include?(chars[index].ord)
        cluster.each { |c| out << c }
        next
      end
      if mode == "pua" && state == "ai" && cluster.length == 1 && base2pua.key?(cp)
        out << base2pua[cp].chr(Encoding::UTF_8)
      else
        cluster.each { |c| out << c }
        out << selector
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
    chars = text.chars
    out = String.new(encoding: "UTF-8")
    if from_mode == "vs"
      index = 0
      while index < chars.length
        char = chars[index]
        index += 1
        if index < chars.length && chars[index].ord == vs_ai && base2pua.key?(char.ord)
          out << base2pua[char.ord].chr(Encoding::UTF_8)
          index += 1
        else
          out << char
        end
      end
      return out
    end
    chars.each do |char|
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
               "unknown" => 0, "edited" => 0, "mixed" => 0, "whitespace" => 0 }
    unrecognised_selectors = []
    unrecognised_pua = []
    sel_cp_set = selectors.values.to_set

    chars = text.chars
    index = 0
    while index < chars.length
      char = chars[index]
      cp = char.ord
      index += 1
      if sel2name.key?(cp)
        unrecognised_selectors << cp
        next
      end
      if cp.between?(0xE0100, 0xE01EF)
        unrecognised_selectors << cp
        next
      end
      if pua2base.key?(cp)
        counts["ai_pua"] += 1
        next
      end
      if cp.between?(0x100000, 0x10FFFD)
        unrecognised_pua << cp
        next
      end
      if char.match?(/\s/)
        counts["whitespace"] += 1
        next
      end
      index = cluster_end(chars, index - 1, sel_cp_set)
      if index < chars.length && sel_cp_set.include?(chars[index].ord)
        name = sel2name[chars[index].ord]
        index += 1
        key = name == "ai" ? "ai_vs" : name
        counts[key] += 1
      else
        counts["unmarked"] += 1
      end
    end

    lines = ["characters: #{chars.length}"]
    %w[unmarked human ai_vs ai_pua unknown edited mixed whitespace].each do |key|
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
