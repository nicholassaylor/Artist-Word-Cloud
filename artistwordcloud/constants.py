from re import compile
from nltk.corpus import stopwords
from wordcloud import STOPWORDS
from unidecode import unidecode
import nltk


try:
    nltk.data.find("corpora/stopwords.zip")
except LookupError:
    # Download stopwords if not found
    print("Downloading stopwords...")
    nltk.download("stopwords")

combined_stopwords = set(STOPWORDS)
for lang in stopwords.fileids():
    lang_stopwords = set(stopwords.words(unidecode(lang)))
    combined_stopwords.update(lang_stopwords)

COMBINED_STOPWORDS = combined_stopwords
ALBUM_LINK_CLASS = "u-display_block"
LYRIC_CLASS = "Lyrics__Container-sc-1ynbvzw-1 kUgSbL"
CLEAN_LYRICS_RE = compile(r"(\[[^\[\]]*])|((<[^>]*>)+)|([,.?!()\n])")
ARTIST_RE = compile(r"[^a-z0-9-]")
