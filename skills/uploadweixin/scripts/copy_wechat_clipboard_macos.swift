import AppKit
import Foundation

func fail(_ message: String) -> Never {
    FileHandle.standardError.write((message + "\n").data(using: .utf8)!)
    exit(1)
}

guard CommandLine.arguments.count >= 2 else {
    fail("Usage: swift copy_wechat_clipboard_macos.swift /path/to/article.html")
}

let inputPath = CommandLine.arguments[1]
let inputURL = URL(fileURLWithPath: inputPath)

guard FileManager.default.fileExists(atPath: inputPath) else {
    fail("Input file not found: \(inputPath)")
}

let html: String
do {
    html = try String(contentsOf: inputURL, encoding: .utf8)
} catch {
    fail("Failed to read HTML: \(error)")
}

let htmlData = Data(html.utf8)
let attributed: NSMutableAttributedString
do {
    attributed = try NSMutableAttributedString(
        data: htmlData,
        options: [
            .documentType: NSAttributedString.DocumentType.html,
            .characterEncoding: String.Encoding.utf8.rawValue
        ],
        documentAttributes: nil
    )
} catch {
    fail("Failed to convert HTML to rich text: \(error)")
}

let plainText = attributed.string
let pasteboard = NSPasteboard.general
pasteboard.clearContents()

let wroteRichObject = pasteboard.writeObjects([attributed])
pasteboard.setString(html, forType: .html)
pasteboard.setString(html, forType: NSPasteboard.PasteboardType(rawValue: "public.html"))
pasteboard.setString(plainText, forType: .string)

let types = (pasteboard.types ?? []).map { $0.rawValue }.joined(separator: ",")
print("PASS clipboard rich=\(wroteRichObject) chars=\(plainText.count)")
print("types=\(types)")
