# frozen_string_literal: true

require_relative "lib/textprov/version"

Gem::Specification.new do |spec|
  spec.name        = "textprov"
  spec.version     = Textprov::VERSION
  spec.summary     = "Experimental TextProv text attribution encoder and decoder."
  spec.description = "Ruby SDK demonstration for the TextProv proposal. " \
                     "Encodes and decodes producer-declared origin labels in Unicode text; " \
                     "does not detect or verify origin."
  spec.authors     = ["TextProv contributors"]
  spec.license     = "MIT"
  spec.homepage    = "https://github.com/textprov/textprov"

  spec.metadata = {
    "source_code_uri" => "https://github.com/textprov/textprov",
    "bug_tracker_uri" => "https://github.com/textprov/textprov/issues",
    "rubygems_mfa_required" => "true"
  }

  spec.required_ruby_version = ">= 3.2"

  spec.files = Dir.chdir(__dir__) do
    Dir["lib/**/*", "exe/*", "LICENSE", "README.md"]
  end
  spec.bindir = "exe"
  spec.executables = spec.files.grep(%r{\Aexe/}) { |file| File.basename(file) }
  spec.require_paths = ["lib"]
end
