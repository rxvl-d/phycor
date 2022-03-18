from poppler import load_from_file, PageRenderer
from glob import glob
import numpy as np

class Loader:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.renderer = PageRenderer()

    def list_files(self):
        return glob(self.data_dir + '/books/*.pdf')

    def files(self):
        for filename in self.list_files():
            yield filename, load_from_file(filename)

    def page_images(self):
        for filename, file in self.files():
            for page_index in range(file.pages):
                poppler_image = self.renderer.render_page(file.create_page(page_index))
                image = poppler_to_rgb(poppler_image)
                yield filename.split('/')[-1], page_index, image


def poppler_to_rgb(image):
    a = np.array(image.memoryview(), copy=False)
    a = a[..., :3].astype(np.uint8)
    a = a[..., ::-1]
    return a