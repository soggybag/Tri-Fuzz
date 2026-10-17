"""Render Tri-Fuzz audio clips through ngspice. usage: render.py <clip name> [...]  (or 'list')
Output: docs/sim-audio/<name>.wav (through a simple cab filter) and docs/sim-audio/di/<name>.wav (pedal output),
both RMS-normalised; the raw output RMS is logged to docs/sim-audio/levels.txt so loudness differences are known."""
import sys, os, math, struct, wave; sys.path.insert(0, os.path.dirname(__file__))
import guitar
SR = guitar.SR
HERE = os.path.dirname(os.path.abspath(__file__)); OUTD = os.path.join(HERE, '..', '..', 'docs', 'sim-audio')
D = lambda drive, clip='sym', vol=0.7: dict(drive=drive, clip=clip, vol=vol)
NOON, HIGH3, MAX, MIN = 75e3, 200e3, 500e3, 0     # A500k: noon ~15 %, 3 o'clock ~40 % of track
CLIPS = {
 '00_clean_DI':            None,
 '01_single_band_LED':     dict(pre=2.5e3, single=True, low=D(HIGH3)),
 '02_trifuzz_sym':         dict(pre=2.5e3, low=D(HIGH3), mid=D(HIGH3), high=D(HIGH3)),
 '03_trifuzz_mid_not_inverted': dict(pre=2.5e3, low=D(HIGH3), mid=D(HIGH3), high=D(HIGH3), mid_inverted=False),
 '04_trifuzz_asym':        dict(pre=2.5e3, low=D(HIGH3, 'asym'), mid=D(HIGH3, 'asym'), high=D(HIGH3, 'asym')),
 '05_trifuzz_rails':       dict(pre=2.5e3, low=D(HIGH3, 'rails'), mid=D(HIGH3, 'rails'), high=D(HIGH3, 'rails')),
 '06_clean_bass':          dict(pre=2.5e3, low=D(MIN), mid=D(HIGH3), high=D(HIGH3)),
 '07_max_drive':           dict(pre=2.5e3, low=D(MAX), mid=D(MAX), high=D(MAX)),
 '08_low_solo':            dict(pre=2.5e3, low=D(HIGH3), mid=D(HIGH3, vol=0), high=D(HIGH3, vol=0)),
 '09_mid_solo':            dict(pre=2.5e3, low=D(HIGH3, vol=0), mid=D(HIGH3), high=D(HIGH3, vol=0)),
 '10_high_solo':           dict(pre=2.5e3, low=D(HIGH3, vol=0), mid=D(HIGH3, vol=0), high=D(HIGH3)),
 '11_low_drive_noon':      dict(pre=2.5e3, low=D(NOON), mid=D(NOON), high=D(NOON)),
}
def biquad(x, b, a):
    y = []; x1 = x2 = y1 = y2 = 0.0
    for v in x:
        o = b[0] * v + b[1] * x1 + b[2] * x2 - a[1] * y1 - a[2] * y2
        x2, x1, y2, y1 = x1, v, y1, o; y.append(o)
    return y
def lp(f, q):
    w = 2 * math.pi * f / SR; al = math.sin(w) / (2 * q); c = math.cos(w); a0 = 1 + al
    return [(1 - c) / 2 / a0, (1 - c) / a0, (1 - c) / 2 / a0], [1, -2 * c / a0, (1 - al) / a0]
def hp(f, q):
    w = 2 * math.pi * f / SR; al = math.sin(w) / (2 * q); c = math.cos(w); a0 = 1 + al
    return [(1 + c) / 2 / a0, -(1 + c) / a0, (1 + c) / 2 / a0], [1, -2 * c / a0, (1 - al) / a0]
def peak(f, q, gdb):
    A = 10 ** (gdb / 40); w = 2 * math.pi * f / SR; al = math.sin(w) / (2 * q); c = math.cos(w); a0 = 1 + al / A
    return [(1 + al * A) / a0, -2 * c / a0, (1 - al * A) / a0], [1, -2 * c / a0, (1 - al / A) / a0]
def cab(x):
    """rough 1x12 guitar cab: 80 Hz high-pass, ~100 Hz resonance, 2.5 kHz presence, steep roll-off above ~4.5 kHz"""
    for b, a in (hp(80, 0.7), peak(110, 1.2, 3), peak(2500, 1.0, 3), lp(4500, 0.54), lp(4500, 1.31)): x = biquad(x, b, a)
    return x
def rms(x): return math.sqrt(sum(v * v for v in x) / len(x))
def write(path, x, target_db=-20):
    g = 10 ** (target_db / 20) / (rms(x) or 1); y = [v * g for v in x]
    pk = max(abs(v) for v in y)
    if pk > 0.98: y = [v * 0.98 / pk for v in y]
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b''.join(struct.pack('<h', int(max(-1, min(1, v)) * 32767)) for v in y))
def run(name):
    import ng, trifuzz_net as tn
    sig = guitar.phrase()
    if CLIPS[name] is None:
        out = sig
    else:
        src = 'VIN in 0 PWL(' + ' '.join(f'{k / SR:.6f} {v:.5f}' for k, v in enumerate(sig)) + ')'
        dat = os.path.join(OUTD, f'.{name}.dat')
        ng.run(tn.build(CLIPS[name], src), [f'tran {1 / SR} {len(sig) / SR}', 'linearize v(out)', f'wrdata {dat} v(out)'])
        out = [float(l.split()[1]) for l in open(dat) if l.strip()][:len(sig)]
        os.remove(dat)
    os.makedirs(os.path.join(OUTD, 'di'), exist_ok=True)
    write(os.path.join(OUTD, 'di', name + '.wav'), out)
    write(os.path.join(OUTD, name + '.wav'), cab(out))
    with open(os.path.join(OUTD, 'levels.txt'), 'a') as f:
        f.write(f'{name}\t{20 * math.log10(rms(out)):.1f} dBV rms\t{max(abs(v) for v in out):.3f} V peak\n')
    print('done', name, flush=True)
if __name__ == '__main__':
    names = list(CLIPS) if sys.argv[1:] == ['all'] else sys.argv[1:]
    for n in names: run(n)
