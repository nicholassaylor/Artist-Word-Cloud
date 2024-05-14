from re import compile

LINK_CLASS = "ListItem__Link-sc-122yj9e-1"
LYRIC_CLASS = "Lyrics__Container-sc-1ynbvzw-1 kUgSbL"
SUMMARY_CLASS = "ListSectiondesktop__Summary-sc-53xokv-6.dSgVld"
SECTION_RE = compile(r'\[[^\[\]]*]')
HTML_TAG_RE = compile(r'(<[^>]*>)+')
CLEAN_PUNC_RE = compile(r'[,.?!()\n]')
ARTIST_RE = compile(r'[^a-z0-9-]')
MAX_COLLECTION_RETRIES = 5
