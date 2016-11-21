#!flask/bin/python3
from app import app, ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from flask import render_template, request, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
from .controllers.WaveArray import WaveArray


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)
            wav = WaveArray(path)
            flash(wav)

    return render_template("index.html")

