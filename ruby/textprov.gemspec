# frozen_string_literal: true

require_relative "lib/textprov/version"

Gem::Specification.new do |spec|
  spec.name        = "textprov"
  spec.version     = Textprov::VERSION
  spec.summary     = "Put provenance marks in text, and read them back out"
  spec.description = "Ruby reference implementation of the TextProv protocol: " \
                     "encode, decode, convert, and render provenance-marked text."
  spec.authors     = ["TextProv contributors"]
  spec.license     = "MIT"
  spec.homepage    = "https://github.com/textprov/textprov"

  spec.metadata = {
    "source_code_uri" => "https://github.com/textprov/textprov",
    "specification_uri" => "https://github.com/textprov/textprov/blob/main/SPEC.md",
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
