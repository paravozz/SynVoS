#!flask/bin/python3
import os

# GLOBAL VARIABLES
basedir = os.path.abspath(os.path.dirname(__file__))

# SQLALCHEMY_DATABASE_URI = 'postgres://jdappfswfuldjx:' \
#                           '4yt1VYr8drhAc-Z7nVOpr8OnvA@ec2-54-75-228-77.' \
#                           'eu-west-1.compute.amazonaws.com:5432/ddauplqp92qvmb'


YANDEX_API_KEY = 'cd6d68b2-8abf-4e88-9f91-881624e8392e'
UPLOAD_FOLDER = '/Volumes/multimedia/prvz/Desktop/UNIVERSITY/SynVoS/app/static/audio'
ALLOWED_EXTENSIONS = set(['wav'])


# APP CONFIG VARIABLES
class Config(object):
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    MAX_CONTENT_LENGTH = 40 * 1024 * 1024
    SQLALCHEMY_DATABASE_URI = 'postgres://jdappfswfuldjx:' \
                              '4yt1VYr8drhAc-Z7nVOpr8OnvA@ec2-54-75-228-77.' \
                              'eu-west-1.compute.amazonaws.com:5432/ddauplqp92qvmb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OAUTH_CREDENTIALS = {
        'facebook': {
            'id': '662876993894844',
            'secret': '308a19aab23f059b5f85f1a95db40401'
        },
        'vk': {
            'id': '5754384',
            'secret': 'L7zp1zTPiezsXVABptLw'
        },
        'google': {
            'id': '69141475487-0eagjkc11tccov4dr7glb0aqlqn6bf27.apps.googleusercontent.com',
            'secret': 'Ob1nmJJzEcpeZIeEn_mzVzyy'
        },
        'github': {
            'id': '2980f19efdea38694ca4',
            'secret': '0af29e3b176f04836fe9f56e0a1483a54d081e48'
        }
    }
