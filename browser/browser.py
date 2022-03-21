from functools import lru_cache

import pandas as pd
from flask import Flask, render_template, send_file, jsonify, abort
from markupsafe import escape
from urllib.parse import unquote
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

data_dir = '../data/'

@app.route("/<model>/books.json")
def all_books(model):
    df = get_df(model)
    return {'books': [{'name': n, 'page_count': c} for n, c in
            df.groupby('pdf_filename').page_num.max().to_dict().items()]}


@app.route("/<model>/page_elements.csv")
def page_elements(model):
    return send_file(page_elements_csv(model))

@app.route("/<model>/book/<book_id>.json")
def book_route(model, book_id):
    book_filename = unquote(book_id)
    df = get_df(model)
    page_count = df[df.pdf_filename == book_filename].shape[0]
    return {'page_count': page_count}



@app.route("/<model>/book/<book_id>/page/<page_num>.jpg")
def page_image_route(model, book_id, page_num):
    book_filename = unquote(book_id)
    df = pd.read_csv(page_elements_csv(model))
    print(book_filename, page_num)
    selected = df[(df.pdf_filename == book_filename) & (df.page_num == int(page_num))]
    if selected.shape[0] == 0:
        return 'page not found', 404
    page_image_filename = selected.page_image.iloc[0]
    return send_file(page_image_jpg(model, page_image_filename))


@app.route("/<model>/book/<book_id>/page/<page_num>/element/<element_num>.jpg")
def element_image_route(model, book_id, page_num, element_num):
    book_filename = unquote(book_id)
    df = pd.read_csv(page_elements_csv(model))
    el_image_filename = df[(df.pdf_filename == book_filename) &
                           (df.page_num == int(page_num)) &
                           (df.el_num == element_num)].el_image.iloc[0]
    return send_file(el_image_jpg(model, el_image_filename))


@app.route("/<model>/book/<book_id>/page/<page_num>/element_ocr/<element_num>.txt")
def element_ocr_route(model, book_id, page_num, element_num):
    book_filename = unquote(book_id)
    df = pd.read_csv(page_elements_csv(model))
    el_txt_filename = df[(df.pdf_filename == book_filename) &
                         (df.page_num == page_num) &
                         (df.el_num == element_num)].el_txt.iloc[0]
    return send_file(el_ocr_txt(model, el_txt_filename))


def page_elements_csv(model):
    return data_dir + escape(model) + '/page_elements.csv'


def page_image_jpg(model, page_image_filename):
    return data_dir + escape(model) + '/page_image/' + page_image_filename


def el_image_jpg(model, el_image_filename):
    return data_dir + escape(model) + '/crop_image/' + el_image_filename


def el_ocr_txt(model, el_ocr_filename):
    return data_dir + escape(model) + '/crop_text/' + el_ocr_filename


@lru_cache(maxsize=1)
def get_df(model):
    return pd.read_csv(page_elements_csv(model))
