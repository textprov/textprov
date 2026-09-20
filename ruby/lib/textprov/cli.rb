# ruby/lib/textprov/cli.rb
#
# frozen_string_literal: true

require "optparse"
require_relative "../textprov"

module Textprov
  module CLI
    PROG = "textprov"

    module_function

    def read_input(path)
      if path == "-"
        $stdin.binmode
        $stdin.read.force_encoding("UTF-8")
      else
        File.binread(path).force_encoding("UTF-8")
      end
    end

    def write_output(text, path)
      bytes = text.dup.force_encoding("UTF-8").b
      if path
        File.binwrite(path, bytes)
      else
        $stdout.binmode
        $stdout.write(bytes)
        $stdout.flush
      end
    end

    def version_string
      "#{PROG} #{Textprov::VERSION} (contract #{Textprov::CONTRACT_VERSION}, mapping #{Textprov.default_mapping.version})"
    end

    def usage
      <<~USAGE
        Usage: #{PROG} [-o FILE] COMMAND [OPTIONS] ARGS...

        Commands:
          mark [--human|--ai|--mixed] [--mode vs|pua] FILE
          mark-added [--human|--ai|--mixed] [--mode vs|pua] OLD NEW
          convert --from vs|pua --to vs|pua FILE
          strip FILE
          render [--strip] [--no-merge-whitespace] [--class-prefix P] FILE
          inspect FILE

        FILE may be '-' for stdin. Text is read and written as UTF-8 verbatim.
        --version prints the version and exits.
      USAGE
    end

    def parse_state(argv, defaults: { state: "ai", mode: "vs" })
      opts = defaults.dup
      rest = []
      i = 0
      while i < argv.length
        case argv[i]
        when "--human", "--ai", "--mixed"
          opts[:state] = argv[i].sub(/^--/, "")
        when "--mode"
          opts[:mode] = argv[i + 1]
          raise ArgumentError, "invalid --mode #{opts[:mode].inspect}" unless %w[vs
                                                                                 pua].include?(opts[:mode])

          i += 1
        else
          rest << argv[i]
        end
        i += 1
      end
      [opts, rest]
    end

    def main(argv)
      argv = argv.dup
      # Top-level --version / --help handled before subcommand dispatch.
      if argv.include?("--version")
        $stdout.puts version_string
        return 0
      end
      if argv.include?("--help") || argv.include?("-h") || argv.empty?
        $stdout.puts usage
        return argv.empty? ? 1 : 0
      end

      # -o/--output may appear before or after the command.
      output = nil
      filtered = []
      i = 0
      while i < argv.length
        case argv[i]
        when "-o", "--output"
          output = argv[i + 1]
          i += 1
        else
          filtered << argv[i]
        end
        i += 1
      end
      argv = filtered

      command = argv.shift
      out =
        case command
        when "mark"
          opts, rest = parse_state(argv)
          raise ArgumentError, "mark: FILE required" if rest.empty?

          Textprov.mark(read_input(rest[0]), state: opts[:state], mode: opts[:mode])
        when "mark-added"
          opts, rest = parse_state(argv)
          raise ArgumentError, "mark-added: OLD and NEW required" if rest.length < 2

          Textprov.mark_added(read_input(rest[0]), read_input(rest[1]),
                              state: opts[:state], mode: opts[:mode])
        when "convert"
          from_mode = nil
          to_mode = nil
          rest = []
          i = 0
          while i < argv.length
            case argv[i]
            when "--from" then from_mode = argv[i + 1]
                               i += 1
            when "--to" then to_mode = argv[i + 1]
                             i += 1
            else rest << argv[i]
            end
            i += 1
          end
          raise ArgumentError, "convert: --from and --to required" unless from_mode && to_mode
          raise ArgumentError, "convert: FILE required" if rest.empty?

          Textprov.convert(read_input(rest[0]), from_mode, to_mode)
        when "strip"
          raise ArgumentError, "strip: FILE required" if argv.empty?

          Textprov.strip_marks(read_input(argv[0]))
        when "render"
          strip = false
          merge_ws = true
          class_prefix = "prov"
          rest = []
          i = 0
          while i < argv.length
            case argv[i]
            when "--strip" then strip = true
            when "--no-merge-whitespace" then merge_ws = false
            when "--class-prefix" then class_prefix = argv[i + 1]
                                       i += 1
            else rest << argv[i]
            end
            i += 1
          end
          raise ArgumentError, "render: FILE required" if rest.empty?

          Textprov.to_html(read_input(rest[0]),
                           strip: strip, merge_whitespace: merge_ws, class_prefix: class_prefix)
        when "inspect"
          raise ArgumentError, "inspect: FILE required" if argv.empty?

          Textprov.inspect_text(read_input(argv[0]))
        else
          warn "unknown command: #{command}"
          warn usage
          return 2
        end

      write_output(out, output)
      0
    rescue ArgumentError => e
      warn "#{PROG}: #{e.message}"
      2
    end
  end
end
