from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from parse_books_by_id import download_txt, download_image, parse_book_page, check_for_redirect
import json
import argparse
import logging
import time


DELAY_BETWEEN_ATTEMPTS = 0
MAX_CONNECTION_ATTEMPTS = 2
logging.basicConfig(level=logging.ERROR)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Download books from tululu.org.")
    parser.add_argument("--start_page", type=int, default=1)
    parser.add_argument("--end_page", type=int, default=701)
    parser.add_argument("--dest_folder_txt", type=str, default="media/books/")
    parser.add_argument("--dest_folder_img", type=str, default="media/images/")
    parser.add_argument("--skip_imgs", action='store_true')
    parser.add_argument("--skip_txt", action='store_true')

    return parser.parse_args()



def main():
    args = parse_arguments()
    parsed_books = []
    for page in range(args.start_page, args.end_page + 1):
        download_url = 'http://tululu.org/txt.php'
        url = f'https://tululu.org/l55/{page}'
        attempt = 1
        while attempt < MAX_CONNECTION_ATTEMPTS:
            try:
                response = requests.get(url)
                response.raise_for_status()
                check_for_redirect(response)
                soup = BeautifulSoup(response.text, 'lxml')
                book_tags = soup.select('table.d_book')
                for book_tag in book_tags:
                    book_link = book_tag.select_one('a')['href']
                    url_for_parse = urljoin(url, book_link)
                    book_id = book_link.strip('b/')
                    try:
                        book_response = requests.get(url_for_parse)
                        book_response.raise_for_status()
                        check_for_redirect(book_response)
                        book_soup = BeautifulSoup(book_response.text, 'lxml')
                        parsed_page = parse_book_page(book_soup, book_id)
                        img_url = urljoin(url_for_parse, parsed_page["img_src"])
                        if not args.skip_imgs:
                            download_image(img_url, args.dest_folder_img)
                        if not args.skip_txt:
                            download_txt(download_url, '{0}. {1}'.format(book_id, parsed_page['title']),
                                         args.dest_folder_txt)
                        parsed_books.append(parsed_page)
                    except requests.HTTPError as e:
                        logging.error(f"HTTPError with book {book_id}: {e}")
                    except requests.ConnectionError as e:
                        logging.error(f"Error processing book {book_id}: {e}")
                    time.sleep(DELAY_BETWEEN_ATTEMPTS)
                break
            except requests.HTTPError as e:
                logging.error(f"HTTPError while fetching page {url}, attempt {attempt}: {e}")
            except requests.ConnectionError as e:
                logging.error(f"ConnectionError while fetching page {url}, attempt {attempt}: {e}")
            attempt += 1
            time.sleep(DELAY_BETWEEN_ATTEMPTS)
        else:
            logging.error(f"Max attempts reached for page {url}. Skipping...")

    with open("books.json", "w", encoding='utf-8') as file:
        json.dump(parsed_books, file, ensure_ascii=False)


if __name__ == "__main__":
    main()
