# ruby/test/test_conformance.rb
#
# frozen_string_literal: true

require_relative "test_helper"
require "cgi"

class TestVendoredRegistry < Minitest::Test
  def test_vendored_copy_matches_canonical
    vendored  = File.binread(Textprov::MAPPING_PATH)
    canonical = File.binread(REGISTRY_PATH)

    assert_equal canonical, vendored
  end

  def test_pua_rule_holds_for_every_entry
    PUA2BASE.each do |pua, (base, state)|
      assert_equal base, pua - 0x100000, format("U+%06X", pua)
      assert_equal "ai", state, format("U+%06X", pua)
    end
  end
end

class TestObsoleteSelectors < Minitest::Test
  def test_only_human_and_ai_states_are_exposed
    assert_equal %w[human ai], Textprov::GENERATED_STATES
    assert_equal %w[human ai], SELECTORS.keys
    refute Textprov.const_defined?(:PROPOSED_STATES)
  end

  def test_obsolete_selectors_are_preserved_as_ordinary_text
    (0xE0102..0xE0104).each do |cp|
      selector = cp.chr(Encoding::UTF_8)
      [selector, "a#{selector}", " #{selector}", "a#{AI}#{selector}", "a#{selector}#{AI}"].each do |text|
        assert_equal text.delete(AI), Textprov.strip_marks(text)
        [false, true].each do |strip|
          state = text.end_with?(AI) ? "ai" : nil
          expected = strip && state ? text[0...-1] : text
          assert_equal [[state, expected]], Textprov.runs(text, strip: strip)
          rendered = state ? span(state, expected) : expected
          assert_equal rendered, Textprov.to_html(text, strip: strip)
        end
        [["vs", "pua"], ["pua", "vs"]].each do |from_mode, to_mode|
          expected = from_mode == "vs" ? text.gsub("a#{AI}", MAPPING.base2pua["a".ord].chr(Encoding::UTF_8)) : text
          assert_equal expected, Textprov.convert(text, from_mode, to_mode)
        end
      end
    end
  end

  def test_inspect_does_not_report_obsolete_states
    report = Textprov.inspect_text("a\u{E0102}b\u{E0103}c\u{E0104}")
    assert_includes report, "unmarked: 3\n"
    %w[mixed edited unknown].each { |state| refute_includes report, "#{state}:" }
    assert_includes Textprov.inspect_text("\u{E0102}\n\u{E0103}\n\u{E0104}"),
                    "unrecognised_selectors: U+E0102 U+E0103 U+E0104"
  end
end

class TestFixtures < Minitest::Test
  FX = JSON.parse(File.read(FIXTURES_PATH, encoding: "UTF-8"))

  def test_versions_match_the_implementation
    assert_equal FX["spec_version"], Textprov::SPEC_VERSION
    assert_equal FX["registry_version"], MAPPING.version
  end

  def test_every_case
    FX["cases"].each do |c|
      options = c["options"] || {}
      kwargs = {}
      kwargs[:strip] = options["strip"] if options.key?("strip")
      kwargs[:merge_whitespace] = options["merge_whitespace"] if options.key?("merge_whitespace")
      got = Textprov.runs(c["input"], **kwargs)
      want = c["runs"].map { |r| [r["state"], r["text"]] }

      assert_equal want, got, "case #{c["name"].inspect}"
    end
  end
end

class TestSegments < Minitest::Test
  JAMO = "\u1100\u1161\u11A8"
  CONJUNCT = "\u0915\u094D\u0937"
  TAG_FLAG = "\u{1F3F4}\u{E0067}\u{E0062}\u{E0065}\u{E006E}\u{E0067}\u{E007F}"
  SARA_AM = "\u0E19\u0E33"

  def test_ascii
    assert_equal %w[a b c], Textprov.segments("abc")
  end

  def test_combining_marks
    assert_equal %w[é x], Textprov.segments("éx")
    assert_equal %w[é̂ x], Textprov.segments("é̂x")
  end

  def test_zwj_sequence
    assert_equal [FAMILY, "x"], Textprov.segments("#{FAMILY}x")
  end

  def test_skin_tone
    assert_equal [TONE, "x"], Textprov.segments("#{TONE}x")
  end

  def test_regional_indicators_pair_up
    assert_equal [FLAG, "\u{1F1E8}"], Textprov.segments("#{FLAG}\u{1F1E8}")
  end

  def test_emoji_variation_selectors
    assert_equal ["❤️", "x"], Textprov.segments("❤️x")
    assert_equal ["❤︎", "x"], Textprov.segments("❤︎x")
  end

  def test_provenance_selector_extends_the_cluster
    assert_equal [AI, "x"], Textprov.segments("#{AI}x")
    assert_equal ["a#{AI}", "b"], Textprov.segments("a#{AI}b")
    assert_equal ["#{FAMILY}#{AI}", "b"], Textprov.segments("#{FAMILY}#{AI}b")
  end

  def test_clusters_the_approximation_used_to_split
    [JAMO, CONJUNCT, TAG_FLAG, SARA_AM].each do |text|
      assert_equal [text], Textprov.segments(text)
      assert_equal ["#{text}#{AI}"], Textprov.segments("#{text}#{AI}")
    end
  end

  def test_empty
    assert_equal [], Textprov.segments("")
  end

  def test_unicode_version_matches_the_test_file
    first = File.open(GRAPHEME_TEST_PATH, encoding: "UTF-8", &:readline)

    assert_includes first, "GraphemeBreakTest-#{Textprov::UNICODE_VERSION}.txt"
  end

  # Every line of Unicode's GraphemeBreakTest.txt for the pinned version.
  # "÷" marks a boundary and "×" its absence; text after "#" is a comment.
  def test_grapheme_break_test
    total = 0
    File.foreach(GRAPHEME_TEST_PATH, encoding: "UTF-8") do |line|
      body = line.split("#")[0].strip
      next if body.empty?

      expected = []
      current = +""
      body.split[1..].each do |token|
        if token == "÷"
          expected << current
          current = +""
        elsif token != "×"
          current << token.to_i(16).chr(Encoding::UTF_8)
        end
      end

      assert_equal expected, Textprov.segments(expected.join), body
      total += 1
    end

    assert_operator total, :>, 700
  end
