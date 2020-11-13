"""
controller.py

handles the paths to the various views/templates of the webapp,
as well as calling the models
also deals with generated files from calling the models,
categorizing them as static assets or temporary files that are deleted
"""

import os
from flask import Flask, render_template, request
from models.tolatex.resultstolatex import results_to_latex
from models.classes import CLASSES
from models.displaylatex.displaylatex import displaylatex

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.jpeg']
# location of uplaoded image and rendered pdf
app.config['STATIC_MATRIX_PATH'] = './static/matrix'
app.config['STATIC_MATRIX_FOLDER'] = app.config['STATIC_MATRIX_PATH'][2:]
# temporary, intermediate files
app.config['TEMP_PATH'] = './temp'
app.config['TEMP_FOLDER'] = app.config['TEMP_PATH'][2:]
app.config['CLASSES'] = CLASSES


@app.route('/')
def index():
    """
        displays index view;
        initial page with brief instructions
        and ability to upload image
    """
    return render_template('index.html')


@app.route('/', methods=['POST'])
def upload_files():
    """
        verifies uploaded file as valid image, runs
        the YOLOv5, tolatex, and renderlatex model in that order,
        deletes any intermediate files, and displays results view
        with initial image, generated latex text, and rendered pdf
    """
    # remove and remake folder to clean out anything from past runs
    os.system(f'rm -r {app.config["STATIC_MATRIX_FOLDER"]}')
    os.system(f'mkdir {app.config["STATIC_MATRIX_FOLDER"]}')
    uploaded_file = request.files['file']
    filename = uploaded_file.filename
    if filename != '':
        # only continue with nonempty filename
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            # not a valid file extension
            return render_template('index.html')

        # save the uplaoded file to STATIC_PATH
        full_filename = os.path.join(app.config['STATIC_MATRIX_PATH'],
                                     filename)
        uploaded_file.save(full_filename)
        return render_template('confirm_image.html', image_filename=filename,
                               matrix_image=full_filename, loading=False)
    return render_template('index.html')


@app.route('/results', methods=['POST'])
def predict():
    """
        runs the three models and displays results view
    """
    filename = request.form['filename']
    file_root = os.path.splitext(filename)[0]
    full_filename = os.path.join(app.config['STATIC_MATRIX_PATH'],
                                 filename)
    # run YOLOv5 model
    os.system(f'python models/yolov5/detect.py '
              f'--weights models/yolov5/best-2.pt '
              f'--source {app.config["STATIC_MATRIX_FOLDER"]} '
              f'--out {app.config["TEMP_FOLDER"]} '
              f'--img 416 --conf 0.4 --save-txt')
    # run toLatex model
    latex = results_to_latex(
            os.path.join(app.config['TEMP_PATH'], file_root + '.txt'), CLASSES)
    latex_filename = os.path.join(app.config['STATIC_MATRIX_PATH'],
                                  file_root)
    # run renderLatex model
    displaylatex(latex.replace('\n', ''), latex_filename)
    # delete temporary folder
    os.system('rm -r temp')
    return render_template('results.html', latex=latex,
                           matrix_image=full_filename,
                           image_filename=filename,
                           latex_pdf=latex_filename+'.pdf')


@app.route('/about')
def about():
    """
        displays about view;
        about creators and reasoning behind the project
    """
    return render_template('about.html')


@app.route('/instructions')
def instructions():
    """
        displays instruction view about
        how to use webapp and limitations of it
    """
    return render_template('instructions.html')
