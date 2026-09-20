# frozen_string_literal: true

require_relative "lib/textprov/version"

Gem::Specification.new do |spec|
  spec.name        = "textprov"
  spec.version     = Textprov::VERSION
  spec.summary     = "Put provenance marks in text, and read them back out"
  spec.description = "Ruby reference implementation of the TextProv protocol: encode, decode, convert, and render provenance-marked text."
  spec.authors     = ["TextProv contributors"]
  spec.license     = "MIT"
  spec.homepage    = "https://github.com/textprov/textprov"

  spec.metadata = {
    "source_code_uri"    => "https://github.com/textprov/textprov",
    "specification_uri"  => "https://github.com/textprov/textprov/blob/main/SPEC.md",
    "bug_tracker_uri"    => "https://github.com/textprov/textprov/issues"
  }

  spec.required_ruby_version = ">= 3.2"

  spec.files = Dir["lib/**/*", "bin/*", "LICENSE", "README.md"]
  spec.bindir      = "bin"
  spec.executables = ["textprov"]
  spec.require_paths = ["lib"]

  spec.add_development_dependency "minitest", "~> 5.20"
  spec.add_development_dependency "rake", "~> 13.0"
end
