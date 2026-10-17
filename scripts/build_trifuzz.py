"""Tri-Fuzz: three-band multiband distortion for guitar (after Craig Anderton's Quadrafuzz and a 3-band variant,
docs/variant_schematic.gif). 9 V single supply, two TL074s.
  v0.3 (2026-10-09): CLIP = symmetric / rails / asymmetric per band (LOW LEDs, MID 2xSi, HIGH Si), trimmable
    crossovers (RV9-RV11), DC block + post-clip low-pass per band, CUT removed (6 knobs + 3 toggles)
  v0.2 (2026-10-09): per-band DRIVE / VOLUME / CLIP, MID band inverted, Terrarium-style 125B controls
  - U1A input / PRE trim: non-inverting, 4k7 || 47p feedback, ground leg 2k2 + 4u7 + PRE trim 50k (x1.1 to x3.1);
    kept low so a hot pickup can't clip U1A before the bands split (v0.3: 22k, x11)
  - three inverting MFB filters:
      LOW  U1B  MFB low-pass  15k/15k/15k, 100n + 22n   fc ~225 Hz,  Q 0.71
      MID  U1C  MFB band-pass 10k in, 47k fb, 10n + 10n  f0 ~735 Hz,  Q ~1.1, gain 2.35
      HIGH U1D  MFB high-pass 10n x3, 3k3 + 15k          fc ~2.26 kHz, Q 0.71
  - three clippers U2A-C, feedback = 10k + DRIVE A500k (rheostat) || Cf, CLIP toggle ON-OFF-ON: red LED pair / none
    (op-amp rail clipping) / 1N4148 pair. LOW and HIGH inverting (C + 3k3 in, x3 to x155); MID NON-inverting
    (3k3 + C gain leg to VB, x4 to x156) so MID arrives at the mixer in opposite polarity to its neighbours: the
    2nd-order crossovers then sum flat instead of notching (-22 dB at ~300 Hz, -34 dB at ~1.6 kHz when all matched).
  - LOW / MID / HIGH VOLUME pots (A10k, returned to VB), inverting mixer U2D (10k in, 2k2 fb), CUT toggle (22n across
    the feedback, ~3.3 kHz), OUTPUT trim
Breadboard-first: no footprints yet.
usage: build_trifuzz.py <out.kicad_sch>"""
from sch import *
import sys
OUT = sys.argv[1]
g = lambda n: round(n * 2.54, 3)
s = Sheet('TriFuzz', 'A1')
W = lambda *p: s.wire(*p)
P = s.P
def GND(p): s.power('GND', p)
def V9(p): s.power('+9V', p)
def lab(n, p, side='r'): s.label(n, p, side)
def R_(ref, v, cx, cy, rot, d=''): s.part(ref, 'Device', 'R', v, cx, cy, rot, desc=d, text='t' if rot == 90 else 'r')
def C_(ref, v, cx, cy, rot, d=''): s.part(ref, 'Device', 'C', v, cx, cy, rot, desc=d, text='t' if rot == 90 else 'r')
def EL(kind, ref, v, cx, cy, rot, d=''): (R_ if kind == 'R' else C_)(ref, v, cx, cy, rot, d)
def CPv(ref, v, x, cy, d=''): s.part(ref, 'Device', 'C_Polarized', v, x, cy, 0, desc=d, text='r')
PINS = {1: ('3', '2', '1'), 2: ('5', '6', '7'), 3: ('10', '9', '8'), 4: ('12', '13', '14')}
def OP(ref, unit, x, ytop):
    s.part(ref, 'Amplifier_Operational', 'TL074', 'TL074', x, ytop + 2.54, 0, unit=unit, text='ic')
    pl, mi, ou = PINS[unit]
    return P(ref, pl), P(ref, mi), P(ref, ou)
def vb_plus(pl):
    W(pl, (pl[0] - g(6), pl[1])); lab('VB', (pl[0] - g(6), pl[1]), 'l')

