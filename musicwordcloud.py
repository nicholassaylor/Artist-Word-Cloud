from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from typing import List
import time
import re
import requests


# Constants
SECTION_RE = re.compile(r'\[[^\[\]]*]')
HTML_TAG_RE = re.compile(r'(<[^>]*>)+')
CLEAN_PUNC_RE = re.compile(r'[,.?!()\n]')

# Globals
global artist
global song_list
song_list: List[str]


def main():
    global artist
    artist = input("Enter artist name: ")
    build_song_links(build_artist_page())
    for url in song_list:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        lyrics_elements = soup.find_all('div', class_='Lyrics__Container-sc-1ynbvzw-1 kUgSbL')
        for item in lyrics_elements:
            print(remove_fluff(item.decode_contents()))


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
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')  # Disable GPU acceleration to avoid some issues
    driver = webdriver.Firefox(options=options)
    driver.get(artist_page)
    # Get the initial page height
    initial_page_height = driver.execute_script(
        "return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight,"
        " document.documentElement.scrollHeight, document.documentElement.offsetHeight);")
    # Scroll down until no new HTML is revealed
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        # Get the updated page height
        updated_page_height = driver.execute_script(
            "return Math.max(document.body.scrollHeight, document.body.offsetHeight, "
            "document.documentElement.clientHeight, document.documentElement.scrollHeight, "
            "document.documentElement.offsetHeight);")
        if updated_page_height == initial_page_height:
            break  # No new content loaded, exit the loop
        initial_page_height = updated_page_height
    link_stub = "https://genius.com/" + re.sub(r'[^a-zA-Z0-9-]', '', artist.replace(" ", "-").lower())
    response = [link.get_attribute('href') for link in driver.find_elements(By.TAG_NAME, 'a')
                if link is not None and link.get_attribute('href') is not None]
    # Extracts only song link while excluding duplicates (3 featured songs at top of page)
    response = list(dict.fromkeys([href for href in response if link_stub.lower() in href.lower()]))
    song_list = response
    driver.quit()
    print(f'Finished scraping! Found {len(song_list)} songs!')


if __name__ == "__main__":
    main()
