# frozen_string_literal: true

module Textprov
  module_function

  # Return the shared gradient-mist and dotted-underline CSS as UTF-8 text.
  def stylesheet
    File.read(File.join(__dir__, "textprov.css"), encoding: "UTF-8")
  end
end
