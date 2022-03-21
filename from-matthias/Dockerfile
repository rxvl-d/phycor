FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-devel

RUN DEBIAN_FRONTEND=noninteractive apt update -y
RUN DEBIAN_FRONTEND=noninteractive apt upgrade -y
RUN DEBIAN_FRONTEND=noninteractive apt install python-pip git libpoppler-cpp-dev cmake libpoppler-glib-dev -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install ffmpeg libsm6 libxext6  -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install tesseract-ocr tesseract-ocr-deu  tesseract-ocr-eng -y
RUN cd /
RUN pip install python-poppler
RUN pip install layoutparser
RUN pip install "git+https://github.com/facebookresearch/detectron2.git@v0.5#egg=detectron2"
RUN pip install pytesseract
RUN pip install pandas
RUN pip install effdet

