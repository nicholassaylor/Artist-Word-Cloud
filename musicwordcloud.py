from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from typing import List
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import time
import re
import requests


# Constants
SECTION_RE = re.compile(r'\[[^\[\]]*]')
HTML_TAG_RE = re.compile(r'(<[^>]*>)+')
CLEAN_PUNC_RE = re.compile(r'[,.?!()\n]')
MAX_COLLECTION_RETRIES = 10

# Globals
global artist
global song_list
song_list: List[str]


def main():
    global artist
    artist = input("Enter artist name: ")
    build_song_links(build_artist_page())
    data_set = ""
    #TODO: Use NLTK stopwords as well?
    stopwords = set(STOPWORDS)
    print("Processing lyrics...")
    for url in song_list:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        lyrics_elements = soup.find_all('div', class_='Lyrics__Container-sc-1ynbvzw-1 kUgSbL')
        for item in lyrics_elements:
            portion = remove_fluff(item.decode_contents().lower())
            data_set += " " + re.sub(r'\s+', ' ', portion) + " "
        print(f'Processed {song_list.index(url) + 1} of {len(song_list)} songs')
    print("Generating word cloud...")
    wordcloud = WordCloud(width=1080, height=1080, background_color='black', stopwords=stopwords,
                          min_font_size=8, max_words=125, relative_scaling=0.7).generate(data_set)
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.show()


def remove_fluff(element) -> str:
    """Removes html tags, section names, and additional non-lyric text from lyrics"""
    element = re.sub(HTML_TAG_RE, ' ', element)
    element = re.sub(SECTION_RE, '', element)
    return re.sub(CLEAN_PUNC_RE, '', element).replace('\n', ' ')


def build_artist_page() -> str:
    global artist
    base_url = "https://genius.com/artists/"
    constructed_url = re.sub(r'[^a-zA-Z0-9-]', '', artist.replace(" ", "-").lower())
    return base_url + constructed_url + "/songs"


def build_song_links(artist_page: str) -> None:
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
    song_count = driver.find_element(By.CLASS_NAME, "ListSectiondesktop__Summary-sc-53xokv-6.dSgVld")
    song_count = int(re.sub("[^0-9]", "", song_count.text))
    print(f'{song_count} songs listed, collecting links...')
    previous_count, trapped_count = 0, 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        # Find elements that are contained in the infinite scroll list elements and extract the links
        # This prevents false positives like the featured songs on the page or popular songs in the footer
        song_list = [link.get_attribute('href') for link in
                     driver.find_elements(By.CLASS_NAME, "ListItem__Link-sc-122yj9e-1.klWOzg")
                     if link is not None and link.get_attribute('href') is not None]
        if len(song_list) == song_count:
            break  # All songs found
        # Check to make sure that we are actually getting new songs each attempt
        if previous_count == len(song_list):
            trapped_count += 1
            if trapped_count == MAX_COLLECTION_RETRIES:
                # If attempts exceeds max tries, abort scraping and return with current collection of links
                print(f'Failed collection too many times; continuing with first {len(song_list)} songs')
                break
        else:
            # No need to update these variables if we failed a collection cycle
            trapped_count = 0
            previous_count = len(song_list)
        print(f'Collected {len(song_list)} out of {song_count} song links')
    driver.quit()
    print(f'Finished scraping, found {len(song_list)} songs!')


if __name__ == "__main__":
    main()
