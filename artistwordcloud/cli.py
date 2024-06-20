import re
import sys
from artistwordcloud.cloud_core import (
    build_song_links,
    build_artist_page,
    convert_lyrics,
)
from artistwordcloud.constants import ARTIST_RE, COMBINED_STOPWORDS
from multiprocessing import freeze_support
from unidecode import unidecode
from wordcloud import WordCloud


def build_cloud(data_set: str) -> None:
    """
    Processes the string into a word cloud, which are saved as .png files.
    Files are named after the artist as they appear in the Genius links
    """
    print("Generating word cloud...")
    output_name = re.sub(ARTIST_RE, "", unidecode(artist).replace(" ", "-").lower())
    try:
        WordCloud(
            width=1080,
            height=1080,
            background_color="black",
            stopwords=COMBINED_STOPWORDS,
            min_font_size=8,
            max_words=150,
            relative_scaling=0.7,
        ).generate(unidecode(data_set)).to_file(f"{output_name}.png")
        print(f"Saved word cloud as {output_name}.png!")
    except OSError:
        print(
            f"Could not save {output_name}.png\nYou may not have access to write in this directory."
        )


if __name__ == "__main__":
    freeze_support()
    cmd_args = sys.argv[1:]
    if len(cmd_args) == 0:
        while True:
            artist = input("Enter artist name (or press enter to exit): ")
            try:
                if artist == "":
                    break
                decoded_artist = unidecode(artist)
                song_list = build_song_links(
                    build_artist_page(decoded_artist), decoded_artist
                )
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
                decoded_artist = unidecode(artist)
                song_list = build_song_links(
                    build_artist_page(decoded_artist), decoded_artist
                )
                build_cloud(convert_lyrics(song_list))
            except ValueError:
                print(
                    f"Artist {artist} could not be found on Genius. "
                    f"Please ensure that it is spelled correctly in quotes.",
                    file=sys.stderr,
                )
