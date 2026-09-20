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

class TestFixtures < Minitest::Test
  FX = JSON.parse(File.read(FIXTURES_PATH, encoding: "UTF-8"))

  def test_versions_match_the_implementation
    assert_equal FX["contract_version"], Textprov::CONTRACT_VERSION
    assert_equal FX["mapping_version"], MAPPING.version
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

class TestClusterEnd < Minitest::Test
  def cluster(text, start = 0)
    Textprov.cluster_end(text.chars, start, SELECTORS.values.to_set)
  end

  def test_ascii
    assert_equal 1, cluster("abc")
    assert_equal 2, cluster("abc", 1)
  end

  def test_combining_marks
    assert_equal 2, cluster("éx")
    assert_equal 3, cluster("é̂x")
  end

  def test_zwj_sequence
    assert_equal 5, cluster("#{FAMILY}x")
    assert_equal 5, cluster(FAMILY)
  end

  def test_skin_tone
    assert_equal 2, cluster("#{TONE}x")
  end

  def test_regional_indicators
    assert_equal 2, cluster("#{FLAG}\u{1F1E8}")
    assert_equal 1, cluster("\u{1F1E8}x")
  end

  def test_emoji_variation_selectors
    assert_equal 2, cluster("❤️x")
    assert_equal 2, cluster("❤︎x")
  end

  def test_provenance_selector_ends_the_cluster
    assert_equal 1, cluster("#{AI}x")
    assert_equal 1, cluster("a#{AI}b")
    assert_equal 2, cluster("é#{AI}b")
    assert_equal 5, cluster("#{FAMILY}#{AI}b")
  end

  def test_is_combining
    assert Textprov.is_combining("́")
    refute Textprov.is_combining("a")
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
