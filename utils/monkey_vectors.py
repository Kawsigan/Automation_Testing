"""
Centralized Monkey & Chaos Test Vectors.
Provides standardized payloads for fuzzing, boundary testing,
security injection validation, and stress-testing input fields.
"""

# 1. SQL Injection / Database Payload Vectors
SQLI_VECTORS = [
    {"id": "sqli_01_or_true", "payload": "' OR '1'='1", "desc": "Classic OR true bypass"},
    {"id": "sqli_02_admin_comment", "payload": "admin'--", "desc": "Admin user comment bypass"},
    {"id": "sqli_03_union_select", "payload": "' UNION SELECT null, null, null--", "desc": "Union select probe"},
    {"id": "sqli_04_drop_table", "payload": "'; DROP TABLE test_dummy;--", "desc": "Stacked drop statement"},
    {"id": "sqli_05_sleep_blind", "payload": "' OR pg_sleep(0)--", "desc": "Time-based blind SQLi vector"},
    {"id": "sqli_06_boolean_and", "payload": "' AND 1=0 UNION ALL SELECT 'a'--", "desc": "Boolean based probe"},
    {"id": "sqli_07_quoted_numeric", "payload": "1' OR '1'='1' --", "desc": "Quoted numeric injection"},
    {"id": "sqli_08_hex_encoded", "payload": "0x27204f5220313d31", "desc": "Hex encoded injection probe"},
]

# 2. Cross-Site Scripting (XSS) & HTML Injection Vectors
XSS_VECTORS = [
    {"id": "xss_01_basic_script", "payload": "<script>alert(1)</script>", "desc": "Standard script tag"},
    {"id": "xss_02_img_onerror", "payload": "<img src=x onerror=alert(1)>", "desc": "Image onerror handler"},
    {"id": "xss_03_svg_onload", "payload": "<svg onload=alert(1)>", "desc": "SVG onload handler"},
    {"id": "xss_04_js_pseudo", "payload": "javascript:alert(1)", "desc": "Javascript pseudo-protocol"},
    {"id": "xss_05_iframe_src", "payload": "<iframe src='javascript:alert(1)'></iframe>", "desc": "Iframe injection"},
    {"id": "xss_06_event_handler", "payload": "\" onfocus=\"alert(1)\" autofocus=\"", "desc": "Attribute breakout onfocus"},
    {"id": "xss_07_body_onload", "payload": "<body onload=alert(1)>", "desc": "Body onload vector"},
    {"id": "xss_08_html_entities", "payload": "&lt;script&gt;alert(1)&lt;/script&gt;", "desc": "HTML entity payload"},
]

# 3. Unicode, Emojis & BiDi Vectors
UNICODE_VECTORS = [
    {"id": "unicode_01_emojis", "payload": "🔥🚀⚡️ Keepwisely Test 🛑🛠️", "desc": "High surrogate emoji sequence"},
    {"id": "unicode_02_cjk", "payload": "資産管理システム保守点検", "desc": "Japanese CJK ideographs"},
    {"id": "unicode_03_arabic_rtl", "payload": "نظام صيانة الأصول والمعدات", "desc": "Arabic right-to-left script"},
    {"id": "unicode_04_cyrillic", "payload": "Тестирование системы ТОиР", "desc": "Cyrillic unicode alphabet"},
    {"id": "unicode_05_accents", "payload": "Mainténânce des équípeménts spéciaux", "desc": "Accented Latin characters"},
    {"id": "unicode_06_zero_width", "payload": "Keep\u200bWise\u200cly\u200dApp", "desc": "Zero-width joiners and spaces"},
    {"id": "unicode_07_zalgo_text", "payload": "K̵e̴e̶p̵W̵i̸s̷e̸l̴y̶", "desc": "Zalgo combining diacritics"},
    {"id": "unicode_08_bidi_override", "payload": "\u202Ereversed_input\u202C", "desc": "Right-to-left override marker"},
]

# 4. Boundary Length & Buffer Overflow Vectors
BOUNDARY_LENGTH_VECTORS = [
    {"id": "len_01_single_char", "payload": "A", "desc": "Single character boundary"},
    {"id": "len_02_32_chars", "payload": "A" * 32, "desc": "32-character boundary"},
    {"id": "len_03_64_chars", "payload": "B" * 64, "desc": "64-character boundary"},
    {"id": "len_04_128_chars", "payload": "C" * 128, "desc": "128-character boundary"},
    {"id": "len_05_256_chars", "payload": "D" * 256, "desc": "256-character boundary"},
    {"id": "len_06_512_chars", "payload": "E" * 512, "desc": "512-character boundary"},
    {"id": "len_07_1024_chars", "payload": "F" * 1024, "desc": "1024-character buffer"},
    {"id": "len_08_2048_chars", "payload": "G" * 2048, "desc": "2048-character stress buffer"},
]

# 5. Whitespace Chaos Vectors
WHITESPACE_CHAOS_VECTORS = [
    {"id": "ws_01_leading_spaces", "payload": "    LeadingSpaces", "desc": "4 leading spaces"},
    {"id": "ws_02_trailing_spaces", "payload": "TrailingSpaces    ", "desc": "4 trailing spaces"},
    {"id": "ws_03_both_padded", "payload": "   PaddedValue   ", "desc": "Leading and trailing spaces"},
    {"id": "ws_04_inner_tabs", "payload": "Tab\tSeparated\tInput", "desc": "Horizontal tab characters"},
    {"id": "ws_05_newlines", "payload": "Line1\nLine2\nLine3", "desc": "Embedded newline characters"},
    {"id": "ws_06_multiple_spaces", "payload": "Multi     Spaced     Query", "desc": "Consecutive inner spaces"},
    {"id": "ws_07_spaces_only", "payload": "          ", "desc": "Spaces-only query"},
    {"id": "ws_08_nbsp", "payload": "Non\u00A0Breaking\u00A0Spaces", "desc": "Non-breaking whitespace"},
]

# 6. Numerical, Format & Special Symbol Vectors
SPECIAL_SYMBOL_VECTORS = [
    {"id": "sym_01_punctuations", "payload": "!@#$%^&*()_+~|}{[]:;?><,./", "desc": "Full ASCII punctuation set"},
    {"id": "sym_02_path_traversal", "payload": "../../../../etc/passwd", "desc": "Path traversal pattern"},
    {"id": "sym_03_format_string", "payload": "%s%s%s%s%s%n%x", "desc": "C-style format string specifier"},
    {"id": "sym_04_null_byte", "payload": "Test\x00NullByte", "desc": "Embedded null byte character"},
    {"id": "sym_05_template_expr", "payload": "{{7*7}} ${7*7} #{7*7}", "desc": "Template expression injection"},
    {"id": "sym_06_negative_number", "payload": "-999999999", "desc": "Extreme negative integer"},
    {"id": "sym_07_large_float", "payload": "1.7976931348623157e+308", "desc": "IEEE double max float"},
    {"id": "sym_08_json_fragment", "payload": '{"key": null, "arr": [1,2,3]}', "desc": "Raw JSON object payload"},
]

def get_all_monkey_vectors():
    """Returns combined list of 48 comprehensive chaos test vectors."""
    return (
        SQLI_VECTORS
        + XSS_VECTORS
        + UNICODE_VECTORS
        + BOUNDARY_LENGTH_VECTORS
        + WHITESPACE_CHAOS_VECTORS
        + SPECIAL_SYMBOL_VECTORS
    )
