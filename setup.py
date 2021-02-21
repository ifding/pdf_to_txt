import os
import setuptools

this_dir = os.path.abspath(os.path.dirname(__file__))
long_description = "This python package contains modules to help with finding and extracting tabular data from a PDF or image."

setuptools.setup(
    name="pdf_to_txt",
    version="0.0.1",
    author="Fei Ding",
    description="Extract text from tables in images.",
    long_description=long_description,
    long_description_content_type="text/plain",
    url="https://github.com/ifding/pdf_to_txt",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["opencv-python~=4.2", "numpy~=1.19", "pdf2image~=1.14", "fuzzywuzzy~=0.18"],
    python_requires=">=3.6",
)
