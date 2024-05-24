import os
import re
import sys
from multiprocessing import Pool, freeze_support

import matplotlib.pyplot as plot
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from wordcloud import WordCloud

from constants import ARTIST_RE, CLEAN_PUNC_RE, COMBINED_STOPWORDS, HTML_TAG_RE, LYRIC_CLASS, SECTION_RE


def remove_fluff(element) -> str:
    """
    Removes html tags, section names, and additional non-lyric text from lyrics
    """
    element = re.sub(HTML_TAG_RE, " ", element)
    element = re.sub(SECTION_RE, "", element)
    return re.sub(CLEAN_PUNC_RE, "", element).replace("\n", " ")


def build_artist_page(artist_name: str) -> str:
    """
    Returns a link to an artist's Genius page when given their name
    """
    base_url = "https://genius.com/artists/"
    # Non-alphanumeric characters are excluded from Genius links, they are effectively replaced with ''
    # Spaces are replaced with '-'
    constructed_url = re.sub(ARTIST_RE, "", artist_name.replace(" ", "-").lower())
    return base_url + constructed_url + "/songs"


def build_song_links(artist_page: str, artist_name: str) -> list:
    """
    Compiles a list of song links associated to a particular artist
    Pulls data from Genius's API
    """
    response = requests.get(artist_page)
    candidates = re.findall(r"artists/[0-9]+", response.text)
    api_string = ""
    for candidate in candidates:
        content = requests.get(f"https://genius.com/api/{candidate}").json()
        if (unidecode(re.sub(r"\W", "", artist_name.lower())) in
                unidecode(re.sub(r"\W", "", content["response"]["artist"]["name"].lower()))):
            api_string = re.sub(r"artists/", "", candidate)
            break
    if api_string == "":
        raise ValueError()
    print(
        "Collecting links...\nDepending on the size of the artist's library, this may take a while..."
    )
    content = requests.get(
        f"https://genius.com/api/artists/{api_string}/songs?page=1&per_page=20&sort=popularity&text_format=html%2Cmarkdown"
    ).json()
    link_list = []
    while True:
        for entry in content["response"]["songs"]:
            link_list.append(entry["url"])
        if content["response"]["next_page"] is not None:
            content = requests.get(
                f"https://genius.com/api/artists/{api_string}"
                f"/songs?page={content['response']['next_page']}&per_page=20&sort=popularity"
                f"&text_format=html%2Cmarkdown"
            ).json()
        else:
            break
    return link_list


def process_lyrics(url: str) -> str:
    """
    Processes the lyrics for a particular webpage and returns them as a nicely formatted string
    This function is called by convert_lyrics as part of a multiprocessing pool
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    lyrics_elements = soup.find_all("div", class_=LYRIC_CLASS)
    portions = [
        remove_fluff(item.decode_contents().lower()) for item in lyrics_elements
    ]
    return " ".join(re.sub(r"\s+", " ", portion) for portion in portions)


def convert_lyrics(song_links: list[str]) -> str:
    """
    Processes the content of the webpage links lists into neatly formatted lyrics strings.
    """
    print("Processing lyrics...")
    if len(song_links) > 250:
        print("This may take a while...")
    # Multiprocess lyrics
    with Pool() as pool:
        data_set = pool.map(process_lyrics, song_links)
        pool.close()
    return " ".join(data_set)


def build_cloud(data_set: str) -> None:
    """
    Processes the string into a word cloud, which are saved as .png files.
    Files are named after the artist as they appear in the Genius links
    """
    print("Generating word cloud...")
    wordcloud = WordCloud(
        width=1080,
        height=1080,
        background_color="black",
        stopwords=COMBINED_STOPWORDS,
        min_font_size=8,
        max_words=150,
        relative_scaling=0.7,
    ).generate(unidecode(data_set))
    plot.figure(figsize=(8, 8), facecolor=None)
    plot.imshow(wordcloud)
    plot.axis("off")
    plot.tight_layout(pad=0)
    output_name = re.sub(ARTIST_RE, '', unidecode(artist).replace(' ', '-').lower())
    try:
        plot.savefig(fname=f"./OutputClouds/{output_name}.png")
        print(f"Saved word cloud as {output_name}.png!")
    except OSError:
        print(f"Could not save {output_name}.png\nYou may not have access to write in this directory.")


if __name__ == "__main__":
    freeze_support()
    cmd_args = sys.argv[1:]
    try:
        os.mkdir("./OutputClouds/")
    except FileExistsError:
        pass
    if len(cmd_args) == 0:
        while True:
            artist = input("Enter artist name (or press enter to exit): ")
            try:
                if artist == "":
                    break
                song_list = build_song_links(build_artist_page(unidecode(artist)), unidecode(artist))
                build_cloud(convert_lyrics(song_list))
            except ValueError:
                artist = input(
                    f"Artist {artist} could not be found on Genius.\n"
                    f"Please input a new artist or press enter to close the program: "
                )
    else:
        artists = cmd_args
        # Create a list of lists with indices labeled by their names
        for artist in artists:
            try:
                print(f"\n\nCurrent artist: {artist}")
                song_list = build_song_links(build_artist_page(unidecode(artist)), unidecode(artist))
                build_cloud(convert_lyrics(song_list))
            except ValueError:
                print(
                    f"Artist {artist} could not be found on Genius. "
                    f"Please ensure that it is spelled correctly in quotes.",
                    file=sys.stderr,
                )
