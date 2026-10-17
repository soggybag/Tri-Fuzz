import sys, time; sys.path.insert(0, '.')
import ng, guitar, trifuzz_net as tn
SR = guitar.SR
sig = guitar.phrase()[: int(0.5 * SR)]
pts = ' '.join(f'{k / SR:.6f} {v:.5f}' for k, v in enumerate(sig))
src = 'VIN in 0 PWL(' + pts + ')'
cfg = dict(pre=2.5e3, low=dict(drive=150e3, clip='sym', vol=0.7), mid=dict(drive=150e3, clip='sym', vol=0.7), high=dict(drive=150e3, clip='sym', vol=0.7))
net = tn.build(cfg, src)
t0 = time.time()
o = ng.run(net, [f'tran {1/SR} {len(sig)/SR}', 'print length(time)', f'linearize v(out) v(lf) v(mf) v(hf) v(lo) v(mo) v(ho) v(pre)', 'wrdata q.dat v(out) v(pre) v(lo) v(mo) v(ho)'])
print(round(time.time() - t0, 1), 's', [l for l in o if 'length' in l or 'rror' in l][:5])
rows = [list(map(float, l.split())) for l in open('q.dat') if l.strip()]
for c, nm in ((1, 'out'), (3, 'pre'), (5, 'lo'), (7, 'mo'), (9, 'ho')):
    v = [r[c] for r in rows]; print(nm, 'min', round(min(v), 3), 'max', round(max(v), 3))
