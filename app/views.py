#!flask/bin/python3
from flask import redirect, render_template, \
    request, jsonify, session, url_for, flash, g

from app import app, db
from app.models import User
from flask_login import logout_user, login_user, current_user
from app.controllers.OAuthController import OAuthSignIn
from app.controllers.MainController import safe_save, process_text, \
    get_wav_repr, create_sid, process_regions, save_in_db


@app.route('/save_to_db', methods=['POST'])
def save_to_db():
    if current_user.is_anonymous:
        flash('Чтобы сохранять файлы необходимо войти')
        return jsonify(url_for('index'))
    if request.json:
        save_in_db(request.json)
        flash('Файл {} сохранен'.format(request.json))
        return jsonify(url_for('profile'))


@app.route('/region_done', methods=['POST'])
def region_process():
    if request.json:
        req = request.json
        return jsonify(process_regions(req, session['_id']))
    else:
        pass

    return 'Error'


@app.route('/file_upload', methods=['POST'])
def file_upload():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    path, filename = safe_save(file, session['_id'])
    return jsonify(get_wav_repr(path, session['_id'], filename))


@app.route('/text_generated', methods=['POST'])
def text_process():
    if request.json:
        req = request.json
        if process_text(req, session['_id']):
            return jsonify('OK')
        else:
            return 'Error'
    else:
        return 'Error'


@app.before_request
def before_request():
    g.user = current_user


@app.route('/index', methods=['GET', 'POST'])
def lame_index():
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
def index():
    if '_id' not in session:
        session['_id'] = create_sid(request)
    return render_template("index.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile')
def profile():
    if not current_user.is_anonymous:
        return render_template('profile.html')
    return redirect(url_for('index'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, email=email, nickname=username)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))
