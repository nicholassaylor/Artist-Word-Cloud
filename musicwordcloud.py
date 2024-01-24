from bs4 import BeautifulSoup as bs
import requests
import re


SECTION_RE = re.compile(r'\[[^\[\]]*\]')
HTML_TAG_RE = re.compile(r'(\<[^>]*\>)+')


def main():
    artist_song_page = build_artist_page(input("Enter artist name:"))
    #TODO: Find url dynamically
    #url = 'https://genius.com/Caligulas-horse-the-world-breathes-with-me-lyrics'
    #url = 'https://genius.com/Nwa-fuck-tha-police-lyrics'
    url = 'https://genius.com/Eminem-lose-yourself-lyrics'
    response = requests.get(url)
    soup = bs(response.text, 'html.parser')
    lyrics_elements = soup.find_all('div', class_='Lyrics__Container-sc-1ynbvzw-1 kUgSbL')
    for item in lyrics_elements:
        print(remove_fluff(item.decode_contents()))


def remove_fluff(element) -> str:
    """Removes html tags, section names, and additional non-lyric text from lyrics"""
    element = re.sub(HTML_TAG_RE, ' ', element)
    return re.sub(SECTION_RE, '', element)


def build_artist_page(artist: str) -> str:
    base_url = "https://genius.com/artists/"
    constructed_url = re.sub(r'[^a-zA-Z0-9-]', '', artist.replace(" ", "-").lower())
    return base_url + constructed_url + "/songs"


if __name__ == "__main__":
    main()
