import requests
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urlparse, urljoin


def check_for_redirect(response):
    if response.history and response.url == "https://tululu.org/":
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
    book_dir = Path(__file__).parent / folder
    book_dir.mkdir(parents=True, exist_ok=True)
    response = requests.get(url)
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
    book_info = {}
    title_tag_text = soup.find('div', id='content').find('h1').text
    title, author = title_tag_text.split("::")
    book_info['title'], book_info['author'] = title.strip(), author.strip()
    book_info['img_src'] = soup.find('div', class_='bookimage').find('img')['src']
    comments = []
    for comment in soup.find_all('div', class_='texts'):
        comments.append(comment.find('span', class_='black').text)
    book_info['comments'] = comments
    genres = []
    for genre in soup.find('span', class_='d_book').find_all('a'):
        genres.append(genre.text)
    book_info['genres'] = genres
    return book_info


def parse_arguments():
    parser = argparse.ArgumentParser(description="Download books from tululu.org.")
    parser.add_argument("start_id", type=int, default=1)
    parser.add_argument("end_id", type=int, default=10)
    return parser.parse_args()


def main():
    args = parse_arguments()
    for book_id in range(args.start_id, args.end_id + 1):
        download_url = f'http://tululu.org/txt.php?id={book_id}'
        try:
            response = requests.get(f'https://tululu.org/b{book_id}/')
            response.raise_for_status()
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            book_info = parse_book_page(soup)
            img_url = urljoin('https://tululu.org', book_info["img_src"])
            download_image(img_url)
            download_txt(download_url, '{0}. {1}'.format(book_id, book_info['title']))
            print(book_info["title"], book_info["author"], sep='\n')
        except requests.HTTPError as e:
            print(f"Error with book_id {book_id}: {e}")


if __name__ == '__main__':
    main()
