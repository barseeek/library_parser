from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from main import download_txt, download_image, parse_book_page
import json
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Download books from tululu.org.")
    parser.add_argument("--start_page", type=int, default=1)
    parser.add_argument("--end_page", type=int, default=701)
    parser.add_argument("--dest_folder", type=str, default="downloads/")
    parser.add_argument("--skip_imgs", action='store_true')
    parser.add_argument("--skip_txt", action='store_true')

    return parser.parse_args()


def main():
    args = parse_arguments()
    count = 0
    write_to_json=[]
    for page in range(args.start_page, args.end_page + 1):
        download_url = 'http://tululu.org/txt.php'
        url = f'https://tululu.org/l55/{page}'
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        book_tags = soup.select('table.d_book')
        for book_tag in book_tags:
            link_tag = book_tag.select_one('a')['href']
            url_for_parse = urljoin(url, link_tag)
            book_id = link_tag.strip('b/')
            try:
                book_response = requests.get(url_for_parse)
                book_response.raise_for_status()
                book_soup = BeautifulSoup(book_response.text, 'lxml')
                parsed_page = parse_book_page(book_soup)
                img_url = urljoin(url_for_parse, parsed_page["img_src"])
                if not args.skip_imgs:
                    download_image(img_url, args.dest_folder)
                if not args.skip_txt:
                    download_txt(download_url, '{0}. {1}'.format(book_id, parsed_page['title']), args.dest_folder)
                write_to_json.append(parsed_page)
                print(url_for_parse)
            except requests.HTTPError as e:
                print(f"HTTPError with book {book_id}: {e}")
    with open("{0}{1}".format(args.dest_folder,"books.json"), "w", encoding='utf-8') as file:
        json.dump(write_to_json, file, ensure_ascii=False)


if __name__ == "__main__":
    main()
