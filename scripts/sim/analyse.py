"""Band energies of the chord section of each DI clip (pure-Python biquads). Sub-70 Hz energy in a chord whose lowest
note is E2 (82 Hz) is intermodulation (difference tones): the 'mud' multiband is meant to avoid."""
import wave, struct, math, sys, os
sys.path.insert(0, '.')
from render import lp, hp, biquad, SR
D = '../../docs/sim-audio/di'
def load(n):
    w = wave.open(f'{D}/{n}.wav'); x = struct.unpack(f'<{w.getnframes()}h', w.readframes(w.getnframes())); return [v / 32768 for v in x]
def band(x, lo, hi):
    if lo: x = biquad(biquad(x, *hp(lo, 0.54)), *hp(lo, 1.31))
    if hi: x = biquad(biquad(x, *lp(hi, 0.54)), *lp(hi, 1.31))
    return math.sqrt(sum(v * v for v in x) / len(x))
B = ((None, 65), (65, 400), (400, 2000), (2000, 5000), (5000, None))
print('chord section, dB re total:   <65Hz(IMD)  65-400   400-2k   2k-5k   >5k')
for n in sys.argv[1:]:
    x = load(n)[int(1.85 * SR):int(3.9 * SR)]
    tot = math.sqrt(sum(v * v for v in x) / len(x))
    print(f'{n:30s}', '  '.join(f'{20 * math.log10(band(x, lo, hi) / tot):7.1f}' for lo, hi in B))
