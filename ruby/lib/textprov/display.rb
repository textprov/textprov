# frozen_string_literal: true

module Textprov
  module_function

  DISPLAY_VERSION_PROPERTY = /--prov-display-version:\s*"([^"]+)"/

  # Return the shared gradient-mist and dotted-underline CSS as UTF-8 text.
  def stylesheet
    File.read(File.join(__dir__, "textprov.css"), encoding: "UTF-8")
  end

  # Return the reveal treatment version, "YYYY-MM-DD.family", read from
  # --prov-display-version in the packaged stylesheet (its single source).
  # Scheme: docs/development/display-versions.md.
  def display_version
    match = DISPLAY_VERSION_PROPERTY.match(stylesheet)
    raise "packaged stylesheet declares no --prov-display-version" unless match

    match[1]
  end
end
