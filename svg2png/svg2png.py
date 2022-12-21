"""
License:
This file is part of the 'PublicPythonProjects' distribution (https://github.com/sjoerdv or http://sjoerdv.github.io).
Copyright (C) 2022  Sjoerd de Valk

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3 as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Description:
this CLI program will convert any svg image (in the same folder as the script) to png preserving transparancy.

Prerequisites:
* Python3 3.9+
* pip install pymupdf
* pip install svglib

References:
https://github.com/deeplook/svglib/issues/171#issuecomment-1287829712

Image Sources:
https://upload.wikimedia.org/wikipedia/commons/b/b7/Eo_circle_red_arrow-down.svg
https://upload.wikimedia.org/wikipedia/commons/c/c0/Eo_circle_green_arrow-up.svg

Tested on:
* Linux
** OS: LMDE 5 (elsie) x86_64
** Kernel: 6.0.0-0.deb11.2-amd64
** WM: Cinnamon 5.4.12
** Python3: 3.9.2
* Windows
** OS: Windows 10 21H2
** Python3: 3.9.5

Example:
svg2png.py
This will convert any svg file to its png equivalent, preserving transparancy info.
The png output files should not exist and wil NOT be overwritten.
"""


# Import modules
import sys
import os
import re
import fitz
from svglib import svglib
from reportlab.graphics import renderPDF


def main(argv):
    """_summary_

    Args:
        argv (_type_): _description_
    """
    # folder path
    dir_path = r'.'

    # list to store files
    res = []
    # Iterate directory
    for my_input_file in os.listdir(dir_path):
        # check only text files
        if my_input_file.endswith('.svg'):
            my_output_file = re.sub(r".svg$", ".png", my_input_file)
            if not os.path.isfile(my_output_file):
                # Convert svg to pdf in memory with svglib+reportlab
                # directly rendering to png does not support transparency nor scaling
                drawing = svglib.svg2rlg(path=my_input_file)
                pdf = renderPDF.drawToString(drawing)

                # Open pdf with fitz (pyMuPdf) to convert to PNG
                doc = fitz.Document(stream=pdf)
                pix = doc.load_page(0).get_pixmap(alpha=True, dpi=300)
                pix.save(my_output_file)
                print("Created:",my_output_file)
            else:
                print(my_output_file,"already exists. Skipped!")


# Start main thread
if __name__ == "__main__":
    main(sys.argv[1:])
