from flask import Flask

UPLOAD_FOLDER = '/Volumes/multimedia/prvz/Desktop/UNIVERSITY/SynVoS/app/static/audio'
ALLOWED_EXTENSIONS = set(['wav'])


app = Flask(__name__)

from app import views
app.config['MAX_CONTENT_LENGTH'] = 40 * 1024 * 1024
