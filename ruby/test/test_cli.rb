# frozen_string_literal: true

require_relative "test_helper"
require "tmpdir"
require "fileutils"
require "stringio"
require "textprov/cli"

class TestCli < Minitest::Test
  def setup
    @dir = Dir.mktmpdir("textprov-ruby-test-")
  end

  def teardown
    FileUtils.remove_entry(@dir) if @dir && File.directory?(@dir)
  end

  def write(name, text)
    path = File.join(@dir, name)
    File.binwrite(path, text.dup.force_encoding("UTF-8").b)
    path
  end

  def run_cli(*argv)
    out = File.join(@dir, "out.txt")

    assert_equal 0, Textprov::CLI.main(["-o", out, *argv])
    File.binread(out).force_encoding("UTF-8")
  end

  def test_mark_convert_strip_round_trip
    source = "Written by a human."
    path = write("s.txt", source)
    marked = run_cli("mark", path)

    assert_equal Textprov.mark(source), marked
    pua = run_cli("convert", write("m.txt", marked), "--from", "vs", "--to", "pua")

    assert_equal Textprov.convert(marked, "vs", "pua"), pua
    assert_equal source, run_cli("strip", write("p.txt", pua))
  end

  def test_mark_state_and_mode_flags
    path = write("s.txt", "Hi")

    assert_equal Textprov.mark("Hi", state: "human"), run_cli("mark", "--human", path)
    assert_equal Textprov.mark("Hi", state: "ai", mode: "pua"),
                 run_cli("mark", "--mode", "pua", path)
  end

  def test_mark_added
    old = write("old.txt", "abc")
    new = write("new.txt", "abXc")

    assert_equal "abX" + AI + "c", run_cli("mark-added", old, new)
  end

  def test_render_and_inspect
    path = write("m.txt", "a" + AI)

    assert_equal Textprov.to_html("a" + AI), run_cli("render", path)
    assert_includes run_cli("render", "--class-prefix", "x", path), 'class="x x-ai"'
    assert_includes run_cli("inspect", path), "ai_vs: 1"
  end

  def test_stdout_is_used_when_no_output_file
    path = write("s.txt", "Hi")
    buffer = StringIO.new
    buffer.set_encoding(Encoding::BINARY)
    original = $stdout
    $stdout = buffer
    begin
      Textprov::CLI.main(["mark", path])
      Textprov::CLI.main(["mark", path])
    ensure
      $stdout = original
    end

    assert_equal Textprov.mark("Hi") * 2, buffer.string.force_encoding("UTF-8")
  end

  def test_crlf_survives
    path = write("s.txt", "a\r\nb")

    assert_equal "a" + AI + "\r\nb" + AI, run_cli("mark", path)
  end

  def test_version_flag
    original = $stdout
    buffer = StringIO.new
    $stdout = buffer
    begin
      assert_equal 0, Textprov::CLI.main(["--version"])
    ensure
      $stdout = original
    end

    assert_match(/\Atextprov \d+\.\d+\.\d+ \(contract 1, mapping 1\)/, buffer.string)
  end
end
