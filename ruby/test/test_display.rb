# frozen_string_literal: true

require_relative "test_helper"
require "tmpdir"

class TestStylesheet < Minitest::Test
  def test_packaged_stylesheet_matches_canonical_browser_styles
    assert_equal File.read(File.join(ROOT, "js", "textprov.css"), encoding: "UTF-8"),
                 Textprov.stylesheet
  end

  def test_display_version_is_the_spec_version_then_the_family
    version = Textprov.display_version
    assert_match(/\Av\d+\.\d+\.\d+-[a-z]+\z/, version)
    assert version.end_with?("-#{Textprov.display_family}")
    refute_equal "v#{Textprov::SPEC_VERSION}", version.split("-").first
    assert_includes Textprov.stylesheet, %(--prov-display-version: "#{version}";)
  end

  def test_candidate_versions_sit_behind_the_root_attribute
    css = Textprov.stylesheet
    declared = css.scan(/--prov-display-version:\s*"([^"]+)"/).flatten
    assert_equal Textprov.display_version, declared.first
    assert_operator declared.length, :>, 1
    declared.drop(1).each do |candidate|
      refute_equal Textprov.display_version, candidate
      assert_match(/\Av\d+\.\d+\.\d+-[a-z]+\z/, candidate)
      assert_includes css, %(:root[data-prov-display-version="#{candidate}"] {\n  --prov-display-version: "#{candidate}";)
    end
    refute_includes css, %([data-prov-display-version="#{Textprov.display_version}"])
  end

  def test_stylesheet_does_not_depend_on_the_working_directory
    expected = Textprov.stylesheet
    Dir.mktmpdir do |directory|
      Dir.chdir(directory) { assert_equal expected, Textprov.stylesheet }
    end
  end
end
