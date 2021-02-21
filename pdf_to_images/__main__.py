import argparse
import os
from pdf_to_txt.util import working_dir, make_tempdir, get_logger
from pdf_to_txt.pdf_to_images import convert

logger = get_logger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("files", nargs="+")


if __name__ == "__main__":
    args = parser.parse_args()
    pdf_images = convert(args.files)

    for pdf, images in pdf_images:
        print("{}\n{}\n".format(pdf, "\n".join(images)))
    
