# displaylatex.py
#
# takes in a filepath and a string of LaTeX code bounded with $'s and
# saves a rendered png image of the output to the filepath
#
# TO USE: run 'resultstolatex(latex_string, filepath)'

import matplotlib.pyplot as plt
import matplotlib as mpl

def displaylatex(s, filepath):
    mpl.rcParams['font.size'] = 20
    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['text.latex.preamble'] = r'\usepackage{{amsmath}}'

    fig = plt.figure()

    fig.text(0,1,s)
    plt.savefig(filepath, bbox_inches='tight')
