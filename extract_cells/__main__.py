import sys

from pdf_to_txt.extract_cells import main

paths = main(sys.argv[1])
print("\n".join(paths))
