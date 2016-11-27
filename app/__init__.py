from flask import Flask

UPLOAD_FOLDER = '/Volumes/multimedia/prvz/Desktop/UNIVERSITY/SynVoS/app/static/audio'
ALLOWED_EXTENSIONS = set(['wav'])
YANDEX_API_KEY = 'cd6d68b2-8abf-4e88-9f91-881624e8392e'

app = Flask(__name__)

from app import views
app.config['MAX_CONTENT_LENGTH'] = 40 * 1024 * 1024