def mfb(ref, unit, x, ytop, el, in_lab, out_lab, title):
    """inverting multiple-feedback filter. el = dict of (kind, ref, value) for:
       'in' (input -> A), 'am' (A -> -), 'mo' (- -> out), 'ao' (A -> out), 'avb' (A -> VB, optional)"""
    pl, mi, ou = OP(ref, unit, x, ytop)
    vb_plus(pl)
    M = (mi[0] - g(1), mi[1])
    A = (M[0] - g(1) - 7.62 - g(1) - (7.62 + g(1) if 'am_trim' in el else 0), mi[1])
    rx = ou[0] + g(1)
    W(mi, M)
    k, r, v = el['am']; EL(k, r, v, M[0] - g(1) - 3.81, mi[1], 90); W(P(r, '2'), (M[0] - g(1), mi[1]), M)
    if 'am_trim' in el:  # series rheostat trimmer between A and the fixed resistor (crossover tuning)
        tr, tv, tdesc = el['am_trim']; tc = P(r, '1')[0] - g(0.5) - 3.81
        s.part(tr, 'Device', 'R_Potentiometer_Trim', tv, tc, mi[1], 90, desc=tdesc, text=((tc, mi[1] + g(1.4)), (tc, mi[1] + g(2.5)), None))
        W(P(tr, '3'), P(r, '1')); w = P(tr, '2'); W(w, (P(tr, '3')[0], w[1]), P(tr, '3')); W(A, P(tr, '1'))
    else:
        W(A, (A[0] + g(1), A[1]), P(r, '1'))
    k, r, v = el['in']; EL(k, r, v, A[0] - g(1) - 3.81, mi[1], 90); W(P(r, '2'), (A[0] - g(1), mi[1]), A)
    q = P(r, '1'); W(q, (q[0] - g(2), q[1])); lab(in_lab, (q[0] - g(2), q[1]), 'l')
    f1 = mi[1] + g(4); f2 = mi[1] + g(8)
    W(M, (M[0], f1))
    k, r, v = el['mo']; EL(k, r, v, (M[0] + rx) / 2, f1, 90); W((M[0], f1), P(r, '1')); W(P(r, '2'), (rx, f1))
    W(A, (A[0], f2))
    k, r, v = el['ao']; EL(k, r, v, (A[0] + rx) / 2, f2, 90); W((A[0], f2), P(r, '1')); W(P(r, '2'), (rx, f2))
    W(ou, (rx, ou[1])); W((rx, ou[1]), (rx, f2))
    if 'avb' in el:
        k, r, v = el['avb']; EL(k, r, v, A[0], f2 + g(1) + 3.81, 0); W((A[0], f2), P(r, '1'))
        q = P(r, '2')
        if 'avb_trim' in el:  # series rheostat trimmer to VB (crossover tuning)
            tr, tv, tdesc = el['avb_trim']
            s.part(tr, 'Device', 'R_Potentiometer_Trim', tv, q[0], q[1] + g(1) + 3.81, 0, desc=tdesc, text='l')
            W(q, P(tr, '1')); w = P(tr, '2'); p3 = P(tr, '3'); W(w, (w[0], p3[1]), p3); q = p3
        W(q, (q[0], q[1] + g(1))); lab('VB', (q[0], q[1] + g(1)), 'l')
    W((rx, ou[1]), (rx + g(4), ou[1])); lab(out_lab, (rx + g(4), ou[1]))
    s.text(title, A[0] - g(6), ytop - g(5))

