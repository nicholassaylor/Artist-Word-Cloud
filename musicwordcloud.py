from bs4 import BeautifulSoup as bs
import requests
import re


section_re = re.compile(r'\[.*\]')


def main():
    #TODO: Find url dynamically
    url = 'https://genius.com/Caligulas-horse-the-world-breathes-with-me-lyrics'
    response = requests.get(url)
    soup = bs(response.text, 'html.parser')
    #TODO: Confirm class is consistent between pages
    lyrics_elements = soup.find_all('div', class_='Lyrics__Container-sc-1ynbvzw-1 kUgSbL')
    for item in lyrics_elements:
        print(remove_sections(item.get_text(separator='\n', strip=True)))


def remove_sections(element):
    return re.sub(section_re, '', element)


if __name__ == "__main__":
    main()
