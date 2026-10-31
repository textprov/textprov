# frozen_string_literal: true

module Textprov
  module_function

  DISPLAY_VERSION_PROPERTY = /--prov-display-version:\s*"([^"]+)"/

  # Return the shared gradient-mist and dotted-underline CSS as UTF-8 text.
  def stylesheet
    File.read(File.join(__dir__, "textprov.css"), encoding: "UTF-8")
  end

  # Return the reveal treatment version, "v<spec version>-<family>", read from
  # the first --prov-display-version in the packaged stylesheet (its single
  # source; a candidate declares its own only behind the data-prov-display-version
  # root attribute). The prefix is the spec (proposal) version, not the 0.2
  # baseline experiment identifier in SPEC_VERSION and not this gem's version.
  # Scheme: docs/development/display-versions.md.
  def display_version
    match = DISPLAY_VERSION_PROPERTY.match(stylesheet)
    raise "packaged stylesheet declares no --prov-display-version" unless match

    match[1]
  end

  # Return the family part of display_version.
  def display_family
    display_version.rpartition("-").last
  end
end
