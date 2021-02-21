import os
import sys
import argparse
import requests
import subprocess
import shutil
from fuzzywuzzy import fuzz
import pdf_to_txt.util
import pdf_to_txt.extract_tables
import pdf_to_txt.extract_cells
import pdf_to_txt.ocr_image
import pdf_to_txt.ocr_to_csv
import pdf_to_txt.pdf_to_images

parser = argparse.ArgumentParser()
parser.add_argument("files", nargs="+")

def download_image_to_tempdir(url, filename=None):
    if filename is None:
        filename = os.path.basename(url)
    response = requests.get(url, stream=True)
    tempdir = pdf_to_txt.util.make_tempdir("demo")
    filepath = os.path.join(tempdir, filename)
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content():
            f.write(chunk)
    return filepath

def improve_table_by_pdftotext(lines, table):
    new_table = []
    for row in table:
        # focus on fixing the first two columns
        clean_row = [w.replace('\n', '') for w in row] 
        row_str = "".join([ w + "\n" for w in clean_row[:2]])
        for i in range(len(lines)-2):
            line_str = "".join(lines[i:i+2])
            if fuzz.ratio(row_str, line_str) > 90:
                clean_row[:2] = [w.replace('\n', '') for w in lines[i:i+2]]
                break 
        if clean_row[-1] and '' in clean_row: # has missing but not the last column
            row_str = "".join([ w + "\n" for w in clean_row if w])
            for i in range(len(lines)-len(clean_row)):
                # missing value in the first index
                line_str_1 = "".join([lines[i]] + lines[i+2:i+len(clean_row)])
                line_str_2 = "".join(lines[i+1:i+len(clean_row)]) # second index
                if fuzz.partial_ratio(row_str, line_str_1) > 90 or \
                        fuzz.partial_ratio(row_str, line_str_2) > 90:
                    clean_row = [w.replace('\n', '') for w in lines[i:i+len(clean_row)]]
        new_table.append(clean_row) 
    return new_table

def get_original_name(image_filepath):
    directory, filename = os.path.split(image_filepath)
    if not os.path.isabs(directory):
        directory = os.path.abspath(directory)
    filename_sans_ext = filename.split(".png")[0]
    return os.path.join(directory, filename_sans_ext)

def merge_with_pdftotext(image_without_ext, ocr_csv_outputs):
    raw_table = [ocr_csv.split("\r\n") for ocr_csv in ocr_csv_outputs]
    raw_table = sum(raw_table, [])
    raw_table = [row.split(",") for row in raw_table]
    table = []
    for row in raw_table:
        if len(row) == 1 and not row[0]:
            continue
        if "\n" not in row[0]:
            table.append(row)
        else:
            new_row = []
            for word in row:
                if not word and len(new_row) > 0:
                    new_row.append([''] * len(new_row[0]))
                else:
                    multiples = [w.replace('"', '') for w in word.split("\n") if w]
                    new_row.append(multiples)
            new_row = list(map(list, zip(*new_row)))
            table.extend(new_row)

    pdftotext_input = image_without_ext[:-4] + ".pdf"
    pdftotext_output = os.path.join(image_without_ext, "pdftotext.txt")
    subprocess.run(["pdftotext", pdftotext_input, pdftotext_output])
    with open(pdftotext_output) as file:
        lines = [line for line in file if line.strip()] 
    stack = []
    lookup = {}
    tbl_start = 0
    found = False
    for idx, line in enumerate(lines):
        if line.endswith(":\n") and idx < len(lines)-1:
            for i in range(idx+1, len(lines)):
                if lines[i].endswith(":\n"):
                    break
                if lines[i].startswith(table[0][0]):
                    found = True 
                    break
                stack.append(lines[i])
            lookup[line.replace(':\n', '')] = "".join(stack).replace('\n', '')
            stack = []
            tbl_start = idx
        if found:
            break
    lookup['TABLE'] = improve_table_by_pdftotext(lines[tbl_start:], table)
    return lookup

#def main(url):
#    image_filepath = download_image_to_tempdir(url)
def main(filepath):
    if filepath[0].endswith('.pdf'):
        image_files = pdf_to_txt.pdf_to_images.convert(filepath)
        image_files = sum([item[1] for item in image_files], [])
    elif filepath[0].endswith('.png'):
        image_files = [filepath]
    image_tables = pdf_to_txt.extract_tables.main(image_files)
    print("Running `{}`".format(f"extract_tables.main([{image_files}])."))
    print("Extracted the following tables from the image:")
    print(image_tables)
    for image, tables in image_tables:
        print(f"Processing tables for {image}.")
        image_without_ext = get_original_name(image)
        ocr_csv_outputs = []
        for table in tables:
            print(f"Processing table {table}.")
            cells = pdf_to_txt.extract_cells.main(table)
            ocr = [
                pdf_to_txt.ocr_image.main(cell, None)
                for cell in cells
            ]
            ocr_csv_output = pdf_to_txt.ocr_to_csv.text_files_to_csv(ocr)
            ocr_csv_outputs.append(ocr_csv_output)
        csv_output = merge_with_pdftotext(image_without_ext, ocr_csv_outputs)
        print()
        print("Here is the parser output:")
        print()
        print(csv_output)
        print()
        try:
            shutil.rmtree(image_without_ext)
        except OSError as e:
            print("Error: %s - %s." %(e.filename, e.strerror))
        os.remove(image)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args.files)