DIODE = {'LED': ('LED', 'red LED', 'Clipping LED (~1.8 V)'), 'Si': ('D', '1N4148W', 'Clipping diode (Si, ~0.65 V)')}
def clipper(ref, unit, x, ytop, parts, inverting, cf_val, cin_val, in_lab, out_lab, name, nets, drefs):
    """parts = (Rin/Rg 3k3, Rmin 10k, Cf, Cin/Cg, DRIVE pot, CLIP switch)
    nets = (sym, asym); each = (pos string, neg string), a string = list of 'LED' / 'Si' in series.
    pos strings have their anodes toward the output (they limit the positive swing). Asymmetric networks all put the
    bigger drop on the positive side, so every band's even-order products and DC shift come out the same sign."""
    rin, rmin, cf, cin, pot, sw = parts
    drefs = list(drefs)
    pl, mi, ou = OP(ref, unit, x, ytop)
    R_(rin, '3k3', mi[0] - 6.35, mi[1], 90, 'Clipper input (x3 to x155)' if inverting else 'Gain leg to VB (x4 to x156)'); W(P(rin, '2'), mi)
    C_(cin, cin_val, P(rin, '1')[0] - g(1) - 3.81, mi[1], 90, 'DC block: offsets are not amplified' if inverting else 'Gain-leg DC block (DC gain 1)')
    W(P(cin, '2'), P(rin, '1')); q = P(cin, '1'); W(q, (q[0] - g(2), q[1]))
    if inverting:
        vb_plus(pl); lab(in_lab, (q[0] - g(2), q[1]), 'l')
    else:
        lab('VB', (q[0] - g(2), q[1]), 'l')
        W(pl, (q[0] - g(2), pl[1])); lab(in_lab, (q[0] - g(2), pl[1]), 'l')
    L = P(rin, '2')[0]; xd = L + g(2) + 15.24; rx = xd + g(2) + 10.16 + g(1)
    r0, r1 = mi[1] + g(4), mi[1] + g(8)
    rows = [mi[1] + g(k) for k in (13, 15, 21, 23)]
    W((L, mi[1]), (L, rows[3])); W(ou, (rx, ou[1])); W((rx, ou[1]), (rx, r1))
    R_(rmin, '10k', L + g(1) + 3.81, r0, 90, 'Minimum drive'); W((L, r0), P(rmin, '1'))
    pc = P(rmin, '2')[0] + g(1) + 3.81
    s.part(pot, 'Device', 'R_Potentiometer', 'A500k', pc, r0, 90, desc=f'{name} DRIVE (rheostat)', extra={'Panel': f'{name} DRIVE'},
           text=((pc + g(3), r0 + g(1.2)), (pc + g(3), r0 + g(2.4)), 'left'))
    W(P(rmin, '2'), P(pot, '1')); w = P(pot, '2'); p3 = P(pot, '3')
    W(w, (p3[0], w[1]), p3); W(p3, (rx, r0))
    s.part(cf, 'Device', 'C', cf_val, L + g(1) + 3.81, r1, 90, desc='HF roll-off', text='b'); W((L, r1), P(cf, '1')); W(P(cf, '2'), (rx, r1))
    def string(kinds, y, pos):
        cx = L + g(1); W((L, y), (cx, y))
        for i, kd in enumerate(kinds):
            sym, val, desc = DIODE[kd]; dref = drefs.pop(0)
            s.part(dref, 'Device', sym, val, cx + 3.81, y, 0 if pos else 180, desc=desc, text='t' if pos else 'b', hideval=len(kinds) > 1)
            a_, k_ = P(dref, '2'), P(dref, '1')
            left, right = (k_, a_) if pos else (a_, k_)
            W((cx, y), left); cx = right[0]
        W((cx, y), (xd, y))
    for (posk, negk), yp, yn in ((nets[0], rows[0], rows[1]), (nets[1], rows[2], rows[3])):
        string(posk, yp, True); string(negk, yn, False); W((xd, yp), (xd, yn))
    sy = mi[1] + g(18); sx = xd + g(2) + 5.08
    s.part(sw, 'Switch', 'SW_SPDT', 'ON-OFF-ON', sx, sy, 0, mirror='y', desc=f'{name} CLIP: symmetric / op-amp rails (centre) / asymmetric (even-order)',
           extra={'Panel': f'{name} CLIP'}, text=((sx, sy + g(2.5)), (sx, sy + g(3.7)), None))
    W((xd, rows[1]), (xd, P(sw, '1')[1]), P(sw, '1')); W((xd, rows[2]), (xd, P(sw, '3')[1]), P(sw, '3'))
    W(P(sw, '2'), (rx, sy), (rx, r1))
    W((rx, ou[1]), (rx + g(4), ou[1])); lab(out_lab, (rx + g(4), ou[1]))

