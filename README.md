# PDF to Text

This repo includes two main methods to extract text from pdf:

- pdftotext

- tesseract OCR

The former can accurately detect text from pdf, but the problem is that it cannot 
handle tables very well, especially for the table with empty cell.

The latter utilizes opencv to detect table from an image, and extract ordered cell
from a table, then uses OCR technique to extract texts from each cell. It can 
maintain the cell orders, but the problem is that OCR cannot recover texts 100%.

Then this package combines them together, and uses the pdftotext result to correct the
OCR result. The basic idea is to use `fuzzywuzzy` to calculate the similaries between
strings. If the similarity is higher than a certain threshold, replace the OCR string
with pdftotext string.

### Install Requirements:

1. Tesseract OCR

```
sudo apt-get install tesseract-ocr
```

2. Imagemagick

```
sudo apt-get install imagemagick
```

3. PDF Utilities

```
sudo apt-get install poppler-utils
```
4. This repo

```
git clone https://github.com/ifding/pdf_to_txt.git
cd pdf_to_txt
pip3 install .
```

### Usage

1. If you have pdf files in one folder, just run the command:

```
python3 -m pdf_to_txt.run pdf_to_txt/examples/test*.pdf
```

The output should look like:

```
{'Product Name': 'Clay Mask Base', 'INCI Name': 'Water, kaolin, glycerin, cetearyl alcohol (and) polysorbate 60, isopropyl myristate,colloidal oatmeal, glyceryl stearate, allantoin, edta, xanthan gum, phenoxyethanol,ethylhexyl glycerin, DMDM hydantoin', 'Lot Number': 'Not available (data may vary slightly with different lots or batches)', 'Expiration Date': '24 months from production date', 'TABLE': [['Specifications', 'Range', 'Results'], ['Appearance', 'Thick cream', 'Pass'], ['Color', 'Yellow to beige', 'Pass'], ['pH value', '5.0-6.5', 'Pass'], ['Water', '40-80%', ''], ['Kaolin', '10-30%', ''], ['Glycerin', '5-20%', ''], ['Cetearyl alcohol (and) Polysorbate 60', '5-15%', ''], ['Isopropyl myristate', '5-15%', ''], ['Colloidal oatmeal', '4-10%', ''], ['Cetearyl alcohol', '2-8%', ''], ['Glyceryl stearate', '2-6%', ''], ['Allantoin', '1.0-4%', ''], ['Disodium EDTA', '0.5-3%', ''], ['Xanthan gum', '0.5-3%', ''], ['Phenoxyethanol', '0.5-2%', ''], ['Ethylhexylglycerin', '0.5-2%', ''], ['DMDM Hydantoin', '0.05-0.1%', '']]}
```

```
{'Product Name': 'Bismuth Oxychloride', 'INCI Name': 'Bismuth oxychloride', 'CAS Number': '7787-59-9', 'Lot Number': 'Not available (data may vary slightly with different lots or batches)', 'Expiration Date': '120 months from production date', 'TABLE': [['Property', 'Range', 'Result'], ['Chemical Composition Analysis', '', ''], ['Bismouth Oxychloride', '19-21%', '20.0%'], ['Mica', '79-81%', '80.0%'], ['Lot Analysis:', '', ''], ['pH', '5.0-9.0', '7.4 (4%aqueous suspension)'], ['Specific Gravity', '', ''], ['Bulk Density', '20-40 /100ml', '21 g/100ml'], ['Loss on Drying', '<2.0%', '0.02%(Open cup @105 C for 1 hour)'], ['Particle Size', '5-80um', 'Passed (Laser Diffracton)'], ['Trace Elements:', '', ''], ['Lead(Pb)', '<10 ppm', 'Passed'], ['Arsenic(As)', '<2 ppm', 'Passed'], ['Antimony (Sb)', '<2 ppm', 'Passed'], ['Mercury (Hg)', '<1 ppm', 'Passed']]}
```


### References

- [eihli/image-table-ocr](https://github.com/eihli/image-table-ocr)
