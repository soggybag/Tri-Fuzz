"""Intermodulation measure for the chord section: FFT (pure Python, radix-2), energy within +-2.5 Hz... (a few bins) of
any harmonic of the six chord notes (up to 5 kHz) = 'harmonic'; everything else from 40 Hz to 5 kHz = 'inharmonic'
(intermodulation sum/difference tones). Ratio inharmonic/harmonic in dB: lower = cleaner chords."""
import wave, struct, math, cmath, sys
SR = 44100; D = '../../docs/sim-audio/di'
NOTES = (82.41, 123.47, 164.81, 207.65, 246.94, 329.63)
def load(n):
    w = wave.open(f'{D}/{n}.wav'); x = struct.unpack(f'<{w.getnframes()}h', w.readframes(w.getnframes())); return [v / 32768 for v in x]
def fft(a):
    n = len(a); j = 0; a = list(a)
    for i in range(1, n):
        bit = n >> 1
        while j & bit: j ^= bit; bit >>= 1
        j |= bit
        if i < j: a[i], a[j] = a[j], a[i]
    L = 2
    while L <= n:
        w = cmath.exp(-2j * math.pi / L)
        for s in range(0, n, L):
            wk = 1
            for k in range(L // 2):
                u = a[s + k]; v = a[s + k + L // 2] * wk
                a[s + k] = u + v; a[s + k + L // 2] = u - v; wk *= w
        L <<= 1
    return a
N = 65536
for n in sys.argv[1:]:
    x = load(n)[int(1.95 * SR):int(1.95 * SR) + N]
    win = [0.5 - 0.5 * math.cos(2 * math.pi * i / (N - 1)) for i in range(N)]
    X = fft([a * b for a, b in zip(x, win)])
    df = SR / N
    harm = set()
    for f0 in NOTES:
        k = 1
        while f0 * k < 5000:
            c = f0 * k / df
            for b in range(int(c) - 4, int(c) + 6): harm.add(b)
            k += 1
    eh = ei = 0.0
    for b in range(int(40 / df), int(5000 / df)):
        p = abs(X[b]) ** 2
        if b in harm: eh += p
        else: ei += p
    print(f'{n:30s} inharmonic/harmonic = {10 * math.log10(ei / eh):6.1f} dB')
