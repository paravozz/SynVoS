from flask import Flask

UPLOAD_FOLDER = '/Volumes/multimedia/prvz/Desktop/UNIVERSITY/SynVoS/app/static/'
ALLOWED_EXTENSIONS = set(['wav'])

app = Flask(__name__)
from app import views
