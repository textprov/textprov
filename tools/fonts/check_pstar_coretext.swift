// Verify P* space joins with macOS CoreText. Compile with swiftc, then run:
// check-pstar-coretext ORIGINAL.ttf PSTAR.ttf samples.json
// samples.json: [{"text": "...", "bridges": 1}, ...]
import Foundation
import CoreText

func fail(_ message: String) -> Never {
    FileHandle.standardError.write((message + "\n").data(using: .utf8)!)
    exit(1)
}

func load(_ path: String) -> CTFont {
    let url = URL(fileURLWithPath: path) as CFURL
    guard let descriptors = CTFontManagerCreateFontDescriptorsFromURL(url) as? [CTFontDescriptor],
          let descriptor = descriptors.first else { fail("Cannot load \(path)") }
    return CTFontCreateWithFontDescriptor(descriptor, 24, nil)
}

struct Sample: Decodable { let text: String; let bridges: Int }
struct Shape: Equatable { let names: [String]; let advances: [Double] }

func shape(_ text: String, _ font: CTFont, restoringBridge: Bool, spaceName: String) -> (Shape, Int) {
    let attributed = NSAttributedString(string: text, attributes: [kCTFontAttributeName as NSAttributedString.Key: font])
    let line = CTLineCreateWithAttributedString(attributed)
    var names: [String] = [], advances: [Double] = [], bridges = 0
    for run in CTLineGetGlyphRuns(line) as! [CTRun] {
        let attributes = CTRunGetAttributes(run) as! [NSAttributedString.Key: Any]
        let actual = attributes[kCTFontAttributeName as NSAttributedString.Key] as! CTFont
        guard CTFontCopyPostScriptName(actual) == CTFontCopyPostScriptName(font) else { fail("Unexpected fallback font") }
        let count = CTRunGetGlyphCount(run)
        var glyphs = [CGGlyph](repeating: 0, count: count)
        var widths = [CGSize](repeating: .zero, count: count)
        CTRunGetGlyphs(run, CFRangeMake(0, 0), &glyphs)
        CTRunGetAdvances(run, CFRangeMake(0, 0), &widths)
        for (glyph, width) in zip(glyphs, widths) {
            var name = CTFontCopyNameForGlyph(actual, glyph) as String? ?? "gid\(glyph)"
            if name == "space.provenance.ai" {
                bridges += 1
                if restoringBridge { name = spaceName }
            }
            if name == "space.provenance.candidate" { fail("Temporary candidate glyph escaped cleanup") }
            names.append(name)
            advances.append(Double(width.width))
        }
    }
    return (Shape(names: names, advances: advances), bridges)
}

let arguments = CommandLine.arguments
guard arguments.count == 4 else { fail("Usage: check-pstar-coretext ORIGINAL.ttf PSTAR.ttf samples.json") }
let original = load(arguments[1]), patched = load(arguments[2])
var spaceCharacter: UniChar = 0x20
var spaceGlyph: CGGlyph = 0
guard CTFontGetGlyphsForCharacters(original, &spaceCharacter, &spaceGlyph, 1),
      let spaceName = CTFontCopyNameForGlyph(original, spaceGlyph) as String? else { fail("Missing ordinary space") }
let samples = try JSONDecoder().decode([Sample].self, from: Data(contentsOf: URL(fileURLWithPath: arguments[3])))
for (index, sample) in samples.enumerated() {
    let (before, _) = shape(sample.text, original, restoringBridge: false, spaceName: spaceName)
    let (after, bridges) = shape(sample.text, patched, restoringBridge: true, spaceName: spaceName)
    guard bridges == sample.bridges else { fail("Sample \(index): expected \(sample.bridges) bridges, got \(bridges)") }
    guard before == after else {
        fail("Sample \(index): glyphs or advances changed beyond space ink\nBefore: \(before)\nAfter: \(after)")
    }
}
print("PASS CoreText: \(CTFontCopyPostScriptName(patched)), \(samples.count) samples; glyphs and advances preserved")
