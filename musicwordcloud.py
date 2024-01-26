from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from typing import List
from wordcloud import WordCloud, STOPWORDS
from nltk.corpus import stopwords
from multiprocessing import Pool, freeze_support
import multiprocessing
import nltk
import matplotlib.pyplot as plt
import time
import re
import requests

# Constants
SECTION_RE = re.compile(r'\[[^\[\]]*]')
HTML_TAG_RE = re.compile(r'(<[^>]*>)+')
CLEAN_PUNC_RE = re.compile(r'[,.?!()\n]')
MAX_COLLECTION_RETRIES = 5
LINK_CLASS = "ListItem__Link-sc-122yj9e-1"

# Globals
global artist
global song_list
song_list: List[str]


def remove_fluff(element) -> str:
    """Removes html tags, section names, and additional non-lyric text from lyrics"""
    element = re.sub(HTML_TAG_RE, ' ', element)
    element = re.sub(SECTION_RE, '', element)
    return re.sub(CLEAN_PUNC_RE, '', element).replace('\n', ' ')


def build_artist_page() -> str:
    """Returns a constructed link of an artist's Genius page"""
    global artist
    base_url = "https://genius.com/artists/"
    # Non-alphanumeric characters are excluded from Genius links, they are effectively replaced with ''
    # Spaces are replaced with '-'
    constructed_url = re.sub(r'[^a-zA-Z0-9-]', '', artist.replace(" ", "-").lower())
    return base_url + constructed_url + "/songs"


def build_song_links(artist_page: str) -> None:
    """
    Compiles a list of song links associated to a particular artist and saves it to song_list
    Pulls data from Genius's songs page using a Selenium webdriver
    """
    global artist
    global song_list
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
            song_list = [link.get_attribute('href') for link in
                         driver.find_elements(By.CLASS_NAME, LINK_CLASS)
                         if link is not None and link.get_attribute('href') is not None]
            break  # All songs found
        # Handle no new links loading but total size not reached
        elif current_count == last_count and current_count != song_count:
            trapped_count += 1
            if trapped_count == MAX_COLLECTION_RETRIES:
                # If attempts exceeds max tries, abort scraping and return with current collection of links
                song_list = [link.get_attribute('href') for link in
                             driver.find_elements(By.CLASS_NAME, LINK_CLASS)
                             if link is not None and link.get_attribute('href') is not None]
                print(f'Failed collection too many times; continuing with first {len(song_list)} songs')
                break
        # Only reset trap counter if we are getting new links
        else:
            trapped_count = 0
        print(f'Collected {current_count} out of {song_count} song links')
        last_count = current_count
    driver.quit()
    print(f'Finished scraping, found {len(song_list)} songs!')


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


if __name__ == '__main__':
    freeze_support()
    #  Tracks how many lyrics are done processing
    total_completed = multiprocessing.Value('i', 0)
    song_list = []
    artist = input("Enter artist name: ")
    build_song_links(build_artist_page())
    data_set = ""
    # Check if stopwords are downloaded
    try:
        nltk.data.find('corpora/stopwords.zip')
    except LookupError:
        # Download stopwords if not found
        print("Downloading stopwords...")
        nltk.download('stopwords')
    combined_stopwords = set(STOPWORDS) | set(stopwords.words('english'))
    print("Processing lyrics...")
    if len(song_list) > 250:
        print("This may take a while...")
    # Multiprocess lyrics
    with Pool() as pool:
        data_set = pool.map(process_lyrics, song_list)
        pool.close()
    data_set = " ".join(data_set)
    print("Generating word cloud...")
    wordcloud = WordCloud(width=1080, height=1080, background_color='black', stopwords=combined_stopwords,
                          min_font_size=8, max_words=125, relative_scaling=0.7).generate(data_set)
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.show()
