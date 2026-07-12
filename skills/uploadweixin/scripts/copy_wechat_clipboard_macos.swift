import AppKit
import Foundation

func fail(_ message: String) -> Never {
    FileHandle.standardError.write(("FAIL\n- " + message + "\n").data(using: .utf8)!)
    exit(1)
}

guard CommandLine.arguments.count >= 2 else {
    fail("缺少 article.html 路径。建议：swift copy_wechat_clipboard_macos.swift /path/to/article.html")
}

let inputPath = CommandLine.arguments[1]
let inputURL = URL(fileURLWithPath: inputPath)

guard FileManager.default.fileExists(atPath: inputPath) else {
    fail("article.html 输入文件不存在：\(inputPath)。建议：先运行 render_wechat_article.py 生成 article.html，再复制真实路径。")
}

let html: String
do {
    html = try String(contentsOf: inputURL, encoding: .utf8)
} catch {
    fail("读取 HTML 失败：\(error)。建议：确认文件是 UTF-8 编码且当前用户有读取权限。")
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
    fail("转换富文本失败：\(error)。建议：先运行 validate_wechat_html.py 检查 article.html。")
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
