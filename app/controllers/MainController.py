import os
import requests

from hashlib import md5
from werkzeug.utils import secure_filename

from app import ALLOWED_EXTENSIONS, UPLOAD_FOLDER, YANDEX_API_KEY
from .WaveArray import WaveArray

_VOICE_PATHS = []
_WAV_INSTR = None


def process_text(req, sess_path):
    audios = []
    url = 'https://tts.voicetech.yandex.net/generate'

    for line in req['lines']:
        request_str = {
            'text': line,
            'format': 'wav',
            'lang': req['lang'],
            'speaker': req['speaker'],
            'key': YANDEX_API_KEY
        }
        audios += [requests.get(url, request_str).content]

    i = 1
    audio_paths = []
    for audio in audios:
        path = os.path.join(UPLOAD_FOLDER, sess_path, '{}.wav'.format(i))

        with open(path, 'wb') as f:
            f.write(audio)

        audio_paths += path
        i += 1

    global _VOICE_PATHS
    _VOICE_PATHS = audio_paths
    return True


def safe_save(file, sess_path):
    def allowed_file(fname):
        return '.' in fname and \
               fname.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        safe_path = os.path.join(UPLOAD_FOLDER, sess_path)
        if not os.path.exists(safe_path):
            os.mkdir(safe_path)
        path = os.path.join(safe_path, filename)
        file.save(path)
        return path
    #
    # if file and allowed_file(file.filename):
    #     return path
    # else:
    #     pre, ext = os.path.splitext(path)
    #     new_path = pre + '.wav'
    #     ff = ffmpy.FFmpeg(
    #         inputs={path: None},
    #         outputs={new_path: None}
    #     )
    #     ff.run()
    #     return new_path


def get_wav_repr(path, sess_path, filename):
    wav = WaveArray(path)

    global _WAV_INSTR
    _WAV_INSTR = wav

    file_url = os.path.join('static/audio/', sess_path, filename)
    res = {
        'represent': wav.html_repr(),
        # 'file': wav.file_path,
        'file': file_url,
        'bpm': wav.bpm,
        'stereo': wav.stereo,
        'bar_count': wav.bars,
        'bar_len': wav.bar_len
    }
    return res


def create_sid(request):
    base = "{}|{}".format(request.remote_addr, request.headers.get("User-Agent"))
    hsh = md5(base.encode('utf-8', 'replace'))
    return hsh.hexdigest()
