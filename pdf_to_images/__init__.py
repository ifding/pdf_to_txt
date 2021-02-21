import os
import re
import subprocess

from pdf2image import convert_from_path
from pdf_to_txt.util import get_logger, working_dir

logger = get_logger(__name__)

def convert(files):
    pdf_images = []
    print(files)
    for f in files:
        if f.endswith(".pdf"):
            pdf_images.append((f, pdf_to_images(f)))

    for pdf, images in pdf_images:
        for image in images:
            preprocess_img(image)
    return pdf_images

# Wrapper around the Poppler command line utility "pdfimages" and helpers for
# finding the output files of that command.
def pdf_to_images(pdf_filepath):
    """
    Turn a pdf into images
    Returns the filenames of the created images sorted lexicographically.
    """
    directory, filename = os.path.split(pdf_filepath)
    image_filenames = pdfimages(pdf_filepath)

    # Since pdfimages creates a number of files named each for there page number
    # and doesn't return us the list that it created
    return sorted([os.path.join(directory, f) for f in image_filenames])

# The conversion of a PDF file with one or multiple pages to 
# a single merged PNG image.
def pdfimages_(file_path):
    directory, filename = os.path.split(file_path)
    if not os.path.isabs(directory):
        directory = os.path.abspath(directory)
    filename_sans_ext = filename.split(".pdf")[0]
    output_path = os.path.join(directory, filename_sans_ext + ".png")
    # save temp image files in temp dir, delete them after we are finished
    with tempfile.TemporaryDirectory() as temp_dir:
        # convert pdf to multiple image
        images = convert_from_path(file_path, 600, output_folder=temp_dir)
        # save images to temporary directory
        temp_images = []
        for i in range(len(images)):
            image_path = f'{temp_dir}/{i}.jpg'
            images[i].save(image_path, 'PNG')
            temp_images.append(image_path)
        # read images into pillow.Image
        imgs = list(map(Image.open, temp_images))
    # find minimum width of images
    min_img_width = min(i.width for i in imgs)
    # find total height of all images
    total_height = 0
    for i, img in enumerate(imgs):
        total_height += imgs[i].height
    # create new image object with width and total height
    merged_image = Image.new(imgs[0].mode, (min_img_width, total_height))
    # paste images together one by one
    y = 0
    for img in imgs:
        merged_image.paste(img, (0, y))
        y += img.height
    # save merged image
    merged_image.save(output_path)
    logger.debug(
        "Converted {} into files:\n{}".format(file_path, "\n".join(output_path))
    )
    return output_path

def pdfimages(pdf_filepath):
    """
    Uses the `pdfimages` utility from Poppler
    (https://poppler.freedesktop.org/). Creates images out of each page. Images
    are prefixed by their name sans extension and suffixed by their page number.

    This should work up to pdfs with 999 pages since find matching files in dir
    uses 3 digits in its regex.
    """
    directory, filename = os.path.split(pdf_filepath)
    if not os.path.isabs(directory):
        directory = os.path.abspath(directory)
    filename_sans_ext = filename.split(".pdf")[0]

    # pdfimages outputs results to the current working directory
    with working_dir(directory):
        #subprocess.run(["pdfimages", "-png", filename, filename.split(".pdf")[0]])
        pages = convert_from_path(filename, 600)
        for page in pages:
            page.save("%s-%s.png" % (filename_sans_ext, \
                str(pages.index(page)).zfill(3)), "PNG")

    image_filenames = find_matching_files_in_dir(filename_sans_ext, directory)
    logger.debug(
        "Converted {} into files:\n{}".format(pdf_filepath, "\n".join(image_filenames))
    )
    return image_filenames


def find_matching_files_in_dir(file_prefix, directory):
    files = [
        filename
        for filename in os.listdir(directory)
        if re.match(r"{}-\d{{3}}.*\.png".format(re.escape(file_prefix)), filename)
    ]
    return files

def preprocess_img(filepath, tess_params=None):
    """Processing that involves running shell executables,
    like mogrify to rotate.

    Uses tesseract to detect rotation.

    Orientation and script detection is only available for legacy tesseract
    (--oem 0). Some versions of tesseract will segfault if you let it run OSD
    with the default oem (3).
    """
    if tess_params is None:
        tess_params = ["--psm", "0", "--oem", "0"]
    rotate = get_rotate(filepath, tess_params)
    logger.debug("Rotating {} by {}.".format(filepath, rotate))
    mogrify(filepath, rotate)


def get_rotate(image_filepath, tess_params):
    """
    """
    tess_command = ["tesseract"] + tess_params + [image_filepath, "-"]
    output = (
        subprocess.check_output(tess_command)
        .decode("utf-8")
        .split("\n")
    )
    output = next(l for l in output if "Rotate: " in l)
    output = output.split(": ")[1]
    return output


def mogrify(image_filepath, rotate):
    subprocess.run(["mogrify", "-rotate", rotate, image_filepath])
