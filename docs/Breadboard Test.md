# Tri-Fuzz: breadboard test plan

**Status: READY FOR BREADBOARD (schematic v0.3 + PRE change, 2026-10-09).** Listen to the simulated clips first (`docs/sim-audio/`); they cover the questions below in a rough way. The breadboard decides them for real before the PCB.

Gear: multimeter, scope, audio probe, amp. 9 V supply through 100 Ω (each 1 mA = 0.1 V) for the first power-up.

## What to build

The full signal path is big (2× TL074, ~90 parts). Build it in stages, each checked before the next:

1. **Power + VB + U1A input/PRE.**
   - Check VB ≈ 4.5 V and U1A output ≈ 4.5 V DC.
   - With a 200 mVpp 200 Hz sine in, the output should be ×1.1 to ×3.1 over the PRE trim, and clean on the scope.
2. **The three filters (U1B–D).** Sweep a clean sine (signal generator or a phone tone app) and read each output on the scope:
   - **LOW:** flat below ~225 Hz, −3 dB near 225 Hz, falling 12 dB/octave above. The trim should move the corner over ~180–400 Hz.
   - **MID:** a peak near 735 Hz (gain ≈ 1), trim range ~590–1180 Hz.
   - **HIGH:** −3 dB near 2.26 kHz, flat above. Trim range ~1.65–3.75 kHz.
3. **One clipper (start with MID, the non-inverting one)** with its DRIVE pot and the CLIP toggle, or jumpers for the toggle.
   - Check the output DC stays at VB in every CLIP position.
   - Check the clip levels: ±1.3 V (sym), rails, +1.3 / −0.65 V (asym).
4. **The other two clippers, the post-clip filters, the VOLUME pots and the mixer.**

## What to decide (listen through the amp)

| # | Question | How to test | Decide |
|---|---|---|---|
| 1 | Is multiband worth it? | Chords (open and barre, power chords) at high DRIVE; compare with one clipper fed full-range (bypass the filters into U2B) | Go / no-go for the PCB |
| 2 | MID polarity | Swap U2B back to inverting (C21 + R14 into −, + to VB) and compare | Keep inverted, or offer both (spare footswitch?) |
| 3 | LOW clip: LEDs vs Si / Schottky | Swap D2/D3 | Part on the PCB |
| 4 | Asymmetric positions: worth a switch position? | Toggle down vs up on each band | Keep, or bake in |
| 5 | Centre "rails" position: useful or just harsh? | Toggle centre | Keep, or change to clean (no clip) |
| 6 | Crossover defaults | Sweep each trim, note where it sounds best | Fixed values / trim centre |
| 7 | Post-clip low-pass values (1.5 k / 7 k / 10 k) | Swap C27 / C28 / C29 up and down one value | Cap values |
| 8 | Noise at full DRIVE (simulation can't show this) | All DRIVE max, guitar volume off, listen; then HIGH DRIVE alone | HIGH max DRIVE (A250k?), op-amp choice |
| 9a | HIGH band level (sim: ~12 dB under LOW) | HIGH solo vs LOW solo with a real guitar | R22 10k → 3k3, or HIGH sym → 2× Si |
| 9 | Level balance between CLIP positions | Note how far each band's VOLUME moves to match | Fine as is, or pad the rails position |

## Record

| Stage / question | Result | Notes |
|---|---|---|
| 1 PRE | | |
| 2 LOW / MID / HIGH filter corners | | |
| 3 MID clipper levels | | |
| 4 Full path | | |
| Decisions 1–9 | | |
