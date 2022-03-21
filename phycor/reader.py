from PIL.Image import Image
from pytesseract import pytesseract


class Transcriber:
    def transcribe(self, image: Image):
        return pytesseract.image_to_string(image)
