import numpy as np
from PIL import Image
from layoutparser.models.auto_layoutmodel import AutoLayoutModel


class Parser:
    def __init__(self, model_type: str):
        if model_type == 'fast':
            self.model = AutoLayoutModel("lp://detectron2/PubLayNet/faster_rcnn_R_50_FPN_3x")
            self.type_map = {0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}
        elif model_type == 'efficient':
            self.model = AutoLayoutModel("lp://efficientdet/PubLayNet/tf_efficientdet_d1")
            self.type_map = {k: k for k in ["Text", "Title", "List", "Table", "Figure"]}
        else:
            raise Exception(f"Unknown model type {model_type}")

    def get_text_areas(self, image: np.ndarray):
        """return list of (PIL.Image, ElType, score: float)"""
        return [((el.block.coordinates[0], el.block.coordinates[1], el.block.width, el.block.height),
                 Image.fromarray(image).crop(el.block.coordinates),
                 self.type_map[el.type],
                 el.score) for el in self.model.detect(image)]
