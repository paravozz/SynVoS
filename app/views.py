#!flask/bin/python3
from markupsafe import Markup

from app import app, ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from flask import render_template, request, flash, redirect, url_for, jsonify
import os
from werkzeug.utils import secure_filename
from .controllers.WaveArray import WaveArray


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/file_upload', methods=['GET', 'POST'])
def file_upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            # return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            # return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)
            wav = WaveArray(path)
            # wav.time_stretch(2)
            # wav.pitch_shift(-5)
            # wav.save(os.path.join(UPLOAD_FOLDER, 'result.wav'))
            # return Markup(wav.html_repr())
            # flash(Markup(wav.html_repr()))
            res = {
                'represent': wav.html_repr(),
                'file': wav.file_path,
                'bpm': wav.bpm,
                'stereo': wav.stereo,
                'bars': wav.bars,
                'bar_len': wav.bar_len
            }
            return jsonify(res)
    else:
        return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

