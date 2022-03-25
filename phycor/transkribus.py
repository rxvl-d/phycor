# Install Transkribus Client w/ pip install --index-url https://test.pypi.org/simple/ --no-deps  TranskribusPyClient

from TranskribusPyClient.client import TranskribusClient
import os
import re
from datetime import datetime
from dateutil import parser
import numpy as np
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
from glob import glob
from PIL import Image
from bs4 import BeautifulSoup

class TranskribusDownloader:
    def __init__(self):
        self.client = TranskribusClient()
        self.region_types = {'graphicregion', 'separatorregion', 'tableregion', 'textregion'}
        self.all_textregion_types = {'paragraph', None}
        self.client.auth_login(os.getenv('TRANSKRIBUS_USER'), os.getenv('TRANSKRIBUS_PASSWORD'))

    def save_data(self, collection_id, doc_id, result_dir):
        book = self.client.getDocById(collection_id, doc_id)
        urls = [(page['pageNr'],
                 page['url'],
                 [ts['url'] for ts in page['tsList']['transcripts']]
                 ) for page in book['pageList']['pages']]
        os.makedirs(page_images_dir(result_dir))
        os.makedirs(page_files_dir(result_dir))
        for page_nr, page_url, page_xml_urls in tqdm(urls):
            with open(page_images_dir(result_dir) + str(page_nr) + '.jpg', 'wb') as f:
                f.write(requests.get(page_url).content)
            for i, page_xml_url in enumerate(page_xml_urls):
                with open(page_files_dir(result_dir) + str(page_nr) + '_' + str(i) + '.xml', 'wb') as f:
                    f.write(requests.get(page_xml_url).content)

class TranskribusParser:
    def __init__(self, data_dir):
        self.page_images_dir = page_images_dir(data_dir)
        self.page_files_dir = page_files_dir(data_dir)

    def is_ocr(self, page_soup):
        return 'PyLaia' in page_soup.find('creator').text

    def created_at(self, page_soup):
        return parser.parse(page_soup.find('created').text)

    def get_last_ocr(self, page_files):
        last_ocr = None
        last_non_ocr = None
        for ps in page_files:
            if self.is_ocr(ps):
                if last_ocr is None:
                    last_ocr = ps
                else:
                    if self.created_at(ps) > self.created_at(last_ocr):
                        last_ocr = ps
            else:
                if last_non_ocr is None:
                    last_non_ocr = ps
                else:
                    if self.created_at(ps) > self.created_at(last_non_ocr):
                        last_non_ocr = ps
        return last_ocr, last_non_ocr

    def area(self, rect):
        ((x_min, y_min), (x_max, y_max)) = rect
        return (x_max - x_min) * (y_max - y_min)

    def bound(self, shape):
        x_max, y_max = np.max(shape, axis=0)
        x_min, y_min = np.min(shape, axis=0)
        return (x_min, y_min), (x_max, y_max)

    def how_in(self, line, textregion):
        line_bound = self.bound(line)
        (line_x_min, line_y_min), (line_x_max, line_y_max) = line_bound
        (tr_x_min, tr_y_min), (tr_x_max, tr_y_max) = self.bound(textregion)
        min_x, min_y = max(line_x_min, tr_x_min), max(line_y_min, tr_y_min)
        max_x, max_y = min(line_x_max, tr_x_max), min(line_y_max, tr_y_max)
        if ((max_x - min_x) > 0) and ((max_y - min_y) > 0):
            intersection = ((min_x, min_y), (max_x, max_y))
            return self.area(intersection) / self.area(line_bound)
        else:
            return None

    def enough_words(self, lines, threshold):
        count = 0
        for line in lines:
            for word in line.split(' '):
                count += 1
                if count > threshold:
                    return True
        return False

    def polygon(self, coords):
        return np.array([[int(a) for a in p.split(',')] for p in coords['points'].split(' ')])

    def page_to_pil(self, points):
        # image.crop(page_to_pil(region.find('coords')['points']))
        left_upper, _, right_lower, _ = points.split(' ')
        left, upper = tuple(map(int, left_upper.split(',')))
        right, lower = tuple(map(int, right_lower.split(',')))
        return left, upper, right, lower

    def get_lines_in_region(self, image, page_files):
        word_threshold = 50
        last_ocr, last_non_ocr = self.get_last_ocr(page_files)
        lines = last_ocr.find_all('textline')
        textregions = [r.find('coords') for r in last_non_ocr.find_all('textregion')]
        lines_in_region = dict()
        for i, region in enumerate(textregions):
            lines_in_region[i] = []
            for line in lines:
                l = self.polygon(line.find('coords'))
                r = self.polygon(region)
                overlap = self.how_in(l, r)
                if overlap and (overlap > 0.90):
                    lines_in_region[i].append(line.findChildren('textequiv', recursive=False)[0].find('unicode').text)

        for region in lines_in_region:
            if self.enough_words(lines_in_region[region], word_threshold):
                crop = image.crop(self.page_to_pil(textregions[region]['points']))
                text = lines_in_region[region]
                yield crop, text

    def get_page_data(self, page_nr):
        image_file = self.page_images_dir + str(page_nr) + '.jpg'
        xml_files = glob(self.page_files_dir  + str(page_nr) + '_*' + '.xml')
        return Image.open(image_file), [soup(f) for f in xml_files]


def soup(fn):
    with open(fn) as f:
        return BeautifulSoup(f)


def page_images_dir(result_dir): return result_dir + '/pages/'
def page_files_dir(result_dir): return result_dir + '/page_files/'
