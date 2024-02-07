from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from main import download_txt, download_image, parse_book_page
import json


count = 0
write_to_json=[]
for page in range(1,2):
    download_url = 'http://tululu.org/txt.php'
    url = f'https://tululu.org/l55/{page}'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    book_tags = soup.find_all('table', class_='d_book')
    for book_tag in book_tags:

        link_tag = book_tag.find('a')['href']
        url_for_parse = urljoin(url, link_tag)
        try:
            book_response = requests.get(url_for_parse)
            book_response.raise_for_status()
            book_soup = BeautifulSoup(book_response.text, 'lxml')
            parsed_page = parse_book_page(book_soup)
            count += 1
            img_url = urljoin(url_for_parse, parsed_page["img_src"])
            download_image(img_url)
            download_txt(download_url, '{0}-я книга. {1}'.format(count, parsed_page['title']))
            write_to_json.append(parsed_page)
            print(url_for_parse)
        except requests.HTTPError as e:
            print(f"HTTPError with book: {e}")
with open("books.json", "w", encoding='utf-8') as file:
    json.dump(write_to_json, file, ensure_ascii=False)