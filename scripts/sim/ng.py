"""Minimal libngspice driver: run(netlist_lines, commands) -> captured stdout lines."""
import ctypes as C
LIB = '/Applications/KiCad/KiCad.app/Contents/Frameworks/libngspice.0.dylib'
ng = C.CDLL(LIB)
OUT = []
PF = C.CFUNCTYPE(C.c_int, C.c_char_p, C.c_int, C.c_void_p)
_pf = PF(lambda s, i, u: (OUT.append(s.decode(errors='replace')), 0)[1])
_sf = PF(lambda s, i, u: 0)
EX = C.CFUNCTYPE(C.c_int, C.c_int, C.c_bool, C.c_bool, C.c_int, C.c_void_p); _ex = EX(lambda *a: 0)
ng.ngSpice_Init(_pf, _sf, _ex, None, None, None, None)
def run(net, cmds):
    del OUT[:]
    arr = (C.c_char_p * (len(net) + 1))(*[l.encode() for l in net], None)
    ng.ngSpice_Circ(arr)
    for c in cmds: ng.ngSpice_Command(c.encode())
    ng.ngSpice_Command(b'remcirc')
    return list(OUT)
