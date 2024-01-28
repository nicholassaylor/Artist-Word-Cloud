import selenium.common
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from typing import List
from wordcloud import WordCloud, STOPWORDS
from nltk.corpus import stopwords
from multiprocessing import Pool, freeze_support
import nltk
import matplotlib.pyplot as plt
import time
import re
import requests
import sys

# Constants
SECTION_RE = re.compile(r'\[[^\[\]]*]')
HTML_TAG_RE = re.compile(r'(<[^>]*>)+')
CLEAN_PUNC_RE = re.compile(r'[,.?!()\n]')
MAX_COLLECTION_RETRIES = 5
LINK_CLASS = "ListItem__Link-sc-122yj9e-1"

# Globals
global combined_stopwords


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
    constructed_url = re.sub(r'[^a-z0-9-]', '', artist_name.replace(" ", "-").lower())
    return base_url + constructed_url + "/songs"


def build_song_links(artist_page: str) -> List:
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
    # Allow page time to load
    time.sleep(1)
    # The song count can be found in the summary of the songs page
    song_count = driver.find_element(By.CLASS_NAME, "ListSectiondesktop__Summary-sc-53xokv-6.dSgVld")
    # Isolate number in text and cast to integer
    song_count = int(re.sub("[^0-9]", "", song_count.text))
    print(f'{song_count} songs listed, collecting links...')
    if song_count > 500:
        print(f'Warning: Large music libraries may fail to load in their entirety. The program will attempt to'
              f' gather as many lyrics to process as possible.')
    trapped_count = 0
    last_count = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        # Pull only the last link
        current_count = driver.execute_script(
            f"var elements = document.getElementsByClassName('{LINK_CLASS}'); return elements.length;")
        if current_count == last_count and current_count == song_count:
            # Find elements that are contained in the infinite scroll list elements and extract the links
            link_list = [link.get_attribute('href') for link in
                         driver.find_elements(By.CLASS_NAME, LINK_CLASS)
                         if link is not None and link.get_attribute('href') is not None]
            break  # All songs found
        # Handle no new links loading but total size not reached
        elif current_count == last_count and current_count != song_count:
            trapped_count += 1
            if trapped_count == MAX_COLLECTION_RETRIES:
                # If attempts exceeds max tries, abort scraping and return with current collection of links
                link_list = [link.get_attribute('href') for link in
                             driver.find_elements(By.CLASS_NAME, LINK_CLASS)
                             if link is not None and link.get_attribute('href') is not None]
                print(f'Failed collection too many times; continuing with first {len(link_list)} songs')
                break
        # Only reset trap counter if we are getting new links
        else:
            trapped_count = 0
        print(f'Collected {current_count} out of {song_count} song links')
        last_count = current_count
    driver.quit()
    print(f'Finished scraping, found {len(link_list)} songs!')
    return link_list


def process_lyrics(url: str) -> str:
    """
    Processes the lyrics for a particular webpage and returns them as a nicely formatted string
    This is segmented off in order to support multiprocessing in the future
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    lyrics_elements = soup.find_all('div', class_='Lyrics__Container-sc-1ynbvzw-1 kUgSbL')
    portions = [
        remove_fluff(item.decode_contents().lower())
        for item in lyrics_elements
    ]
    return " ".join(re.sub(r'\s+', ' ', portion) for portion in portions)


def convert_lyrics_to_cloud(song_links: List[str]) -> None:
    global combined_stopwords
    print("Processing lyrics...")
    if len(song_links) > 250:
        print("This may take a while...")
    # Multiprocess lyrics
    with Pool() as pool:
        data_set = pool.map(process_lyrics, song_links)
        pool.close()
    data_set = " ".join(data_set)
    print("Generating word cloud...")
    wordcloud = WordCloud(width=1080, height=1080, background_color='black', stopwords=combined_stopwords,
                          min_font_size=8, max_words=125, relative_scaling=0.7).generate(data_set)
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    try:
        plt.savefig(fname=f"{re.sub(r'[^a-z0-9-]', '', artist.replace(' ', '-').lower())}.png")
        print("Saved word cloud as a png file!")
    except OSError:
        print(f"Could not save {re.sub(r'[^a-z0-9-]', '', artist.replace(' ', '-').lower())}.png\n"
              f"You may not have access to write in this directory.")


if __name__ == '__main__':
    freeze_support()
    global combined_stopwords
    # Check if stopwords are downloaded
    try:
        nltk.data.find('corpora/stopwords.zip')
    except LookupError:
        # Download stopwords if not found
        print("Downloading stopwords...")
        nltk.download('stopwords')
    combined_stopwords = set(STOPWORDS) | set(stopwords.words('english'))
    cmd_args = sys.argv[1:]
    if len(cmd_args) == 0:
        artist = input("Enter artist name: ")
        # Error handling for artist name
        while True:
            try:
                song_list = build_song_links(build_artist_page(artist))
                # If artist page is found, will leave prompt loop
                break
            except selenium.common.NoSuchElementException:
                artist = input(f"Artist {artist} could not be found on Genius.\n"
                               f"Please input a new artist or press enter to close the program: ")
                if artist == "":
                    exit(0)
    else:
        artists = cmd_args
        print(artists)
        # Create a list of lists with indices labeled by their names
        for artist in artists:
            try:
                song_list = build_song_links(build_artist_page(artist))
                convert_lyrics_to_cloud(song_list)
            except selenium.common.NoSuchElementException:
                print(f"Artist {artist} could not be found on Genius. "
                      f"Please ensure that it is spelled correctly in quotes.")
                exit(1)
