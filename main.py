import requests
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

def parse_books(url):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag_text = soup.find('div', id='content').find('h1').text
    img_src = soup.find('div', class_='bookimage').find('img')['src']
    title, author = title_tag_text.split("::")
    title, author = title.strip(), author.strip()
    return title, author, img_src


def main():
    for book_id in range(1, 11):
        download_url = f'http://tululu.org/txt.php?id={book_id}'
        parse_url = f'https://tululu.org/b{book_id}/'
        try:
            title, author, img_src = parse_books(parse_url)
            img_url = urljoin('https://tululu.org', img_src)
            download_image(img_url)
            print(title, img_url, sep='\n')
            #filepath = download_txt(download_url, '{0}. {1}'.format(book_id, parse_books(parse_url)))
        except requests.HTTPError as e:
            print(f"Error with book_id {book_id}: {e}")


if __name__ == '__main__':
    main()
