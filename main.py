import requests
from pathlib import Path


def check_for_redirect(response):
    if response.history and response.url == "https://tululu.org/":
        raise requests.HTTPError("Book isn't exist")


def main():
    book_dir = Path(__file__).parent / "books"
    book_dir.mkdir(parents=True, exist_ok=True)
    for book_id in range(1, 11):
        url = f"https://tululu.org/txt.php?id={book_id}"
        response = requests.get(url)
        response.raise_for_status()
        try:
            check_for_redirect(response)
            filename = book_dir / 'book_{0}.txt'.format(book_id)
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(response.text)
        except requests.HTTPError as e:
            print(f"Error downloading book {book_id}: {e}")  


if __name__ == '__main__':
    main()
