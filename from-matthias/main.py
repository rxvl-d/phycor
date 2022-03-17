import os
import sys
import re
import argparse

import numpy as np

from poppler import load_from_file, PageRenderer
import pytesseract
import imageio

from PIL import Image
import layoutparser as lp


def parse_args():
    parser = argparse.ArgumentParser(description="")

    parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")
    parser.add_argument("-i", "--input_path", help="verbose output")
    parser.add_argument("-o", "--output_path", help="verbose output")
    parser.add_argument("-m", "--max_num_pages", type=int, help="verbose output")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    pdf_document = load_from_file(args.input_path)

    if args.max_num_pages:
        num_pages = min(args.max_num_pages, pdf_document.pages)
    else:
        num_pages = pdf_document.pages
    print(lp.is_detectron2_available())
    model = lp.Detectron2LayoutModel(
        "lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config",
        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
        label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
    )

    os.makedirs(args.output_path, exist_ok=True)

    for page_ind in range(num_pages):
        with open(os.path.join(args.output_path, f"{page_ind}.txt"), "w") as f:
            page_1 = pdf_document.create_page(page_ind)

            renderer = PageRenderer()
            image = renderer.render_page(page_1, xres=150.0, yres=150.0)
            a = np.array(image.memoryview(), copy=False)
            a = a[..., :3].astype(np.uint8)
            a = a[..., ::-1]
            layout = model.detect(a)
            print(layout)
            # exit()
            image = Image.fromarray(a)
            text = pytesseract.image_to_string(image, lang="deu")

            f.write(text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