end

class TestToHtml < Minitest::Test
  def test_empty_and_plain
    assert_equal "", Textprov.to_html("")
    assert_equal "plain", Textprov.to_html("plain")
  end

  def test_span_shape
    assert_equal span("ai", "a#{AI}"), Textprov.to_html("a#{AI}")
  end

  def test_escaping
    assert_equal "&lt;&amp;&quot;", Textprov.to_html(%(<&"))
    assert_equal(
      span("ai", "&lt;#{AI}&amp;#{AI}&quot;#{AI}"),
      Textprov.to_html("<#{AI}&#{AI}\"#{AI}")
    )
    assert_equal(
      "#{span("ai", "a#{AI}")}&lt;b#{span("human", "&gt;#{HUMAN}")} &amp; x",
      Textprov.to_html("a#{AI}<b>#{HUMAN} & x")
    )
  end

  def test_class_prefix
    out = Textprov.to_html("a#{AI}", class_prefix: "x")

    assert_equal span("ai", "a#{AI}", prefix: "x"), out
    assert_includes out, 'data-prov="ai"'
  end

  def test_merge_whitespace
    assert_equal span("ai", "a#{AI} b#{AI}"), Textprov.to_html("a#{AI} b#{AI}")
    assert_equal(
      "#{span("ai", "a#{AI}")} #{span("ai", "b#{AI}")}",
      Textprov.to_html("a#{AI} b#{AI}", merge_whitespace: false)
    )
  end

  def test_merge_whitespace_camelcase_alias
    assert_equal(
      "#{span("ai", "a#{AI}")} #{span("ai", "b#{AI}")}",
      Textprov.to_html("a#{AI} b#{AI}", mergeWhitespace: false)
    )
  end

  def test_strip
    assert_equal span("ai", "a b"), Textprov.to_html("a#{AI} b#{AI}", strip: true)
  end

  def test_pua_input
    pua_cp, (pua_base, pua_state) = PUA2BASE.find { |_, entry| entry[1] == "ai" }

    assert_equal "ai", pua_state
    assert_equal span("ai", pua_base.chr(Encoding::UTF_8) + AI),
                 Textprov.to_html(pua_cp.chr(Encoding::UTF_8))
    assert_equal span("ai", pua_base.chr(Encoding::UTF_8)),
                 Textprov.to_html(pua_cp.chr(Encoding::UTF_8), strip: true)
  end

  def test_span_text_reproduces_the_input
    source = "x<y#{AI} & #{FAMILY}#{HUMAN}\n\"z\""
    rendered = Textprov.to_html(source)
    [span("ai", ""), span("human", "")].each do |tag|
      open_tag = tag.sub("</span>", "")
      rendered = rendered.sub(open_tag, "") while rendered.include?(open_tag)
    end

    assert_equal source, CGI.unescapeHTML(rendered.gsub("</span>", ""))
  end
end

class TestStripMarks < Minitest::Test
  def test_selectors_and_pua_are_removed
    pua_cp, (pua_base,) = PUA2BASE.first

    assert_equal "ab", Textprov.strip_marks("a#{AI}b#{HUMAN}")
    assert_equal pua_base.chr(Encoding::UTF_8), Textprov.strip_marks(pua_cp.chr(Encoding::UTF_8))
  end
end

class TestExplicitMapping < Minitest::Test
  def test_mapping_argument
    mapping = Textprov::Mapping.load(REGISTRY_PATH)

    assert_equal MAPPING.version, mapping.version
    assert_equal Textprov.runs("a#{AI}"), Textprov.runs("a#{AI}", mapping: mapping)
    assert_equal(
      Textprov.runs("a#{AI}"),
      Textprov._runs("a#{AI}", mapping.selectors, mapping.pua2base, strip: false,
                                                                    merge_whitespace: true)
    )
    assert_equal(
      Textprov.to_html("a#{AI}"),
      Textprov._to_html("a#{AI}", mapping.selectors, mapping.pua2base,
                        strip: false, merge_whitespace: true, class_prefix: "prov")
    )
  end
end
