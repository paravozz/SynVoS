#!flask/bin/python3
import datetime
import os
import numpy as np
import requests

from hashlib import md5

from flask import url_for
from werkzeug.utils import secure_filename

from app import models
from app.config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER, YANDEX_API_KEY
from .WaveArray import WaveArray
from pydub import AudioSegment

_VOICE_PATHS = []
_VOICE_SPEAKER = None
_WAV_INSTR_PATH = None
_WAV = None


def process_text(req, sess_path):
    audios = []
    url = 'https://tts.voicetech.yandex.net/generate'
    global _VOICE_SPEAKER
    _VOICE_SPEAKER = req['speaker']
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

        audio_paths += [path]
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
        return path, filename
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
    wav = WaveArray(path, no_pitch=True)

    global _WAV_INSTR_PATH, _WAV
    _WAV_INSTR_PATH = path
    _WAV = wav

    file_url = os.path.join('static/audio/', sess_path, filename)
    res = {
        'file': file_url,
        'bpm': wav.bpm,
        'stereo': wav.stereo,
        'bar_count': wav.bars,
        'bar_len': wav.bar_len
    }
    ######
    print(_WAV.html_repr())
    ######
    return res


def create_sid(request):
    base = "{}|{}".format(request.remote_addr, request.headers.get("User-Agent"))
    hsh = md5(base.encode('utf-8', 'replace'))
    return hsh.hexdigest()


def process_regions(region, sess_path):
    instr = AudioSegment.from_wav(_WAV_INSTR_PATH)
    start, end = region['start'] * 1000, region['end'] * 1000
    instr = instr[start:end]

    safe_path = os.path.join(UPLOAD_FOLDER, sess_path)
    buf_path = os.path.join(safe_path, 'instrumental-buff.wav')
    instr.export(buf_path, format='wav')
    wav_instr = WaveArray(buf_path, bpm=_WAV.bpm)

    voice_res = AudioSegment.empty()
    i = 0
    for path in _VOICE_PATHS:
        segment = WaveArray(path, no_process=True)
        # stretch_counter = segment.duration / _WAV.bar_len
        stretch_counter = segment.duration / wav_instr.bar_len
        segment.time_stretch(stretch_counter)
        segment.save(path)
        # wav_segment = WaveArray(path, bpm=_WAV.bpm)
        wav_segment = WaveArray(path, bpm=wav_instr.bpm)
        freq_diff = \
            (12 / np.log(2)) * np.log(wav_segment.pitch[0] / wav_instr.pitch[i])

        if freq_diff >= 0:
            freq_diff %= 12
        else:
            freq_diff %= -12

        if freq_diff < -6:
            freq_diff += 12
        elif freq_diff > 6:
            freq_diff -= 12

        wav_segment.pitch_shift(freq_diff)
        wav_segment.save(path)

        voice_res += AudioSegment.from_wav(path)
        i += 1

    instr -= 3
    voice_res += 6
    # print('voice {} \n instr {} \n'.format(voice_res.duration_seconds, instr.duration_seconds))
    full_track = instr.overlay(voice_res)
    full_track.export(os.path.join(safe_path, 'result.wav'), format='wav')
    url = url_for('index') + 'static/' + 'audio/' + sess_path + '/result.wav'

    file_list = [f for f in os.listdir(safe_path)]
    for f in file_list:
        if not f == 'result.wav':
            f_path = os.path.join(safe_path, f)
            os.remove(f_path)

    return url


def save_in_db(temp_url):
    pass