def level(ref, name, x, y, in_lab, out_lab, post):
    """clipper out -> Cc (DC block: asymmetric clipping shifts the average) -> Rp -> Cp to VB (post-clip low-pass: keeps
    the band's own harmonics from spraying far above it) -> VOLUME (A10k, returned to VB)"""
    cc, rp, cp, cpv, fdesc = post
    top = y - 3.81; xs = x - g(12)
    lab(in_lab, (xs, top), 'l')
    C_(cc, '1u', xs + g(1) + 3.81, top, 90, 'DC block after the clipper'); W((xs, top), P(cc, '1'))
    R_(rp, '4k7', P(cc, '2')[0] + g(1) + 3.81, top, 90, f'Post-clip low-pass ({fdesc})'); W(P(cc, '2'), P(rp, '1'))
    nd = (P(rp, '2')[0] + g(1), top); W(P(rp, '2'), nd)
    s.part(cp, 'Device', 'C', cpv, nd[0], top + g(1) + 3.81, 0, desc=f'Post-clip low-pass ({fdesc})', text='l')
    W(nd, P(cp, '1')); q = P(cp, '2'); W(q, (q[0], q[1] + g(1))); lab('VB', (q[0], q[1] + g(1)), 'l')
    s.part(ref, 'Device', 'R_Potentiometer', 'A10k', x, y, 0, mirror='x', desc=f'{name} VOLUME', extra={'Panel': f'{name} VOL'},
           text=((x + g(2), y + g(2)), (x + g(2), y + g(3.5)), 'left'))
    W(nd, (x, top))
    q = P(ref, '1'); W(q, (q[0], q[1] + g(1))); lab('VB', (q[0], q[1] + g(1)), 'l')
    w = P(ref, '2'); W(w, (w[0] + g(3), w[1])); lab(out_lab, (w[0] + g(3), w[1]))

