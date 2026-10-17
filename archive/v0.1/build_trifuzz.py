"""Tri-Fuzz: three-band multiband distortion for guitar (after Craig Anderton's Quadrafuzz and a 3-band variant,
docs/variant_schematic.gif). 9 V single supply, two TL074s.
  - U1A input / DRIVE: non-inverting, 470k || 10p feedback, ground leg 2k2 + 4u7 + DRIVE (x1.9 to x215)
  - three inverting MFB filters, so all bands arrive at the mixer in the same polarity:
      LOW  U1B  MFB low-pass  15k/15k/15k, 100n + 22n   fc ~225 Hz,  Q 0.71
      MID  U1C  MFB band-pass 10k in, 47k fb, 10n + 10n  f0 ~735 Hz,  Q ~1.1, gain 2.35
      HIGH U1D  MFB high-pass 10n x3, 3k3 + 15k          fc ~2.26 kHz, Q 0.71
  - three clippers U2A-C (as the variant): 3k3 in, 100k || 220p || red LED pair -> x30 into the LEDs
  - LOW / MID / HIGH level pots (A10k, returned to VB), inverting mixer U2D (10k in, 2k2 fb), VOLUME
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
    M = (mi[0] - g(1), mi[1]); A = (M[0] - g(1) - 7.62 - g(1), mi[1])
    rx = ou[0] + g(1)
    W(mi, M)
    k, r, v = el['am']; EL(k, r, v, M[0] - g(1) - 3.81, mi[1], 90); W(P(r, '2'), (M[0] - g(1), mi[1]), M); W(A, (A[0] + g(1), A[1]), P(r, '1'))
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
        q = P(r, '2'); W(q, (q[0], q[1] + g(1))); lab('VB', (q[0], q[1] + g(1)), 'l')
    W((rx, ou[1]), (rx + g(4), ou[1])); lab(out_lab, (rx + g(4), ou[1]))
    s.text(title, A[0] - g(6), ytop - g(5))

def clipper(ref, unit, x, ytop, rin, rf, cf, da, db, in_lab, out_lab):
    pl, mi, ou = OP(ref, unit, x, ytop)
    vb_plus(pl)
    R_(rin, '3k3', mi[0] - 6.35, mi[1], 90, 'Clipper input (x30)'); W(P(rin, '2'), mi)
    q = P(rin, '1'); W(q, (q[0] - g(2), q[1])); lab(in_lab, (q[0] - g(2), q[1]), 'l')
    L = P(rin, '2')[0]; rx = ou[0] + g(3)
    rows = [mi[1] + g(4), mi[1] + g(7), mi[1] + g(10), mi[1] + g(13)]
    W((L, mi[1]), (L, rows[3])); W(ou, (rx, ou[1])); W((rx, ou[1]), (rx, rows[3]))
    R_(rf, '100k', L + g(1) + 3.81, rows[0], 90, 'Clipper feedback'); W((L, rows[0]), P(rf, '1')); W(P(rf, '2'), (rx, rows[0]))
    C_(cf, '220p', L + g(1) + 3.81, rows[1], 90, 'HF roll-off (7 kHz)'); W((L, rows[1]), P(cf, '1')); W(P(cf, '2'), (rx, rows[1]))
    s.part(da, 'Device', 'LED', 'red LED', L + g(1) + 3.81, rows[2], 0, desc='Clipping LED', text='t')
    s.part(db, 'Device', 'LED', 'red LED', L + g(1) + 3.81, rows[3], 180, desc='Clipping LED', text='b')
    W((L, rows[2]), P(da, '1')); W(P(da, '2'), (rx, rows[2]))
    W((L, rows[3]), P(db, '2')); W(P(db, '1'), (rx, rows[3]))
    W((rx, ou[1]), (rx + g(4), ou[1])); lab(out_lab, (rx + g(4), ou[1]))

def level(ref, name, x, y, in_lab, out_lab):
    lab(in_lab, (x - g(3), y - 3.81), 'l'); W((x - g(3), y - 3.81), (x, y - 3.81))
    s.part(ref, 'Device', 'R_Potentiometer', 'A10k', x, y, 0, mirror='x', desc=f'{name} level', extra={'Panel': name},
           text=((x - g(4), y + g(2)), (x - g(4), y + g(3.5)), 'right'))
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
s.box('INPUT / DRIVE (U1A): gain 1 + 470k / (2k2 + DRIVE) = x1.9 to x215', g(42), g(6), g(108), g(62))
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
R_('R5', '470k', (NX + rx) / 2, mi[1] + g(4), 90, 'DRIVE feedback'); W((NX, mi[1] + g(4)), P('R5', '1')); W(P('R5', '2'), (rx, mi[1] + g(4)))
C_('C7', '10p', (NX + rx) / 2, mi[1] + g(7), 90, 'HF limit'); W((NX, mi[1] + g(7)), P('C7', '1')); W(P('C7', '2'), (rx, mi[1] + g(7)))
W(ou, (rx, ou[1])); W((rx, ou[1]), (rx, mi[1] + g(7)))
GX = NX - g(5)
W((NX, mi[1]), (GX, mi[1]))
R_('R6', '2k2', GX, mi[1] + g(1) + 3.81, 0, 'Max-gain limit'); W((GX, mi[1]), P('R6', '1'))
CPv('C8', '4u7', GX, P('R6', '2')[1] + g(1) + 3.81, d='DC block in the gain leg (variant: 5u)'); W(P('R6', '2'), P('C8', '1'))
top = P('C8', '2')[1] + g(1)
W(P('C8', '2'), (GX, top))
s.part('RV1', 'Device', 'R_Potentiometer', 'B500k', GX, top + 3.81, 0, mirror='x', desc='DRIVE (variant: ATTACK 500k)', extra={'Panel': 'DRIVE'},
       text=((GX - g(5), top + g(1)), (GX - g(5), top + g(2.5)), 'right'))
W((GX, top), P('RV1', '3'))
w2 = P('RV1', '2'); p1 = P('RV1', '1')
W(w2, (w2[0] + g(1), w2[1]), (w2[0] + g(1), p1[1] + g(1)), (p1[0], p1[1] + g(1)))
W(p1, (p1[0], p1[1] + g(2))); lab('VB', (p1[0], p1[1] + g(2)), 'l')
W((rx, ou[1]), (rx + g(4), ou[1])); lab('PRE', (rx + g(4), ou[1]))

# ================================================================ BANDS
s.box('BANDS: inverting MFB filters (U1B-D) -> clippers (U2A-C) -> level', g(112), g(6), g(262), g(150))
bands = (
    ('LOW', 2, g(24), {'in': ('R', 'R7', '15k'), 'am': ('R', 'R8', '15k'), 'mo': ('C', 'C9', '22n'), 'ao': ('R', 'R9', '15k'),
                        'avb': ('C', 'C10', '100n')}, 'LOW: MFB low-pass, fc ~225 Hz, Q 0.71, gain -1',
     ('R10', 'R11', 'C11', 'D2', 'D3'), 'RV2'),
    ('MID', 3, g(70), {'in': ('R', 'R12', '10k'), 'am': ('C', 'C12', '10n'), 'mo': ('R', 'R13', '47k'), 'ao': ('C', 'C13', '10n')},
     'MID: MFB band-pass, f0 ~735 Hz, Q ~1.1, gain -2.35', ('R14', 'R15', 'C14', 'D4', 'D5'), 'RV3'),
    ('HIGH', 4, g(116), {'in': ('C', 'C15', '10n'), 'am': ('C', 'C16', '10n'), 'mo': ('R', 'R16', '15k'), 'ao': ('C', 'C17', '10n'),
                          'avb': ('R', 'R17', '3k3')}, 'HIGH: MFB high-pass, fc ~2.26 kHz, Q 0.71, gain -1',
     ('R18', 'R19', 'C18', 'D6', 'D7'), 'RV4'),
)
for name, unit, yb, el, title, cl, pot in bands:
    mfb('U1', unit, g(150), yb, el, 'PRE', name + '_F', title)
    clipper('U2', unit - 1, g(196), yb, *cl, name + '_F', name + '_C')
    level(pot, name, g(240), yb + g(6), name + '_C', name + '_L')

# ================================================================ MIXER + OUTPUT
s.box('MIXER (U2D): inverting sum, 10k in / 2k2 fb (x0.22 per band), then VOLUME', g(266), g(6), g(326), g(80))
pl, mi, ou = OP('U2', 4, g(292), g(30))
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
s.part('RV5', 'Device', 'R_Potentiometer', 'A100k', rx + g(9), ou[1] + 3.81, 0, mirror='x', desc='VOLUME', extra={'Panel': 'VOLUME'},
       text=((rx + g(11), ou[1] + g(3)), (rx + g(11), ou[1] + g(4.5)), 'left'))
GND(P('RV5', '1'))
w = P('RV5', '2'); W(w, (w[0] + g(4), w[1])); lab('OUT', (w[0] + g(4), w[1]))
s.text('Each band clips at about +-1.8 V (red LEDs); the mixer scales the sum back before VOLUME.', g(268), g(70))

s.write(OUT, title_block={'title': 'Tri-Fuzz (multiband, 9 V)', 'rev': '0.1', 'company': 'Super-Freq',
                         'comments': ['After Craig Anderton Quadrafuzz and a 3-band variant', 'LOW / MID / HIGH bands spread for guitar; breadboard first']})
print('written', OUT)
