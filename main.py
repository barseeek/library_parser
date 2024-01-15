import requests
from pathlib import Path


def main():
    book_dir = Path(__file__).parent / "books"
    book_dir.mkdir(parents=True, exist_ok=True)
    for book_id in range(1, 11):
        url = f"https://tululu.org/txt.php?id={book_id}"
        response = requests.get(url)
        response.raise_for_status()
        filename = book_dir / 'book_{0}.txt'.format(book_id)
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(response.text)


if __name__ == '__main__':
    main()