# ================================================================ POWER + JACKS
s.box('POWER + BIAS + JACKS', g(4), g(6), g(38), g(62))
lab('9V_IN', (g(7), g(12)), 'l')
s.part('D1', 'Device', 'D_Schottky', '1N5817', g(12), g(12), 180, desc='Reverse-polarity protection', text='t')
W((g(7), g(12)), P('D1', '2')); W(P('D1', '1'), (g(18), g(12)))
V9((g(18), g(12))); s.power('PWR_FLAG', (g(18), g(12)))
W((g(18), g(12)), (g(30), g(12)))
CPv('C1', '100u', g(22), g(15.5), d='Supply reservoir'); W((g(22), g(12)), P('C1', '1')); GND(P('C1', '2'))
s.part('C2', 'Device', 'C', '100n', g(26), g(15.5), 0, desc='U1 decoupling', text='r'); W((g(26), g(12)), P('C2', '1')); GND(P('C2', '2'))
s.part('C3', 'Device', 'C', '100n', g(30), g(15.5), 0, desc='U2 decoupling', text='r'); W((g(30), g(12)), P('C3', '1')); GND(P('C3', '2'))
R_('R1', '10k', g(9), g(26), 0); V9(P('R1', '1'))
R_('R2', '10k', g(9), g(34), 0); GND(P('R2', '2'))
W(P('R1', '2'), P('R2', '1'))
W((g(9), g(30)), (g(15), g(30)), (g(15), g(33.5) - 3.81)); CPv('C4', '100u', g(15), g(33.5), d='VB filter: stiff, the level pots return here'); GND(P('C4', '2'))
W((g(15), g(30)), (g(19), g(30))); lab('VB', (g(19), g(30))); s.power('PWR_FLAG', (g(19), g(30)))
s.part('U1', 'Amplifier_Operational', 'TL074', 'TL074', g(26), g(40), 0, unit=5, text='ic'); V9(P('U1', '4')); GND(P('U1', '11'))
s.part('U2', 'Amplifier_Operational', 'TL074', 'TL074', g(33), g(40), 0, unit=5, text='ic'); V9(P('U2', '4')); GND(P('U2', '11'))
s.part('J1', 'Connector_Generic', 'Conn_01x02', '9V / GND', g(8), g(47), 180, text=((g(6), g(44)), (g(6), g(45.5)), 'right'))
q = P('J1', '1'); W(q, (q[0] + g(3), q[1])); lab('9V_IN', (q[0] + g(3), q[1]))
q = P('J1', '2'); W(q, (q[0] + g(3), q[1])); GND((q[0] + g(3), q[1])); s.power('PWR_FLAG', (q[0] + g(3), q[1]))
s.part('J2', 'Connector_Generic', 'Conn_01x03', 'IN / OUT / GND', g(8), g(54), 180, text=((g(6), g(50)), (g(6), g(51.5)), 'right'))
for pin, net in (('1', 'IN'), ('2', 'OUT')):
    q = P('J2', pin); W(q, (q[0] + g(3), q[1])); lab(net, (q[0] + g(3), q[1]))
q = P('J2', '3'); W(q, (q[0] + g(3), q[1])); GND((q[0] + g(3), q[1]))

# ================================================================ INPUT / DRIVE
s.box('INPUT / PRE (U1A): gain 1 + 4k7 / (2k2 + PRE trim) = x1.1 to x3.1 (stays clean)', g(42), g(6), g(108), g(62))
y = g(16)
lab('IN', (g(45), y), 'l'); W((g(45), y), (g(49), y))
R_('R3', '1M', g(49), y + g(3.5), 0, 'Input pull-down'); W((g(49), y), P('R3', '1')); GND(P('R3', '2'))
W((g(49), y), (g(51), y)); C_('C5', '100n', g(52.5), y, 90, 'Input coupling'); W((g(51), y), P('C5', '1'))
W(P('C5', '2'), (g(57), y))
R_('R4', '1M', g(57), y + g(3.5), 0, 'Bias to VB (1M input)'); W((g(57), y), P('R4', '1'))
q = P('R4', '2'); W(q, (q[0], q[1] + g(1))); lab('VB', (q[0], q[1] + g(1)), 'l')
pl, mi, ou = OP('U1', 1, g(78), y)
W((g(57), y), pl)
NX = mi[0] - g(1); rx = ou[0] + g(1)
W(mi, (NX, mi[1])); W((NX, mi[1]), (NX, mi[1] + g(7)))
R_('R5', '4k7', (NX + rx) / 2, mi[1] + g(4), 90, 'PRE feedback (max x3.1)'); W((NX, mi[1] + g(4)), P('R5', '1')); W(P('R5', '2'), (rx, mi[1] + g(4)))
C_('C7', '220p', (NX + rx) / 2, mi[1] + g(7), 90, 'HF limit (150 kHz)'); W((NX, mi[1] + g(7)), P('C7', '1')); W(P('C7', '2'), (rx, mi[1] + g(7)))
W(ou, (rx, ou[1])); W((rx, ou[1]), (rx, mi[1] + g(7)))
GX = NX - g(5)
W((NX, mi[1]), (GX, mi[1]))
R_('R6', '2k2', GX, mi[1] + g(1) + 3.81, 0, 'Max-gain limit'); W((GX, mi[1]), P('R6', '1'))
CPv('C8', '4u7', GX, P('R6', '2')[1] + g(1) + 3.81, d='DC block in the gain leg (variant: 5u)'); W(P('R6', '2'), P('C8', '1'))
top = P('C8', '2')[1] + g(1)
W(P('C8', '2'), (GX, top))
s.part('RV1', 'Device', 'R_Potentiometer_Trim', '50k', GX, top + 3.81, 0, mirror='x', desc='PRE trim (internal, 3362P): overall gain into all bands',
       text=((GX - g(5), top + g(1)), (GX - g(5), top + g(2.5)), 'right'))
