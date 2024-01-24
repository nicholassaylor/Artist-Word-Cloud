from bs4 import BeautifulSoup as bs
import requests
import re


section_re = re.compile(r'\[[^\[\]]*\]')
html_tag_re = re.compile(r'(\<[^>]*\>)+')


def main():
    #TODO: Find url dynamically
    #url = 'https://genius.com/Caligulas-horse-the-world-breathes-with-me-lyrics'
    #url = 'https://genius.com/Nwa-fuck-tha-police-lyrics'
    url = 'https://genius.com/Eminem-lose-yourself-lyrics'
    response = requests.get(url)
    soup = bs(response.text, 'html.parser')
    lyrics_elements = soup.find_all('div', class_='Lyrics__Container-sc-1ynbvzw-1 kUgSbL')
    for item in lyrics_elements:
        print(remove_fluff(item.decode_contents()))


def remove_fluff(element):
    """Removes html tags, section names, and additional non-lyric text from lyrics"""
    element = re.sub(html_tag_re, ' ', element)
    return re.sub(section_re, '', element)


if __name__ == "__main__":
    main()
