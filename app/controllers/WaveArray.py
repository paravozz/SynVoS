#!flask/bin/python3
import numpy as np
import scipy.io.wavfile as waveio
from aubio import tempo, pitch, pvoc, float_type, cvec, unwrap2pi


class WaveArray(object):

    def __init__(self, file_path, win_size=1024):
        self._file = file_path.split('/')[-1]

        self._win_size = win_size
        self._hop_size = win_size // 8  # TODO: 4 or 8

        self._samplerate, wav_array = waveio.read(file_path)
        self._stereo = True if type(wav_array[0]) is np.ndarray else False
        self._samples = self._get_samples(wav_array)

        self._duration = len(self._samples) / self._samplerate
        self._bpm = self._get_bpm()
        self._bar_len = self._bpm / 60
        self._bar_count = int(np.floor(self._duration / self._bar_len))

        self._pitch = self._get_pitch()

    def _get_samples(self, wav_array, chan='L+R'):
        def get_channel(channel):
            i = 0 if channel is 'L' else 1
            res = []

            for sample in wav_array:
                res += [sample[i]]

            res = np.asarray(res)
            return res

        def get_sum():
            samples_sum = []

            for sample in wav_array:
                samples_sum += [sample.sum()]

            return np.asarray(samples_sum)

        if not self._stereo:
            return wav_array

        if chan == 'L':
            return get_channel('L')
        elif chan == 'R':
            return get_channel('R')
        elif chan == 'L+R':
            return get_sum()

    def _get_bpm(self):
        o = tempo("specdiff", self._win_size, self._hop_size, self._samplerate)
        # List of beats, in samples
        samples = self._samples.astype(np.float32)
        beats = []
        steps = len(samples) - (len(samples) % self._hop_size)

        for i in range(0, steps, self._hop_size):
            samples_proc = samples[i:i + self._hop_size]
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
            if b > 200:
                while b > 200:
                    b /= 2
        else:
            b = 0
            print("not enough beats found in wave array")
        b = round(b)
        if int(b) & 1:
            b -= 1
        return b

    def _get_pitch(self, tolerance=0.8):
        def process_pitch(pitch_array):
            bar_pitch_len = int(np.floor(len(pitch_array) / self._bar_count))

            pitch_bars = []
            for j in range(0, bar_pitch_len * self._bar_count, bar_pitch_len):
                pitch_bars += [round(np.median(pitch_array[j:j + bar_pitch_len]))]

            return pitch_bars

        pitch_o = pitch("yinfft", self._win_size, self._hop_size, self._samplerate)
        pitch_o.set_unit("Hz")
        pitch_o.set_tolerance(tolerance)

        samples = self._samples.astype(np.float32)

        pitches = []
        steps = len(samples) - (len(samples) % self._hop_size)

        for i in range(0, steps, self._hop_size):
            pitchin = pitch_o(samples[i:i + self._hop_size])[0]
            pitches += [pitchin]

        return process_pitch(pitches)

    def time_stretch(self, rate):  # TODO: make it work
        win_s = self._win_size
        hop_s = self._hop_size

        warmup = win_s // hop_s - 1

        p = pvoc(win_s, hop_s)

        # allocate memory to store norms and phases
        n_blocks = len(self._samples) // hop_s + 1
        # adding an empty frame at end of spectrogram
        norms = np.zeros((n_blocks + 1, win_s // 2 + 1), dtype=float_type)
        phases = np.zeros((n_blocks + 1, win_s // 2 + 1), dtype=float_type)

        block_read = 0
        samples = self._samples
        steps_max = len(samples) - (len(samples) % hop_s)

        for i in range(0, steps_max, hop_s):
            # pitchin = pitch_o(samples[i:i + self._hop_size])
            # read from source
            samples_proc = np.asarray(samples[i:i + hop_s]).astype(np.float32)
            # compute fftgrain
            spec = p(samples_proc)
            # store current grain
            norms[block_read] = spec.norm
            phases[block_read] = spec.phas
            # increment block counter
            block_read += 1

        # just to make sure
        # source_in.close()

        sink_out = []

        # interpolated time steps (j = alpha * i)
        steps = np.arange(0, n_blocks, rate, dtype=float_type)
        # initial phase
        phas_acc = phases[0]
        # excepted phase advance in each bin
        phi_advance = np.linspace(0, np.pi * hop_s, win_s / 2 + 1).astype(float_type)

        new_grain = cvec(win_s)

        for (t, step) in enumerate(steps):

            frac = 1. - np.mod(step, 1.0)
            # get pair of frames
            t_norms = norms[int(step):int(step + 2)]
            t_phases = phases[int(step):int(step + 2)]

            # compute interpolated frame
            new_grain.norm = frac * t_norms[0] + (1. - frac) * t_norms[1]
            new_grain.phas = phas_acc
            # print t, step, new_grain.norm
            # print t, step, phas_acc

            # psola
            samples_proc = p.rdo(new_grain)
            if t > warmup:  # skip the first few frames to warm up phase vocoder
                # write to sink
                sink_out.append(samples_proc[:hop_s])

            # calculate phase advance
            dphas = t_phases[1] - t_phases[0] - phi_advance
            # unwrap angle to [-pi; pi]
            dphas = unwrap2pi(dphas)
            # cumulate phase, to be used for next frame
            phas_acc += phi_advance + dphas

        for t in range(warmup + 1):  # purge the last frames from the phase vocoder
            new_grain.norm[:] = 0
            new_grain.phas[:] = 0
            samples_proc = p.rdo(new_grain)
            sink_out.append(samples_proc[:hop_s])

        self._samples = np.asarray(sink_out).astype(np.int16)

    def save(self, file_path):
        waveio.write(file_path, self._samplerate, self._samples)

    def __repr__(self):
        stereo = "Stereo" if self._stereo else "Mono"
        return "WAV File {}:\n " \
               "{} kHz, {}, BPM: {}\n " \
               "{} bars\n " \
               "PitchArray:\n" \
               "{}".format(self._file, self._samplerate, stereo,
                           self._bpm, self._bar_count, self._pitch)

    @property
    def pitch(self):
        return self._pitch

    @property
    def bpm(self):
        return self._bpm

    @property
    def samplerate(self):
        return self._samplerate

    @property
    def stereo(self):
        return self._stereo

    @property
    def bars(self):
        return self._bar_count