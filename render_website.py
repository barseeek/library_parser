import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked
import os


def generate_pages(books_per_page, books, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    books_pages = list(chunked(books, books_per_page))

    for i, books_page in enumerate(books_pages, start=1):
        page_filename = f'{folder}/index{i}.html'
        with open(page_filename, 'w', encoding="utf8") as file:
            rendered_page = template.render(books=chunked(books_page, 2), folder='downloads')
            file.write(rendered_page)


def on_reload():
    with open('downloads/books.json', 'r', encoding="utf8") as json_file:
        books = json.load(json_file)
    generate_pages(20, books, 'pages')


env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)
template = env.get_template('templates/index.html')

on_reload()
server = Server()
server.watch('templates/index.html', on_reload)
server.serve(root='.')
