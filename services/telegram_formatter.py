import re
import html

def convert_markdown_tables(text: str) -> str:
    """
    Finds markdown tables and transforms them into clean Telegram-friendly bullet lists using markdown syntax.
    """
    lines = text.split("\n")
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        # Check if line looks like a table row
        if stripped.startswith("|") and stripped.endswith("|") and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            # Check if next line is a separator like |---|---| or |:---:|
            if next_line.startswith("|") and re.match(r'^\|[\s:\-\|]+\|$', next_line):
                # Parse headers
                headers = [h.strip() for h in stripped.strip("|").split("|")]
                i += 2 # skip header and separator
                
                rows = []
                while i < len(lines):
                    row_line = lines[i].strip()
                    if not (row_line.startswith("|") and row_line.endswith("|")):
                        break
                    cells = [c.strip() for c in row_line.strip("|").split("|")]
                    if any(cells):
                        rows.append(cells)
                    i += 1
                
                # Format into bullet points with bold / italic
                new_lines.append("")
                for r in rows:
                    if not r:
                        continue
                    first_cell = r[0] if len(r) > 0 else ""
                    remaining = []
                    for h_idx in range(1, len(r)):
                        h_title = headers[h_idx] if h_idx < len(headers) else f"Detail {h_idx}"
                        val = r[h_idx]
                        if val:
                            remaining.append(f"• *{h_title}:* {val}")
                    
                    if remaining:
                        new_lines.append(f"📌 **{first_cell}**")
                        for item in remaining:
                            new_lines.append(f"  {item}")
                    else:
                        new_lines.append(f"• **{first_cell}**")
                new_lines.append("")
                continue

        new_lines.append(line)
        i += 1

    return "\n".join(new_lines)


def format_telegram_html(text: str) -> str:
    """
    Converts general LLM markdown output into valid, clean Telegram HTML.
    Prevents unsupported tags, unrendered tables, and raw markdown headers.
    """
    if not text:
        return ""

    # 1. Convert markdown tables to clean markdown bullets first
    text = convert_markdown_tables(text)

    # 2. Extract and protect code blocks using safe tokens without underscores
    code_blocks = []
    def save_code_block(m):
        lang = m.group(1) or ""
        code = m.group(2)
        idx = len(code_blocks)
        escaped_code = html.escape(code.rstrip())
        if lang:
            code_blocks.append(f'<pre><code class="language-{html.escape(lang)}">{escaped_code}</code></pre>')
        else:
            code_blocks.append(f'<pre><code>{escaped_code}</code></pre>')
        return f"%%TGCODEBLOCK{idx}%%"

    text = re.sub(r'```([a-zA-Z0-9_\-\+]*)\n(.*?)```', save_code_block, text, flags=re.DOTALL)

    # 3. Extract and protect inline code
    inline_codes = []
    def save_inline_code(m):
        code = m.group(1)
        idx = len(inline_codes)
        inline_codes.append(f"<code>{html.escape(code)}</code>")
        return f"%%TGINLINECODE{idx}%%"

    text = re.sub(r'`([^`\n]+)`', save_inline_code, text)

    # 4. Safely escape HTML in prose
    text = html.escape(text)

    # 5. Convert Markdown Headers (#, ##, ###) into bold headers with emojis
    text = re.sub(r'(?m)^#{4,}\s*(.*?)$', r'• <b>\1</b>', text)
    text = re.sub(r'(?m)^###\s*(.*?)$', r'🔹 <b>\1</b>', text)
    text = re.sub(r'(?m)^##\s*(.*?)$', r'💡 <b>\1</b>', text)
    text = re.sub(r'(?m)^#\s*(.*?)$', r'🌟 <b>\1</b>', text)

    # 6. Convert horizontal rules (--- or ***) to blank line
    text = re.sub(r'(?m)^[\s\-\*_]{3,}\s*$', '', text)

    # 7. Convert Markdown Bold: **bold** or __bold__ -> <b>bold</b>
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)

    # 8. Convert Markdown Italic: *italic* or _italic_ -> <i>italic</i>
    text = re.sub(r'(?<!\w)\*([^\*\n]+?)\*(?!\w)', r'<i>\1</i>', text)
    text = re.sub(r'(?<!\w)_([^_\n]+?)_(?!\w)', r'<i>\1</i>', text)

    # 9. Convert Markdown Links: [text](url) -> <a href="url">text</a>
    text = re.sub(r'\[([^\]]+)\]\((https?://[^\s\)]+)\)', r'<a href="\2">\1</a>', text)

    # 10. Restore code blocks & inline code
    for idx, block in enumerate(code_blocks):
        text = text.replace(f"%%TGCODEBLOCK{idx}%%", block)

    for idx, code in enumerate(inline_codes):
        text = text.replace(f"%%TGINLINECODE{idx}%%", code)

    # 11. Normalize excessive blank lines (more than 2 consecutive newlines)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()

    return text
