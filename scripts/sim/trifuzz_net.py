"""SPICE netlist of the Tri-Fuzz v0.3 signal path (mirrors TriFuzz.kicad_sch values), with a behavioural op-amp:
gain 1e5, GBW 3 MHz, output limited to 1.5 V inside the 0 / 9 V rails (TL07x-like), 50 ohm out.
cfg keys: pre (gain trim ohms), low/mid/high = dict(drive=ohms of the 500k pot, clip='sym'|'rails'|'asym', vol=0..1),
mid_inverted (True = v0.3, False = v0.1-style all same polarity), single (True = one full-range LED clipper instead)."""
OPAMP = """.options method=gear reltol=2e-3 abstol=1e-9 vntol=1e-5 itl4=50
.subckt OPA inp inn out
Bg n1 0 V = 30*tanh(1e5*(v(inp)-v(inn))/30) + 4.5
Rp n1 n2 1k
Cp n2 0 5.3u
Bo n3 0 V = 4.5 + (v(n2)-4.5)/pow(1+pow(abs((v(n2)-4.5)/3),8),0.125)
Ro n3 out 50
.ends
.model D1N4148 D(Is=2.52n Rs=0.568 N=1.752 Cjo=4p M=0.4 tt=20n)
.model LEDR D(Is=1e-18 N=2 Rs=3 Cjo=20p)
"""
CLIPS = {'LOW': {'sym': (['LEDR'], ['LEDR']), 'asym': (['LEDR'], ['D1N4148'])},
         'MID': {'sym': (['D1N4148'] * 2, ['D1N4148'] * 2), 'asym': (['D1N4148'] * 2, ['D1N4148'])},
         'HIGH': {'sym': (['D1N4148'], ['D1N4148']), 'asym': (['D1N4148'] * 2, ['D1N4148'])}}
def diodes(tag, neg, out, mode, band, L):
    """diode strings between the - node and the output; pos strings anode at the output"""
    if mode == 'rails': return
    pos_s, neg_s = CLIPS[band][mode]
    for kind, chain, anode_out in (('p', pos_s, True), ('n', neg_s, False)):
        nodes = [neg] + [f'{tag}{kind}{i}' for i in range(len(chain) - 1)] + [out]
        for i, m in enumerate(chain):
            a, b = nodes[i], nodes[i + 1]          # a toward the - node, b toward the output
            L.append(f'D{tag}{kind}{i} {b} {a} {m}' if anode_out else f'D{tag}{kind}{i} {a} {b} {m}')
def build(cfg, src):
    L = ['tri-fuzz', src, 'VB vb 0 DC 4.5', 'R3 in 0 1meg', 'C5 in p 100n', 'R4 p vb 1meg',
         'XU1A p m1 pre OPA', 'R5 m1 pre 4.7k', 'C7 m1 pre 220p', 'R6 m1 g1 2.2k', 'C8 g1 g2 4.7u', f'RV1 g2 vb {cfg["pre"]}']
    out_nodes = []
    if cfg.get('single'):
        b = cfg['low']
        L += ['C20 pre sa 4.7u', 'R10 sa sm 3.3k', 'XS vb sm so OPA', f'Rf sm sf {10e3 + b["drive"]}', 'Rf2 sf so 1', 'C11 sm so 47p']
        diodes('S', 'sm', 'so', b['clip'], 'LOW', L)
        out_nodes.append(('so', b['vol'], '4.7n'))   # neutral: 47p / ~10 kHz post filter, like HIGH
    else:
        # LOW: MFB LP, R8 4k7 + RV9 trim (10k = 225 Hz)
        L += ['R7 pre la 15k', 'R9 la lf 15k', 'R8 la lm 14.7k', 'C10 la vb 100n', 'C9 lm lf 22n', 'XU1B vb lm lf OPA']
        # MID: MFB BP, R24 4k7 + RV10 trim (13k = 735 Hz)
        L += ['R12 pre ma 22k', 'C12 ma mm 10n', 'C13 ma mf 10n', 'R13 mm mf 47k', 'R24 ma vb 17.7k', 'XU1C vb mm mf OPA']
        # HIGH: MFB HP, R17 1k2 + RV11 trim (2k = 2.26 kHz)
        L += ['C15 pre ha 10n', 'C16 ha hm 10n', 'C17 ha hf 10n', 'R16 hm hf 15k', 'R17 ha vb 3.2k', 'XU1D vb hm hf OPA']
        # clippers
        b = cfg['low']
        L += ['C20 lf l1 4.7u', 'R10 l1 ln 3.3k', 'XU2A vb ln lo OPA', f'R11 ln lo {10e3 + b["drive"]}', 'C11 ln lo 220p']
        diodes('L', 'ln', 'lo', b['clip'], 'LOW', L)
        b = cfg['mid']
        if cfg.get('mid_inverted', True):
            L += ['XU2B mf mn mo OPA', 'R14 mn m2 3.3k', 'C21 m2 vb 2.2u']
        else:
            L += ['C21 mf m2 2.2u', 'R14 m2 mn 3.3k', 'XU2B vb mn mo OPA']
        L += [f'R15 mn mo {10e3 + b["drive"]}', 'C14 mn mo 47p']
        diodes('M', 'mn', 'mo', b['clip'], 'MID', L)
        b = cfg['high']
        L += ['C22 hf h1 1u', 'R18 h1 hn 3.3k', 'XU2C vb hn ho OPA', f'R19 hn ho {10e3 + b["drive"]}', 'C18 hn ho 22p']
        diodes('H', 'hn', 'ho', b['clip'], 'HIGH', L)
        out_nodes += [('lo', cfg['low']['vol'], '33n'), ('mo', cfg['mid']['vol'], '6.8n'), ('ho', cfg['high']['vol'], '4.7n')]
    # post-clip DC block + low-pass + VOLUME (A10k as a divider) + 10k into the mixer
    for i, (node, vol, cp) in enumerate(out_nodes):
        L += [f'Cc{i} {node} c{i} 1u', f'Rp{i} c{i} t{i} 4.7k', f'Cq{i} t{i} vb {cp}',
              f'Rt{i} t{i} w{i} {max(1, 10e3 * (1 - vol))}', f'Rb{i} w{i} vb {max(1, 10e3 * vol)}', f'Rm{i} w{i} sm2 10k']
    L += ['R23 sm2 mx 2.2k', 'XU2D vb sm2 mx OPA', 'C19 mx out 10u', 'RV5 out 0 100k'] + OPAMP.strip().split('\n') + ['.end']
    return L
