import selenium.common
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from typing import List
from wordcloud import WordCloud
from multiprocessing import Pool, freeze_support
from unidecode import unidecode
from stopwords import COMBINED_STOPWORDS
import matplotlib.pyplot as plt
from html_classes import *
import time
import re
import requests
import sys

# Constants
SECTION_RE = re.compile(r'\[[^\[\]]*]')
HTML_TAG_RE = re.compile(r'(<[^>]*>)+')
CLEAN_PUNC_RE = re.compile(r'[,.?!()\n]')
ARTIST_RE = re.compile(r'[^a-z0-9-]')
MAX_COLLECTION_RETRIES = 5


def remove_fluff(element) -> str:
    """Removes html tags, section names, and additional non-lyric text from lyrics"""
    element = re.sub(HTML_TAG_RE, ' ', element)
    element = re.sub(SECTION_RE, '', element)
    return re.sub(CLEAN_PUNC_RE, '', element).replace('\n', ' ')


def build_artist_page(artist_name: str) -> str:
    """Returns a constructed link of an artist's Genius page"""
    base_url = "https://genius.com/artists/"
    # Non-alphanumeric characters are excluded from Genius links, they are effectively replaced with ''
    # Spaces are replaced with '-'
    constructed_url = re.sub(ARTIST_RE, '', artist_name.replace(" ", "-").lower())
    return base_url + constructed_url + "/songs"


def build_song_links(artist_page: str, artist_name: str) -> List:
    """
    Compiles a list of song links associated to a particular artist and saves it to song_list
    Pulls data from Genius's songs page using a Selenium webdriver
    """
    print('Starting browser...')
    # Configure settings for webdriver
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')  # Disable GPU acceleration to avoid some issues
    driver = webdriver.Firefox(options=options)
    driver.get(artist_page)
    print("Determining song library...")
    time.sleep(1)
    # The song count can be found in the summary of the songs page
    song_count = driver.find_element(By.CLASS_NAME, SUMMARY_CLASS)
    # Isolate number in text and cast to integer
    song_count = int(re.sub("[^0-9]", "", song_count.text))
    print(f'{song_count} songs listed, collecting links...')
    if song_count > 200:
        print(f'Warning: Large music libraries may fail to load in their entirety. The program will attempt to'
              f' gather as many lyrics to process as possible.')
    trapped_count, last_count = 0, 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        # Pull only the last link
        current_count = driver.execute_script(
            f"var elements = document.getElementsByClassName('{LINK_CLASS}'); return elements.length;")
        # Found all songs case
        if current_count == last_count and current_count == song_count:
            link_list = [link.get_attribute('href') for link in
                         driver.find_elements(By.CLASS_NAME, LINK_CLASS)
                         if link is not None and link.get_attribute('href') is not None]
            break
        # Failed load case
        elif current_count == last_count:
            trapped_count += 1
            # Failed load too many times case
            if trapped_count == MAX_COLLECTION_RETRIES:
                link_list = [link.get_attribute('href') for link in
                             driver.find_elements(By.CLASS_NAME, LINK_CLASS)
                             if link is not None and link.get_attribute('href') is not None]
                print(f'Genius failed to load more songs; continuing with first {len(link_list)} songs')
                break
        # Only reset trap counter if we are getting new links
        else:
            trapped_count = 0
        print(f'Collected {current_count} out of {song_count} song links')
        last_count = current_count
    # Clean up scraping
    driver.quit()
    print(f'Finished scraping, found {len(link_list)} songs!')
    # Remove links from unrelated artists/interviews (apparently an issue on larger artists)
    print('Validating links...')
    pattern = (rf"https?://genius\.com/{re.sub(ARTIST_RE, '', artist_name.replace(' ', '-').lower())}"
               r".*-(lyrics|annotated)$")
    filtered_links = []
    for item in link_list:
        if re.match(pattern, item, re.IGNORECASE) is not None:
            filtered_links.append(item)
    print(f"Removed {song_count - len(filtered_links)} invalid links; continuing with {len(filtered_links)} songs")
    return filtered_links


def process_lyrics(url: str) -> str:
    """
    Processes the lyrics for a particular webpage and returns them as a nicely formatted string
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    lyrics_elements = soup.find_all('div', class_=LYRIC_CLASS)
    portions = [
        remove_fluff(item.decode_contents().lower())
        for item in lyrics_elements
    ]
    return " ".join(re.sub(r'\s+', ' ', portion) for portion in portions)


def convert_lyrics(song_links: List[str]) -> str:
    """
    Processes the links in the lists into neatly formatted lyrics strings.
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
    wordcloud = WordCloud(width=1080, height=1080, background_color='black', stopwords=COMBINED_STOPWORDS,
                          min_font_size=8, max_words=125, relative_scaling=0.7).generate(unidecode(data_set))
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    try:
        plt.savefig(fname=f"{re.sub(ARTIST_RE, '', unidecode(artist).replace(' ', '-').lower())}.png")
        print(f"Saved word cloud as {re.sub(ARTIST_RE, '', unidecode(artist).replace(' ', '-').lower())}.png !")
    except OSError:
        print(f"Could not save {re.sub(ARTIST_RE, '', unidecode(artist).replace(' ', '-').lower())}.png\n"
              f"You may not have access to write in this directory.")


if __name__ == '__main__':
    freeze_support()
    cmd_args = sys.argv[1:]
    if len(cmd_args) == 0:
        artist = input("Enter artist name: ")
        # Error handling for artist name
        while True:
            try:
                song_list = build_song_links(build_artist_page(unidecode(artist)), unidecode(artist))
                build_cloud(convert_lyrics(song_list))
                break
            except selenium.common.NoSuchElementException:
                artist = input(f"Artist {artist} could not be found on Genius.\n"
                               f"Please input a new artist or press enter to close the program: ")
                if artist == "":
                    break
    else:
        artists = cmd_args
        # Create a list of lists with indices labeled by their names
        for artist in artists:
            try:
                print(f"\n\nCurrent artist: {artist}")
                song_list = build_song_links(build_artist_page(unidecode(artist)), unidecode(artist))
                build_cloud(convert_lyrics(song_list))
            except selenium.common.NoSuchElementException:
                print(f"Artist {artist} could not be found on Genius. "
                      f"Please ensure that it is spelled correctly in quotes.", file=sys.stderr)
