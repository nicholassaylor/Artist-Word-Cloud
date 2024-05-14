from re import compile

LYRIC_CLASS = "Lyrics__Container-sc-1ynbvzw-1 kUgSbL"
SECTION_RE = compile(r"\[[^\[\]]*]")
HTML_TAG_RE = compile(r"(<[^>]*>)+")
CLEAN_PUNC_RE = compile(r"[,.?!()\n]")
ARTIST_RE = compile(r"[^a-z0-9-]")
