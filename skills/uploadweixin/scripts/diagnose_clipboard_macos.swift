import AppKit
import Foundation

let pasteboard = NSPasteboard.general
let types = pasteboard.types ?? []
let rawTypes = types.map { $0.rawValue }
let hasHTML = rawTypes.contains("public.html") || rawTypes.contains("Apple HTML pasteboard type")
let hasRTF = rawTypes.contains("public.rtf") || rawTypes.contains("NeXT Rich Text Format v1.0 pasteboard type")
let hasPlainText = rawTypes.contains("public.utf8-plain-text")
    || rawTypes.contains("public.utf16-external-plain-text")
    || rawTypes.contains("NSStringPboardType")

print("clipboard_types=\(rawTypes.joined(separator: ","))")
print("has_html=\(hasHTML)")
print("has_rtf=\(hasRTF)")
print("has_plain_text=\(hasPlainText)")

if hasHTML || hasRTF {
    print("PASS rich clipboard is available")
} else if hasPlainText {
    print("WARN clipboard has plain text only; WeChat paste will lose formatting")
} else {
    print("WARN clipboard has no recognized article content")
}
