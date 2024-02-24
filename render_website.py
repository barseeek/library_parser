import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked

def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    with open('downloads/books.json', 'r', encoding="utf8") as json_file:
        books = json.load(json_file)
        chunked_books = list(chunked(books, 2))
    template = env.get_template('templates/index.html')
    rendered_page = template.render(books=chunked_books, folder='downloads')

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


on_reload()
server = Server()
server.watch('templates/index.html', on_reload)
server.serve(root='.')
