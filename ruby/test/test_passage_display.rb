# frozen_string_literal: true
require_relative "test_helper"
require "cgi"

class TestPassageDisplay < Minitest::Test
  def projection(markup)
    stack = [nil]
    groups, characters = [], []
    markup.scan(/<span\b[^>]*>|<\/span>|[^<]+/).each do |token|
      if token.start_with?("<span")
        state = token[/\bdata-prov="([^"]+)"/, 1]
        stack << (state || stack.last)
        group = token[/\bdata-prov-passage="([^"]+)"/, 1]
        groups << group if group
      elsif token == "</span>"
        stack.pop
      else
        CGI.unescapeHTML(token).each_char { |char| characters << [char, stack.last] }
      end
    end
    [groups, characters]
  end

  def test_default_groups_partial_marks_and_keeps_the_exact_character_map
    source = "C#{AI}ho#{AI}ose a guide."
    expected = Textprov.runs(source, strip: true, merge_whitespace: false)
                       .flat_map { |state, text| text.each_char.map { |char| [char, state] } }
    groups, characters = projection(Textprov.to_html(source, strip: true))
    assert_equal ["ai"], groups
    assert_equal expected, characters
    assert_equal "C#{AI}ho#{AI}ose a guide.", source
  end

  def test_paragraph_boundaries_and_mixed_recorded_sources
    groups, = projection(Textprov.to_html("a#{AI} rest\n\nPlain.\n\nb#{HUMAN} end", class_prefix: "custom"))
    assert_equal %w[ai human], groups
    groups, characters = projection(Textprov.to_html("a#{AI} and b#{HUMAN}", strip: true))
    assert_equal ["mixed"], groups
    assert_equal %w[ai human], characters.map(&:last).compact
  end

  def test_exact_and_invalid_options
    source = "a#{AI} plain"
    refute_includes Textprov.to_html(source, display: "exact"), "data-prov-passage"
    assert_equal projection(Textprov.to_html(source)).last,
                 projection(Textprov.to_html(source, display: "exact")).last
    assert_equal [["a", "ai"], [" ", nil], ["b", "ai"]],
                 projection(Textprov.to_html("a#{AI} b#{AI}", strip: true, display: "exact")).last
    assert_raises(ArgumentError) { Textprov.to_html(source, display: "word") }
  end
end
