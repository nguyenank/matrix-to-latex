from pylatex import Document, Command, NoEscape

def displaylatex(s, filepath):
    doc = Document('basic', page_numbers=False, font_size="LARGE")
    doc.preamble.append(Command('usepackage', 'amsmath'))
    doc.preamble.append(Command('usepackage', 'geometry'))
    doc.preamble.append(Command('pagestyle', 'empty'))
    doc.preamble.append(NoEscape(r'\geometry{paperwidth=2.5in,paperheight=2.5in, margin=0.1in, hoffset=-0.2in}'))
    doc.append(NoEscape(s))
    doc.generate_pdf(filepath, clean_tex=False)
