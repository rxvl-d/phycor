import sys
sys.path.append('.')

import argparse
from PIL import Image
from itertools import islice

from phycor.loader import Loader
from phycor.layout import Parser
from phycor.writer import Writer

import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def parse_args():
    parser = argparse.ArgumentParser(description="Parse Physics Textbooks")
    #  --data_dir ../data/ --model_type fast --output_path ../data/fast_parse/ --n_pages 10
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose output", default=False)
    parser.add_argument("-i", "--data_dir", help="Data Dir")
    parser.add_argument("-m", "--model_type", help="Model Type", choices=['fast', 'efficient'])
    parser.add_argument("-n", "--n_pages", help="Num. Pages", type=int, required=False, default=None)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    output_path = args.data_dir + '/' + args.model_type + '/'
    run(args.data_dir, output_path, args.model_type, args.n_pages, args.verbose)


def run(data_dir, output_path, model_type, n_pages, verbose):
    loader = Loader(data_dir)
    parser = Parser(model_type)
    writer = Writer(output_path)
    page_images = loader.page_images(verbose)
    optionally_limited = islice(page_images, n_pages) if n_pages else page_images
    for filename, page_index, image in optionally_limited:
        elements = parser.get_text_areas(image)
        for el_idx, (crop, el_type, score) in enumerate(elements):
            writer.write(filename, page_index, el_idx, el_type, score, Image.fromarray(image), crop)
    writer.finalize()


if __name__ == '__main__':
    main()
