"""
displaylatex.py

takes in a string of LaTeX s, and a filepath (with no extension), and outputs
a rendered pdf version of the LaTeX to the filepath + .pdf

TO USE: run 'resultstolatex(s, filepath)'
"""

import os
from pylatex import Document, Command, NoEscape


def displaylatex(latexstring, filepath):
    """
        takes in a string of LaTeX latexstring, and a filepath
        (with no extension), and outputs a rendered pdf version
        of the LaTeX to the filepath + .pdf
    """
    doc = Document('basic', page_numbers=False, font_size='LARGE')
    doc.preamble.append(Command('usepackage', 'amsmath'))
    doc.preamble.append(Command('usepackage', 'geometry'))
    doc.preamble.append(Command('pagestyle', 'empty'))
    doc.preamble.append(
        NoEscape(
            r'\geometry{paperwidth=2.5in, paperheight=2.5in,'
            r'margin=0.1in, hoffset=-0.2in}'
        ))
    # NoEscape renders \'s properly instead of converting to \backslash
    doc.append(NoEscape(latexstring))
    doc.generate_pdf(filepath, clean_tex=False)
    # remove generated tex file
    os.system(f'rm {filepath+".tex"}')
