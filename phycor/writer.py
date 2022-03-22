import os

import pandas as pd
from PIL.Image import Image


class Writer:
    def __init__(self, results_dir):
        self.results_dir = results_dir
        self.page_image_dir = self.results_dir + 'page_image/'
        self.crop_image_dir = self.results_dir + 'crop_image/'
        self.tes_text_dir = self.results_dir + 'crop_text_tes/'
        self.doc_text_dir = self.results_dir + 'crop_text_doc/'
        if os.path.isdir(self.results_dir):
            raise Exception("Results dir already exists. Backup and empty.")
        else:
            os.makedirs(self.results_dir)
            os.makedirs(self.page_image_dir)
            os.makedirs(self.crop_image_dir)
            os.makedirs(self.tes_text_dir)
            os.makedirs(self.doc_text_dir)
        self.results = []

    def write(self, filename: str, page_index: int, el_idx: int, el_type: str,
              score: float, source_image: Image, crop: Image, orc_text_terreract: str,
              orc_text_doc: str):
        page_image_filename = self.write_page_image(filename, page_index, source_image)
        crop_image_filename = self.write_crop_image(filename, page_index, el_idx, crop)
        tes_text_filename = self.write_crop_text_tesseract(filename, page_index, el_idx, orc_text_terreract)
        doc_text_filename = self.write_crop_text_doc(filename, page_index, el_idx, orc_text_doc)
        self.results.append((filename, page_index, el_idx, el_type, score,
                             page_image_filename, crop_image_filename, tes_text_filename, doc_text_filename))

    def finalize(self):
        pd.DataFrame(self.results,
                     columns=['pdf_filename', 'page_num', 'el_num', 'el_type', 'el_score',
                              'page_image', 'el_image', 'el_text_tes', 'el_text_doc']
                     ).to_csv(self.results_dir + 'page_elements.csv')

    def write_page_image(self, filename: str, page_index: int, source_image: Image):
        dest_filename = filename.replace('.pdf', '') + '_' + str(page_index) + '.jpg'
        dest_path = self.page_image_dir + dest_filename
        if not os.path.isfile(dest_path):
            source_image.save(dest_path)
        return dest_filename

    def write_crop_image(self, filename: str, page_index: int, el_idx: int, crop: Image):
        crop_filename = filename.replace('.pdf', '') + '_' + str(page_index) + '_' + str(el_idx) + '.jpg'
        dest_path = self.crop_image_dir + crop_filename
        if not os.path.isfile(dest_path):
            crop.save(dest_path)
        return crop_filename

    def write_crop_text_tesseract(self, filename: str, page_index: int, el_idx: int, crop_text: str):
        crop_text_filename = filename.replace('.pdf', '') + '_' + str(page_index) + '_' + str(el_idx) + '.txt'
        dest_path = self.tes_text_dir + crop_text_filename
        if not os.path.isfile(dest_path):
            with open(dest_path, 'w') as f:
                f.write(crop_text)
        return crop_text_filename

    def write_crop_text_doc(self, filename: str, page_index: int, el_idx: int, crop_text: str):
        crop_text_filename = filename.replace('.pdf', '') + '_' + str(page_index) + '_' + str(el_idx) + '.txt'
        dest_path = self.doc_text_dir + crop_text_filename
        if not os.path.isfile(dest_path):
            with open(dest_path, 'w') as f:
                f.write(crop_text)
        return crop_text_filename