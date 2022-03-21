import logging
from functools import lru_cache
from urllib.parse import unquote

import pandas as pd
from flask import Flask, send_file
from flask_cors import CORS
from markupsafe import escape

app = Flask(__name__)
CORS(app)

@app.errorhandler(ValueError)
def handle_bad_request(e):
    logging.error(e)
    return 'bad request!', 400

data_dir = '../data/'

@app.route("/<model>/books.json")
def all_books(model):
    return {'books': get_books(model)}


@app.route("/<model>/page_elements.csv")
def page_elements(model):
    return send_file(page_elements_csv(model))


@app.route("/<model>/book/<book_id>/page/<page_num>.jpg")
def page_image_route(model, book_id, page_num):
    book_filename = unquote(book_id)
    df = pd.read_csv(page_elements_csv(model))
    selected = df[(df.pdf_filename == book_filename) & (df.page_num == int(page_num))]
    if selected.shape[0] == 0:
        return 'page not found', 404
    page_image_filename = selected.page_image.iloc[0]
    return send_file(page_image_jpg(model, page_image_filename))


@app.route("/<model>/book/<book_id>/page/<page_num>.json")
def page_info_route(model, book_id, page_num):
    book_filename = unquote(book_id)
    df = pd.read_csv(page_elements_csv(model))
    selected = df[(df.pdf_filename == book_filename) & (df.page_num == int(page_num))]
    return {'element_count': selected.shape[0]}


@app.route("/<model>/book/<book_id>/page/<page_num>/element/<element_num>.jpg")
def element_image_route(model, book_id, page_num, element_num):
    book_filename = unquote(book_id)
    df = pd.read_csv(page_elements_csv(model))
    selected = df[(df.pdf_filename == book_filename) &
                  (df.page_num == int(page_num)) &
                  (df.el_num == int(element_num))].el_image
    if selected.shape[0] == 0:
        return 'element not found', 404
    return send_file(el_image_jpg(model, selected.iloc[0]))


@app.route("/<model>/book/<book_id>/page/<page_num>/element_ocr/<element_num>.txt")
def element_ocr_route(model, book_id, page_num, element_num):
    book_filename = unquote(book_id)
    df = pd.read_csv(page_elements_csv(model))
    selected = df[(df.pdf_filename == book_filename) &
                  (df.page_num == int(page_num)) &
                  (df.el_num == int(element_num))].el_text
    if selected.shape[0] == 0:
        return 'element not found', 404
    return send_file(el_ocr_txt(model, selected.iloc[0]))


def page_elements_csv(model):
    return data_dir + escape(model) + '/page_elements.csv'


def page_image_jpg(model, page_image_filename):
    return data_dir + escape(model) + '/page_image/' + page_image_filename


def el_image_jpg(model, el_image_filename):
    return data_dir + escape(model) + '/crop_image/' + el_image_filename


def el_ocr_txt(model, el_ocr_filename):
    return data_dir + escape(model) + '/crop_text/' + el_ocr_filename


@lru_cache()
def get_df(model):
    return pd.read_csv(page_elements_csv(model))

@lru_cache()
def get_books(model):
    df = get_df(model)
    books = [{'name': n, 'page_count': c} for n, c in
                       df.groupby('pdf_filename').page_num.max().to_dict().items()]
    return books

@lru_cache()
def book_exists(model, book_id):
    return book_id in [b['name'] for b in get_books(model)]