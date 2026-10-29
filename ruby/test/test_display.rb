# frozen_string_literal: true

require_relative "test_helper"
require "tmpdir"

class TestStylesheet < Minitest::Test
  def test_packaged_stylesheet_matches_canonical_browser_styles
    assert_equal File.read(File.join(ROOT, "js", "textprov.css"), encoding: "UTF-8"),
                 Textprov.stylesheet
  end

  def test_display_version_is_the_stylesheet_property_in_date_family_form
    version = Textprov.display_version
    assert_match(/\A\d{4}-\d{2}-\d{2}\.[a-z]+\z/, version)
    assert_includes Textprov.stylesheet, %(--prov-display-version: "#{version}";)
  end

  def test_stylesheet_does_not_depend_on_the_working_directory
    expected = Textprov.stylesheet
    Dir.mktmpdir do |directory|
      Dir.chdir(directory) { assert_equal expected, Textprov.stylesheet }
    end
  end
end
