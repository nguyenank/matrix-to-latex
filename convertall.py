"""

    This file uses inkml2jpg to convert all the files in a specified folder
    from inkml to jpg

"""

from __future__ import print_function
import inkml2img, glob, os
import pickle
import os.path
import csv
#.inkml2img('2013ALL_inkml_data/200923-1556-49.inkml','./2013ALL_inkml_data_image/200923-1556-49.png')
#inkml2img.inkml2img('200923-1556-49.inkml','linewidth.jpg')
"""
    takes a txt file with the names of all the inkml files you want to
    convert to convert
    input:  filename (+ path if not in same directory) textfile with inkml file
           names in it, foldername is a string you want to name the directory the
           converted jpgs are stored.
    output: technically none, but puts jpgs in it.
"""


def convert2jpgs(filename):
    inkmls = open(filename, "r")

    if not os.path.exists('jpgs'):
        os.mkdir('jpgs')

    for row in inkmls.readlines():
        jpgname = 'jpgs/' + os.path.splitext(row)[0] + '.jpg'
        print(jpgname)
        inkml2img.inkml2img('TestEM2014/' + row.rstrip('\n'),
                            jpgname)  #replace path name here


filename = 'MatricesTrain/listeMatTrain.txt'
filename1 = 'individualsymbols/individualsymbols1.txt'
filename2 = 'individualsymbols/individualsymbols2.txt'
filename3 = 'TestEM2014/listTestInkml.txt'
convert2jpgs(filename3)
print("made it half way!!!!!!!!!!")
#convert2jpgs(filename2)
