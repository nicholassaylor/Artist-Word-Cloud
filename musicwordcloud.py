from bs4 import BeautifulSoup as bs
import requests


def main():
    url = 'https://genius.com/Caligulas-horse-the-world-breathes-with-me-lyrics'
    response = requests.get(url)
    soup = bs(response.text, 'html.parser')
    lyrics_elements = soup.find_all('div', class_='Lyrics__Container-sc-1ynbvzw-1 kUgSbL')
    for item in lyrics_elements:
        print(item.get_text(separator='\n', strip=True))


if __name__ == "__main__":
    main()
