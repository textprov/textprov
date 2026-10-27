// macOS plain-text clipboard roundtrip; restore every original clipboard type.
// Usage: swift tools/check_marked_clipboard.swift /absolute/marked-sample.txt
import AppKit
import Foundation

enum ClipboardCheckError: Error { case failed(String) }

func check(_ path: String) throws {
    let expected = try String(contentsOfFile: path, encoding: .utf8)
    let clipboard = NSPasteboard.general
    let saved = try (clipboard.pasteboardItems ?? []).map { item in
        try item.types.map { type -> (NSPasteboard.PasteboardType, Data) in
            guard let data = item.data(forType: type) else {
                throw ClipboardCheckError.failed("Could not preserve an original clipboard type")
            }
            return (type, data)
        }
    }
    defer {
        clipboard.clearContents()
        let items = saved.map { values -> NSPasteboardItem in
            let item = NSPasteboardItem()
            for (type, data) in values { item.setData(data, forType: type) }
            return item
        }
        clipboard.writeObjects(items)
    }
    clipboard.clearContents()
    guard clipboard.setString(expected, forType: .string),
          clipboard.string(forType: .string) == expected else {
        throw ClipboardCheckError.failed("Clipboard changed marked Unicode text")
    }
    print("PASS: macOS clipboard preserved all \(expected.unicodeScalars.count) Unicode scalars; original clipboard restored")
}

do {
    guard CommandLine.arguments.count == 2 else {
        throw ClipboardCheckError.failed("Supply a marked UTF-8 sample file")
    }
    try check(CommandLine.arguments[1])
} catch {
    fputs("FAIL: \(error)\n", stderr)
    exit(1)
}
