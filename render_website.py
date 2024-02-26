import argparse
import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


BOOKS_PER_ROW = 2
BOOKS_PER_PAGE = 20


def parse_arguments():
    parser = argparse.ArgumentParser(description="Create html pages with books from tululu.org.")
    parser.add_argument("--filepath", type=str, default="books.json", help="Path to JSON file")
    return parser.parse_args()


def generate_pages(books_per_page, books, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    books_pages = list(chunked(books, books_per_page))

    for page_number, books_page in enumerate(books_pages, start=1):
        page_filename = f"{folder}/index{page_number}.html"
        with open(page_filename, "w", encoding="utf8") as file:
            rendered_page = template.render(books=chunked(books_page, BOOKS_PER_ROW), folder_txt="books",
                                            folder_img="images", total_pages=len(books_pages), current_page=page_number)
            file.write(rendered_page)


def on_reload():
    args = parse_arguments()
    with open(args.filepath, "r", encoding="utf8") as json_file:
        books = json.load(json_file)
    generate_pages(BOOKS_PER_PAGE, books, "pages")


env = Environment(
    loader=FileSystemLoader("."),
    autoescape=select_autoescape(["html", "xml"])
)
template = env.get_template("templates/index.html")

on_reload()
server = Server()
server.watch("templates/index.html", on_reload)
server.serve(root=".")