W((GX, top), P('RV1', '3'))
w2 = P('RV1', '2'); p1 = P('RV1', '1')
W(w2, (w2[0] + g(1), w2[1]), (w2[0] + g(1), p1[1] + g(1)), (p1[0], p1[1] + g(1)))
W(p1, (p1[0], p1[1] + g(2))); lab('VB', (p1[0], p1[1] + g(2)), 'l')
W((rx, ou[1]), (rx + g(4), ou[1])); lab('PRE', (rx + g(4), ou[1]))

# ================================================================ BANDS
s.box('BANDS: inverting MFB filters (U1B-D) -> clippers with DRIVE + CLIP (U2A-C; MID non-inverting = polarity flip) -> VOLUME', g(112), g(6), g(272), g(150))
bands = (
    ('LOW', 2, g(24), {'in': ('R', 'R7', '15k'), 'am': ('R', 'R8', '4k7'), 'mo': ('C', 'C9', '22n'), 'ao': ('R', 'R9', '15k'),
                        'avb': ('C', 'C10', '100n'), 'am_trim': ('RV9', '20k', 'LOW crossover trim: ~400 Hz (0) to ~180 Hz (20k); 225 Hz at ~10k')},
     'LOW: MFB low-pass, fc ~180-400 Hz (trim), Q ~0.7, gain -1',
     ('R10', 'R11', 'C11', 'C20', 'RV6', 'SW1'), True, '220p', '4u7',
     ((['LED'], ['LED']), (['LED'], ['Si'])), ('D2', 'D3', 'D8', 'D9'),
     'RV2', ('C24', 'R25', 'C27', '33n', '~1.5 kHz')),
    ('MID', 3, g(70), {'in': ('R', 'R12', '22k'), 'am': ('C', 'C12', '10n'), 'mo': ('R', 'R13', '47k'), 'ao': ('C', 'C13', '10n'),
                       'avb': ('R', 'R24', '4k7'), 'avb_trim': ('RV10', '50k', 'MID centre trim: ~1.18 kHz (0) to ~590 Hz (50k); 735 Hz at ~13k')},
     'MID: MFB band-pass, f0 ~590-1180 Hz (trim), Q ~0.9-1.7, gain -1.07',
     ('R14', 'R15', 'C14', 'C21', 'RV7', 'SW2'), False, '47p', '2u2',
     ((['Si', 'Si'], ['Si', 'Si']), (['Si', 'Si'], ['Si'])), ('D4', 'D5', 'D10', 'D11', 'D14', 'D15', 'D16'),
     'RV3', ('C25', 'R26', 'C28', '6n8', '~7 kHz')),
    ('HIGH', 4, g(116), {'in': ('C', 'C15', '10n'), 'am': ('C', 'C16', '10n'), 'mo': ('R', 'R16', '15k'), 'ao': ('C', 'C17', '10n'),
                          'avb': ('R', 'R17', '1k2'), 'avb_trim': ('RV11', '5k', 'HIGH crossover trim: ~3.75 kHz (0) to ~1.65 kHz (5k); 2.26 kHz at ~2k')},
     'HIGH: MFB high-pass, fc ~1.65-3.75 kHz (trim), Q ~0.5-1.2, gain -1',
     ('R18', 'R19', 'C18', 'C22', 'RV8', 'SW3'), True, '22p', '1u',
     ((['Si'], ['Si']), (['Si', 'Si'], ['Si'])), ('D6', 'D7', 'D12', 'D13', 'D17'),
     'RV4', ('C26', 'R27', 'C29', '4n7', '~10 kHz')),
)
for name, unit, yb, el, title, cl, inv, cf, cin, nets, drefs, pot, post in bands:
    mfb('U1', unit, g(150), yb, el, 'PRE', name + '_F', title)
    clipper('U2', unit - 1, g(200), yb, cl, inv, cf, cin, name + '_F', name + '_C', name, nets, drefs)
    level(pot, name, g(256), yb + g(6), name + '_C', name + '_L', post)

