import re
import sys
from artistwordcloud.cloud_core import cloud_hook
from artistwordcloud.constants import ARTIST_RE
from multiprocessing import freeze_support
from unidecode import unidecode
from wordcloud import WordCloud


if __name__ == "__main__":
    freeze_support()
    cmd_args = sys.argv[1:]
    # Ran through double click or no CLI arguments
    if len(cmd_args) == 0:
        while True:
            artist = input("Enter artist name (or press enter to exit): ")
            output_name = ""
            if artist == "":
                break
            try:
                output_name = re.sub(
                    ARTIST_RE, "", unidecode(artist).replace(" ", "-").lower()
                )
                cloud: WordCloud = cloud_hook(artist)
                cloud.to_file(f"{output_name}.png")
                print(f"Saved word cloud as {output_name}.png!")
            except ValueError:
                artist = input(
                    f"Artist {artist} could not be found on Genius.\n"
                    f"Please input a new artist or press enter to close the program: "
                )
            except OSError:
                print(
                    f"Could not save {(output_name + '.png') if (output_name is not None) else 'file'}\nYou may not have access to write in this directory."
                )
    else:
        artists = cmd_args
        # Create a list of lists with indices labeled by their names
        for artist in artists:
            print(f"\n\nCurrent artist: {artist}")
            output_name = ""
            try:
                output_name = re.sub(
                    ARTIST_RE, "", unidecode(artist).replace(" ", "-").lower()
                )
                cloud: WordCloud = cloud_hook(artist)
                cloud.to_file(f"{output_name}.png")
                print(f"Saved word cloud as {output_name}.png!")
            except ValueError:
                print(
                    f"Artist {artist} could not be found on Genius. "
                    f"Please ensure that it is spelled correctly in quotes.",
                    file=sys.stderr,
                )
            except OSError:
                print(
                    f"Could not save {(output_name + '.png') if (output_name is not None) else 'file'}\nYou may not have access to write in this directory."
                )
