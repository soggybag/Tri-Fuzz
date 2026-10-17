"""Synthetic guitar DI (Karplus-Strong) at 44.1 kHz: a low E note, then an open E major strum.
Peaks ~150 mV (note) / ~250 mV (chord), roughly a single-coil pickup."""
import random, math
SR = 44100
def pluck(f, dur, amp, seed):
    """Karplus-Strong string: noise burst in a delay line, averaged each pass (string damping)"""
    rnd = random.Random(seed); n = max(2, int(round(SR / f))); N = int(dur * SR)
    buf = [rnd.uniform(-1, 1) for _ in range(n)]
    for _ in range(3): buf = [(buf[i] + buf[i - 1]) / 2 for i in range(n)]   # softer pick
    decay = 0.9985 if f < 150 else 0.997
    out = []
    for k in range(N):
        i = k % n; j = (k + 1) % n
        out.append(buf[i])
        buf[i] = decay * 0.5 * (buf[i] + buf[j])
    pk = max(abs(x) for x in out) or 1
    return [amp * x / pk for x in out]
def phrase():
    note = pluck(82.41, 1.6, 1.0, 1)
    chord_f = (82.41, 123.47, 164.81, 207.65, 246.94, 329.63)
    N = int(2.4 * SR); chord = [0.0] * N
    for j, f in enumerate(chord_f):
        p = pluck(f, 2.4, 1.0 / (1 + 0.15 * j), 10 + j)
        off = int(j * 0.012 * SR)
        for k in range(N - off): chord[k + off] += p[k]
    s = [0.0] * int(0.1 * SR)
    pk = max(abs(x) for x in note); s += [0.150 * x / pk for x in note]
    pk = max(abs(x) for x in chord); s += [0.250 * x / pk for x in chord]
    return s
