#!/usr/bin/env python3
"""Build es/index.html from index.html and es.json. Stdlib only.

The English page is the single source for layout, styles and logic. es.json maps each
English text block to its Spanish translation. The build FAILS if any English block has
no translation, so the Spanish page can never silently fall behind the English one.

  python3 build_es.py          build es/index.html
  python3 build_es.py --list   print English blocks that still need a translation
"""
import json, os, re, sys

SRC = open("index.html", encoding="utf-8").read()
head, script = SRC.split("<script>", 1)   # text blocks live in the markup; the script is handled below

# Markup that must survive translation untouched is swapped for numbered tokens: {a1}, {svg1}...
TOKEN = re.compile(r'(?P<svg><svg\b.*?</svg>)|(?P<a><a\b[^>]*>.*?</a>)|(?P<i><input\b[^>]*>)'
                   r'|(?P<dot><span class="dot"[^>]*></span>)|(?P<n><span class="num">.*?</span>)', re.S)
BLOCK = re.compile(r"<(title|h1|h2|h3|p|li|label|summary|button|small|a|b|span)(\s[^>]*)?>(.*?)</\1>", re.S)

def tokenize(inner):
    found, seen = {}, {}
    def sub(m):
        kind = m.lastgroup
        seen[kind] = seen.get(kind, 0) + 1
        name = "{%s%d}" % (kind, seen[kind])
        found[name] = m.group(0)
        return name
    return " ".join(TOKEN.sub(sub, inner).split()), found

def norm(inner):
    return tokenize(inner)[0]

def needs_translation(key):
    text = re.sub(r"<[^>]+>|\{[a-z]+\d+\}", "", key)
    if not re.search(r"[A-Za-z]{2}", text):
        return False                      # numbers, dashes, emoji
    return not re.fullmatch(r"[\w.-]+\.(gov|com|ca|dev)(/\S*)?", text.strip())   # a bare web address

def blocks(markup):
    body_at = markup.index("<body")
    for m in BLOCK.finditer(markup):
        if m.group(1) != "title" and m.start() < body_at:
            continue
        key = norm(m.group(3))
        if needs_translation(key):
            yield m, key

def main():
    tr = json.load(open("es.json", encoding="utf-8"))
    text, js, attrs = tr["text"], tr["js"], tr["attrs"]
    missing = sorted({k for _, k in blocks(head) if k not in text})
    if "--list" in sys.argv:
        print(json.dumps(missing, indent=1, ensure_ascii=False)); return
    if missing:
        sys.exit("es.json is missing %d translation(s):\n  " % len(missing) + "\n  ".join(missing))

    out, last = [], 0
    for m, key in blocks(head):
        es, found = text[key], tokenize(m.group(3))[1]
        for name, markup in found.items():
            if name not in es:
                sys.exit("translation of %r dropped %s" % (key, name))
            es = es.replace(name, markup)
        out += [head[last:m.start(3)], es]; last = m.end(3)
    page = "".join(out) + head[last:]

    code = script
    for en, es in attrs.items():
        if en not in page:
            sys.exit("es.json [attrs] no longer matches index.html: %r" % en)
        page = page.replace(en, es)
    for en, es in js.items():
        if en not in code:
            sys.exit("es.json [js] no longer matches index.html: %r" % en)
        code = code.replace(en, es)

    os.makedirs("es", exist_ok=True)
    open("es/index.html", "w", encoding="utf-8").write(page + "<script>" + code)
    print("built es/index.html: %d text blocks, %d script strings" % (len(list(blocks(head))), len(js)))

main()
