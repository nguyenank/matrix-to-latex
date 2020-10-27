import imghdr
import os
from flask import Flask, render_template, request, redirect, url_for, abort, \
    send_from_directory
from models.tolatex.resultstolatex import results_to_latex
from models.tolatex.resultstolatex import CLASSES
from models.displaylatex.displaylatex import displaylatex
# allow latex rendering
import matplotlib as mpl
mpl.use('Agg')

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = './static/uploads'
app.config['OUTPUT_PATH'] = './static/output'

def validate_image(stream):
    header = stream.read(512)  # 512 bytes should be enough for a header check
    stream.seek(0)  # reset stream pointer
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')


@app.route('/')
def index():
    files = os.listdir(app.config['OUTPUT_PATH'])
    return render_template('index.html', files=files)

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = uploaded_file.filename
    print(filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
                file_ext != validate_image(uploaded_file.stream):
            abort(400)
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        full_filename = os.path.join(app.config['UPLOAD_PATH'], filename)
        # print(full_filename)
        os.system("python models/yolov5/detect.py --weights models/yolov5/last.pt --source static/uploads --out static/output --img 416 --conf 0.4 --save-txt")
        # print('Here is the LaTeX Code')
        # print(results_to_latex(('./static/output/txts/' + filename.strip('.jpg') + '.txt'), CLASSES))
        latex = results_to_latex(('./static/output/txts/' + filename.strip('.jpg') + '.txt'), CLASSES)
        latex_filename = './static/output/images/latex_' + filename.strip('.jpg')+".png"
        # generate rendered latex output
        displaylatex(latex.replace("\n", ""), latex_filename)

        # returning render_template instead of redirect(url_for('index')) broke the ability to display an image
        return render_template('index.html', latex=latex, matrix_image = full_filename, image_filename= filename, latex_image = latex_filename)


@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

@app.route('/output/<filename>')
def output(filename):
    return send_from_directory(app.config['OUTPUT_PATH'], filename)