# ================================================================ MIXER + OUTPUT
s.box('MIXER (U2D): inverting sum, 10k in / 2k2 fb (x0.22 per band), OUTPUT trim', g(276), g(6), g(326), g(80))
pl, mi, ou = OP('U2', 4, g(296), g(30))
vb_plus(pl)
tapx = mi[0] - g(1)
W(mi, (tapx, mi[1]))
for i, (ref, name) in enumerate((('R20', 'LOW'), ('R21', 'MID'), ('R22', 'HIGH'))):
    yy = mi[1] + g(3 * i)
    R_(ref, '10k', tapx - g(1) - 3.81, yy, 90, f'{name} into the mixer')
    W(P(ref, '2'), (tapx, yy))
    q = P(ref, '1'); W(q, (q[0] - g(2), q[1])); lab(name + '_L', (q[0] - g(2), q[1]), 'l')
fy = mi[1] + g(10); rx = ou[0] + g(1)
W((tapx, mi[1]), (tapx, fy))
R_('R23', '2k2', (tapx + rx) / 2, fy, 90, 'Mixer feedback (variant: 2k2)'); W((tapx, fy), P('R23', '1')); W(P('R23', '2'), (rx, fy))
W(ou, (rx, ou[1])); W((rx, ou[1]), (rx, fy))
W((rx, ou[1]), (rx + g(2), ou[1])); C_('C19', '10u', rx + g(2) + 3.81, ou[1], 90, 'Output coupling')
W(P('C19', '2'), (rx + g(9), ou[1]))
s.part('RV5', 'Device', 'R_Potentiometer_Trim', '100k', rx + g(9), ou[1] + 3.81, 0, mirror='x', desc='OUTPUT trim (internal): sets unity with the bypass',
       text=((rx + g(11), ou[1] + g(3)), (rx + g(11), ou[1] + g(4.5)), 'left'))
GND(P('RV5', '1'))
w = P('RV5', '2'); W(w, (w[0] + g(4), w[1])); lab('OUT', (w[0] + g(4), w[1]))
for i, line in enumerate(('CLIP per band (up / centre / down): symmetric / op-amp rails / asymmetric.',
                          'LOW  LED-LED (+-1.8 V)   / rails / LED+ Si- (+1.8 / -0.65)',
                          'MID  2Si-2Si (+-1.3 V)   / rails / 2Si+ Si- (+1.3 / -0.65)',
                          'HIGH Si-Si (+-0.65 V)    / rails / 2Si+ Si- (+1.3 / -0.65)',
                          'Asymmetric = even-order harmonics; the bigger drop is on the + side in every band.',
                          'Panel (125B): row 1 LOW / MID / HIGH VOL, row 2 DRIVE, row 3 CLIP toggles.',
                          'Internal trims: PRE, OUTPUT, LOW / MID / HIGH crossover.')):
    s.text(line, g(278), g(56 + 2.5 * i))
s.write(OUT, title_block={'title': 'Tri-Fuzz (multiband, 9 V)', 'rev': '0.3', 'company': 'Super-Freq',
                         'comments': ['After Craig Anderton Quadrafuzz and a 3-band variant', 'Per-band VOL / DRIVE / CLIP (sym / rails / asym), trim crossovers, MID inverted']})
print('written', OUT)
