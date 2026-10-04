# ruby/lib/textprov/grapheme.rb
#
# frozen_string_literal: true

require_relative "ucd"

module Textprov
  # Extended grapheme cluster segmentation (UAX #29).
  #
  # The segmenter reads the property tables in ucd.rb, generated from one
  # pinned Unicode version, instead of the Unicode version Onigmo ships with
  # the interpreter. Every port segments from the same tables, so a cluster
  # marked by one decodes as one cluster in the others. Rule numbers below
  # refer to UAX #29, Grapheme Cluster Boundary Rules.
  module Grapheme
    CR = UCD::GCB["CR"]
    LF = UCD::GCB["LF"]
    CONTROL = UCD::GCB["Control"]
    EXTEND = UCD::GCB["Extend"]
    ZWJ = UCD::GCB["ZWJ"]
    RI = UCD::GCB["Regional_Indicator"]
    PREPEND = UCD::GCB["Prepend"]
    SPACING_MARK = UCD::GCB["SpacingMark"]
    L = UCD::GCB["L"]
    V = UCD::GCB["V"]
    T = UCD::GCB["T"]
    LV = UCD::GCB["LV"]
    LVT = UCD::GCB["LVT"]
    CONTROL_LIKE = [CONTROL, CR, LF].freeze
    AFTER_L = [L, V, LV, LVT].freeze
    BEFORE_V = [LV, V].freeze
    V_OR_T = [V, T].freeze
    BEFORE_T = [LVT, T].freeze
    EXTENDING = [EXTEND, ZWJ, SPACING_MARK].freeze
    CONSONANT = UCD::INCB["Consonant"]
    LINKER = UCD::INCB["Linker"]
    INCB_EXTEND = UCD::INCB["Extend"]
    EXTENDED_PICTOGRAPHIC = UCD::EXTENDED_PICTOGRAPHIC
    GCB_MASK = 15
    INCB_MASK = 224

    # The look-behind a boundary decision needs beyond the previous code
    # point: how many regional indicators precede it, whether an emoji ZWJ
    # sequence is open (GB11), and whether an Indic conjunct is open (GB9c).
    State = Struct.new(:regional_run, :pictograph, :conjunct)

    module_function

    # The property byte for one code point.
    def property(codepoint)
      index = UCD::BOUNDS.bsearch_index { |bound| bound > codepoint }
      UCD::CODES[index ? index - 1 : -1]
    end

    # GB4 forces a break after these code points, even before Extend.
    def control_like?(codepoint)
      CONTROL_LIKE.include?(property(codepoint) & GCB_MASK)
    end

    # Split `text` into extended grapheme clusters.
    def segments(text)
      clusters = []
      return clusters if text.empty?

      chars = text.chars
      current = chars[0].dup
      previous = property(chars[0].ord)
      state = advance(State.new(0, 0, 0), previous)
      chars[1..].each do |character|
        following = property(character.ord)
        if join?(previous, following, state)
          current << character
        else
          clusters << current
          current = character.dup
        end
        state = advance(state, following)
        previous = following
      end
      clusters << current
      clusters
    end

    # Is there no boundary between a code point with property byte `previous`
    # and one with `following`? One guard per rule, in rule order.
    def join?(previous, following, state) # rubocop:disable Metrics/CyclomaticComplexity, Metrics/PerceivedComplexity
      before = previous & GCB_MASK
      after = following & GCB_MASK
      return true if before == CR && after == LF # GB3
      return false if CONTROL_LIKE.include?(before) || CONTROL_LIKE.include?(after) # GB4, GB5
      return true if before == L && AFTER_L.include?(after) # GB6
      return true if BEFORE_V.include?(before) && V_OR_T.include?(after) # GB7
      return true if BEFORE_T.include?(before) && after == T # GB8
      return true if EXTENDING.include?(after) # GB9, GB9a
      return true if before == PREPEND # GB9b
      return true if state.conjunct == 2 && (following & INCB_MASK) == CONSONANT # GB9c
      return true if state.pictograph == 2 && following.anybits?(EXTENDED_PICTOGRAPHIC) # GB11
      return state.regional_run.odd? if before == RI && after == RI # GB12, GB13

      false # GB999
    end

    # The state after consuming a code point with property byte `following`.
    def advance(state, following)
      gcb = following & GCB_MASK
      regional_run = gcb == RI ? state.regional_run + 1 : 0
      # 0: nothing; 1: Extended_Pictographic Extend*; 2: that followed by ZWJ.
      open = state.pictograph == 1
      pictograph =
        if following.anybits?(EXTENDED_PICTOGRAPHIC) || (open && gcb == EXTEND) then 1
        elsif open && gcb == ZWJ then 2
        else 0
        end
      # 0: nothing; 1: Consonant (Extend|Linker)* without a Linker yet;
      # 2: Consonant ... Linker (Extend|Linker)*.
      incb = following & INCB_MASK
      conjunct = conjunct_after(state.conjunct, incb)
      State.new(regional_run, pictograph, conjunct)
    end

    def conjunct_after(conjunct, incb)
      return 1 if incb == CONSONANT
      return 0 if conjunct.zero?
      return 2 if incb == LINKER

      incb == INCB_EXTEND ? conjunct : 0
    end
  end
end
