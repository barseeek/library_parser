import requests
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urlparse, urljoin
import time


DELAY_BETWEEN_ATTEMPTS = 5
MAX_CONNECTION_ATTEMPTS = 5


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError("Book isn't exist")


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.

    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    params = {'id': filename.split('.')[0]}
    book_dir = Path(__file__).parent / folder
    book_dir.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    name = f'{sanitize_filename(filename)}.txt'
    filepath = Path(folder, name)
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(response.text)
    return filepath


def download_image(url, folder='images/'):
    """Функция для скачивания картинок.

    Args:
        url (str): Cсылка на картинку, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранена картинка.
    """
    image_dir = Path(__file__).parent / folder
    image_dir.mkdir(parents=True, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    name = urlparse(url).path.split("/")[-1]
    filepath = Path(folder, name)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def parse_book_page(soup):
    title_tag_text = soup.select_one('div#content > h1').text
    title, author = title_tag_text.split("::")
    comments = [comment.select_one('span.black').text for comment in soup.select('div.texts')]
    genres = [genre.text for genre in soup.select('span.d_book a')]
    img_src = soup.select_one('div.bookimage img')['src']
    parsed_page = {
        'title': title.strip(),
        'author': author.strip(),
        'img_src': img_src,
        'comments': comments,
        'genres': genres
    }
    return parsed_page


def parse_arguments():
    parser = argparse.ArgumentParser(description="Download books from tululu.org.")
    parser.add_argument("start_id", type=int, default=1)
    parser.add_argument("end_id", type=int, default=10)
    return parser.parse_args()


def main():
    args = parse_arguments()
    for book_id in range(args.start_id, args.end_id + 1):
        download_url = 'http://tululu.org/txt.php'
        url_for_parse = f'https://tululu.org/b{book_id}/'
        attempt = 1
        while attempt <= MAX_CONNECTION_ATTEMPTS:
            try:
                response = requests.get(url_for_parse)
                response.raise_for_status()
                check_for_redirect(response)
                soup = BeautifulSoup(response.text, 'lxml')
                parsed_page = parse_book_page(soup)
                img_url = urljoin(url_for_parse, parsed_page["img_src"])
                download_image(img_url)
                download_txt(download_url, '{0}. {1}'.format(book_id, parsed_page['title']))
                print("Название:", parsed_page["title"])
                print("Автор:", parsed_page["author"])
                break
            except requests.HTTPError as e:
                print(f"HTTPError with book_id {book_id}: {e}")
                break
            except requests.ConnectionError as e:
                print(f"Connection error with book_id {book_id}: {e}")
                if attempt == 1:
                    pass
                elif attempt < MAX_CONNECTION_ATTEMPTS:
                    print(f"Retry attempt {attempt} in 5 seconds...")
                    time.sleep(DELAY_BETWEEN_ATTEMPTS)
                else:
                    print("Max attempts reached. Skipping book.")
            finally:
                attempt += 1


if __name__ == '__main__':
    main()
