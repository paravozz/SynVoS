#!flask/bin/python3
from flask import render_template, request, jsonify
from flask import session

from app import app
from .controllers.MainController import safe_save, process_text, get_wav_repr, create_sid


@app.route('/region_done')
def region_process():
    pass


@app.route('/file_upload', methods=['POST'])
def file_upload():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    path = safe_save(file, session['_id'])
    return jsonify(get_wav_repr(path, session['_id'], file.filename))


@app.route('/text-generated', methods=['POST'])
def text_process():
    if request.json:
        req = request.json
        if process_text(req, session['_id']):
            return 'OK'
        else:
            return 'Error'
    else:
        return 'Error'


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if '_id' not in session:
        session['_id'] = create_sid(request)
        print(session.keys())
    return render_template("index.html")

