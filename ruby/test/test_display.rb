# frozen_string_literal: true

require_relative "test_helper"
require "tmpdir"

class TestStylesheet < Minitest::Test
  def test_packaged_stylesheet_matches_canonical_browser_styles
    assert_equal File.read(File.join(ROOT, "js", "textprov.css"), encoding: "UTF-8"),
                 Textprov.stylesheet
  end

  def test_stylesheet_does_not_depend_on_the_working_directory
    expected = Textprov.stylesheet
    Dir.mktmpdir do |directory|
      Dir.chdir(directory) { assert_equal expected, Textprov.stylesheet }
    end
  end
end
