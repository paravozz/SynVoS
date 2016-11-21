#!flask/bin/python3
import numpy as np
import scipy.io.wavfile as waveio
from aubio import tempo, pitch


class WaveArray(object):

    def __init__(self, file_path, win_size=4096):
        self.file = file_path.split('/')[-1]

        self.win_size = win_size
        self.hop_size = win_size // 4

        self.samplerate, wav_array = waveio.read(file_path)
        self.stereo = True if type(wav_array[0]) is np.ndarray else False
        self.samples = self.get_samples(wav_array)

        self.duration = len(self.samples) / self.samplerate
        self.bpm = self.get_bpm()
        self.bar_len = self.bpm / 60
        self.bar_count = int(np.floor(self.duration / self.bar_len))

        self.pitch = self.get_pitch()

    def get_samples(self, wav_array, chan='L+R'):
        def get_channel(channel):
            i = 0 if channel is 'L' else 1
            res = []

            for sample in wav_array:
                res += [sample[i]]

            res = np.asarray(res)
            return res

        def left():
            return get_channel('L')

        def right():
            return get_channel('R')

        def _sum():
            samples_sum = []

            for sample in wav_array:
                samples_sum += [sample.sum()]

            return np.asarray(samples_sum)

        if not self.stereo:
            return wav_array

        if chan == 'L':
            return left()
        elif chan == 'R':
            return right()
        elif chan == 'L+R':
            return _sum()

    def get_bpm(self):
        o = tempo("specdiff", self.win_size, self.hop_size, self.samplerate)
        # List of beats, in samples
        samples = self.samples.astype(np.float32)
        beats = []
        steps = len(samples) - (len(samples) % self.hop_size)

        for i in range(0, steps, self.hop_size):
            samples_proc = samples[i:i + self.hop_size]
            is_beat = o(samples_proc)
            if is_beat:
                this_beat = o.get_last_s()
                beats.append(this_beat)
        # Convert to periods and to bpm
        if len(beats) > 1:
            if len(beats) < 4:
                print("few beats found in wave array")
            bpms = 120./np.diff(beats)
            b = np.median(bpms)
        else:
            b = 0
            print("not enough beats found in wave array")
        return round(b)

    def get_pitch(self, tolerance=0.8):
        def process_pitch(pitch_array):
            bar_pitch_len = int(np.floor(len(pitch_array) / self.bar_count))

            pitch_bars = []
            for j in range(0, bar_pitch_len * self.bar_count, bar_pitch_len):
                pitch_bars += [np.median(pitch_array[j:j + bar_pitch_len])]

            return pitch_bars

        pitch_o = pitch("yinfft", self.win_size, self.hop_size, self.samplerate)
        pitch_o.set_unit("Hz")
        pitch_o.set_tolerance(tolerance)

        samples = self.samples.astype(np.float32)

        pitches = []
        steps = len(samples) - (len(samples) % self.hop_size)

        for i in range(0, steps, self.hop_size):
            pitchin = pitch_o(samples[i:i + self.hop_size])[0]
            pitches += [pitchin]

        return process_pitch(pitches)

    def set_time_stretch(self):
        pass

    def __repr__(self):
        stereo = "Stereo" if self.stereo else "Mono"
        return "WAV File {}:\n " \
               "{} kHz, {}, BPM: {}\n " \
               "{} bars\n " \
               "PitchArray:\n" \
               "{}".format(self.file, self.samplerate, stereo,
                           self.bpm, self.bar_count, self.pitch)
