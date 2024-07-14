import re
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
from typing import Optional
from unidecode import unidecode
from wordcloud import WordCloud

from artistwordcloud.constants import (
    ARTIST_RE,
    ALBUM_LINK_CLASS,
    CLEAN_LYRICS_RE,
    COMBINED_STOPWORDS,
    LYRIC_CLASS,
)


def build_artist_page(artist_name: str) -> str:
    """
    Returns a link to an artist's Genius page when given their name
    """
    base_url = "https://genius.com/artists/"
    # Non-alphanumeric characters are excluded from Genius links, they are effectively replaced with ''
    # Spaces are replaced with '-'
    constructed_url = re.sub(ARTIST_RE, "", artist_name.replace(" ", "-").lower())
    return base_url + constructed_url + "/songs"


def build_song_links(
    artist_page: str, artist_name: str, album: Optional[str] = ""
) -> list:
    """
    Compiles a list of song links associated to a particular artist
    Pulls data from Genius's API
    """
    api_string = find_api(artist_page, artist_name)
    if api_string == "":
        raise ValueError()
    print(
        "Collecting links...\nDepending on the size of the artist's library, this may take a while..."
    )
    link_list = []
    if album is not None:
        try:
            album_slug = re.sub(ARTIST_RE, "", album)
            content = requests.get(
                f"https://genius.com/albums/{artist_name}/{album_slug}"
            )
            soup = BeautifulSoup(content.text, "html.parser")
            song_links = soup.find_all("a", class_=ALBUM_LINK_CLASS)
            for link in song_links:
                link_list.append(link["href"])
        except requests.exceptions.RequestException:
            raise LookupError()
    else:
        content = requests.get(
            f"https://genius.com/api/artists/{api_string}/songs?page=1&per_page=20&sort=popularity&text_format=html"
        ).json()
        while True:
            if content["response"]["next_page"] is not None:
                content = requests.get(
                    f"https://genius.com/api/artists/{api_string}"
                    f"/songs?page={content['response']['next_page']}&per_page=20&sort=popularity"
                    f"&text_format=html%2Cmarkdown"
                ).json()
            else:
                break
    return link_list


def _export_cloud(data_set: str) -> WordCloud:
    """
    Processes the string into a word cloud, returning the cloud
    """
    wordcloud = WordCloud(
        width=1080,
        height=1080,
        background_color="black",
        stopwords=COMBINED_STOPWORDS,
        min_font_size=8,
        max_words=150,
        relative_scaling=0.7,
    ).generate(unidecode(data_set))
    return wordcloud


def find_api(page: str, name: str) -> str:
    """
    Finds the api key for an artist on their artist page
    """
    response = requests.get(page)
    candidates = re.findall(r"artists/[0-9]+", response.text)
    api_string = ""
    for candidate in candidates:
        content = requests.get(f"https://genius.com/api/{candidate}").json()
        if unidecode(re.sub(r"\W", "", name.lower())) in unidecode(
            re.sub(r"\W", "", content["response"]["artist"]["name"].lower())
        ):
            api_string = re.sub(r"artists/", "", candidate)
            return api_string
    return api_string


def _process_lyrics(url: str) -> str:
    """
    Processes the lyrics for a particular webpage and returns them as a nicely formatted string
    This function is called by convert_lyrics as part of a multiprocessing pool
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    lyric_elements = soup.find_all("div", class_=LYRIC_CLASS)
    portions = [
        re.sub(CLEAN_LYRICS_RE, " ", item.decode_contents().lower())
        for item in lyric_elements
    ]
    return " ".join(re.sub(r"\s+", " ", portion) for portion in portions)


def _convert_lyrics(song_links: list[str]) -> str:
    """
    Processes the content of the webpage links lists into neatly formatted lyrics strings.
    """
    print("Processing lyrics...")
    if len(song_links) > 250:
        print("This may take a while...")
    # Multiprocess lyrics
    with Pool() as pool:
        data_set = pool.map(_process_lyrics, song_links)
        pool.close()
    return " ".join(data_set)


def cloud_hook(artist_name: str, album: Optional[str] = "") -> WordCloud or None:
    decode_artist = unidecode(artist_name)
    try:
        links = build_song_links(build_artist_page(decode_artist), decode_artist, album)
        return _export_cloud(_convert_lyrics(links))
    except ValueError:
        return None
