from poppler import load_from_file, PageRenderer
from poppler.rectangle import Rectangle
from poppler.page import Page
from glob import glob
import numpy as np
from tqdm import tqdm


class Loader:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.renderer = PageRenderer()

    def list_files(self):
        return glob(self.data_dir + '/books/*.pdf')

    def files(self, verbose):
        for filename in tqdm(self.list_files(), desc='overall') if verbose else self.list_files():
            yield filename, load_from_file(filename)

    def page_images(self, verbose):
        for filename, file in self.files(verbose):
            for page_index in self.pages_progress(filename, file.pages, verbose):
                page = file.create_page(page_index)
                page_text = page.text()
                poppler_image = self.renderer.render_page(page)
                image = poppler_to_rgb(poppler_image)
                yield filename.split('/')[-1], page_index, page, image, page_text

    def pages_progress(self, filename, page_count, verbose):
        return tqdm(range(page_count), total=page_count, desc=filename) if verbose else range(page_count)

    def get_doc_text(self, page: Page, bb: tuple):
        """bb expected to be x,y,width,height"""
        return page.text(Rectangle(*bb))


def poppler_to_rgb(image):
    a = np.array(image.memoryview(), copy=False)
    a = a[..., :3].astype(np.uint8)
    a = a[..., ::-1]
    return a