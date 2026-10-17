# Tri-Fuzz: design notes

## Signal path

1. **U1A input / DRIVE:** non-inverting, gain 1 + 470k / (2k2 + DRIVE).
   - That's ×215 at DRIVE minimum resistance, down to ×1.9 at 500k. It's the variant's "ATTACK".
   - The 4u7 in the gain leg keeps the DC gain at 1.
2. **Three inverting multiple-feedback (MFB) filters.** All the bands share one polarity at the mixer. **Correction (2026-10-09):** that *causes* cancellation notches at the crossovers rather than avoiding them; invert the MID band (see "Crossover phase" below):

| Band | Op-amp | Filter | Values | fc / f0 | Q | Gain |
|---|---|---|---|---|---|---|
| LOW | U1B | MFB low-pass | R7 = R8 = R9 = 15k, C10 100n (A→VB), C9 22n (fb) | **≈ 225 Hz** | 0.71 | −1 |
| MID | U1C | MFB band-pass | R12 10k in, R13 47k fb, C12 = C13 = 10n | **≈ 735 Hz** | ≈ 1.1 | −2.35 |
| HIGH | U1D | MFB high-pass | C15 = C16 = C17 = 10n, R17 3k3 (A→VB), R16 15k (fb) | **≈ 2.26 kHz** | 0.71 | −1 |

3. **Clippers** U2A–C (as the variant): 3k3 in, 100k ∥ 220p ∥ red LED pair in the feedback. ×30 into the LEDs, so each band clips at about ±1.8 V.
4. **LOW / MID / HIGH level** (A10k, returned to VB), into the **U2D inverting mixer**: 10k per band, 2k2 feedback (×0.22, as the variant). Then C19 and VOLUME (A100k).

**Formulas (equal R or equal C):**
- MFB low-pass: fc = 1 / (2π R √(C1 C2)), Q = √(C1/C2) / 3.
- MFB band-pass: f0 = 1 / (2π C √(R1 R2)), Q = ½ √(R2/R1), gain = R2 / 2R1.
- MFB high-pass: fc = 1 / (2π C √(R1 R2)), Q = √(R2/R1) / 3.

## Changes from the variant

| Variant | Here | Why |
|---|---|---|
| Three band-passes at 220 / 335 / 500 Hz | Low-pass 225 Hz, band-pass 735 Hz, high-pass 2.26 kHz | Cover the whole guitar range (Anderton-style) |
| Bipolar supply, + inputs to ground | 9 V single supply, VB 10k/10k + 100µ | Pedal power |
| 220k input bias, 10k + 10p RF filter | 1M bias, 1M pull-down, 100n coupling | Standard pedal input; the 10p was dropped along with the 10k |
| 5µ caps + 5k pots to ground | A10k level pots returned to VB, no caps | The DC path through the mixer resistors would have shifted the mixer's output |
| Two TL074 (8 sections), same as the variant's count | | |

**The panel fits the 125B five-knob grid** (Hyper Fuzz / Rat Energizer): DRIVE, LOW, MID, HIGH, VOLUME.

## On the breadboard

**DC:** VB 4.5 V; every op-amp output at about 4.5 V.

**Sweep each band** with a generator at DRIVE minimum: scope LOW_F, MID_F and HIGH_F from 50 Hz to 10 kHz. Check the corners, and that the bands overlap without deep gaps.

**Listen for:**
- Chords at high DRIVE compared with a normal fuzz: clearer?
- Each band solo (the other two levels down).
- LOW: thick but not muddy. HIGH: fizz or bite?
- MID: the "voice".

**Values to try:**
- **MID f0:** R12/R13 (10k/47k) or C12/C13. 10n → 15n moves it to about 490 Hz.
- **HIGH corner:** C15–C17 10n → 6n8 gives about 3.3 kHz.
- **Clip:** red LEDs → 1N4148 pairs (tighter, quieter, more "fuzz").
- **Mixer gain:** R23 2k2 → 4k7 for more output.
- **DRIVE taper:** a B500k rheostat crowds most of the gain change into the low-resistance end. Try a C (reverse log) pot or a 47k–100k series resistor.

## Later

- **Add a fourth band**, like Anderton's original: split MID into low-mid and high-mid. It needs a third op-amp package.
- **Per-band clip select** (LED / Si), or a bypassable band.
- **Board:** 125B, SMD, on the Hyper Fuzz grid.

## Filter choice: low-pass / band-pass / high-pass vs three band-passes (2026-10-07)

**This design** uses a low-pass for LOW, a band-pass for MID and a high-pass for HIGH, so every frequency lands in some band (full range).
- **The variant** used three band-passes packed between 220 and 500 Hz, so everything outside them was cut, including most of the attack and presence.
- **Anderton's original Quadrafuzz** (from memory, to check against the schematic): low-pass, two band-passes, high-pass.

**Watch-outs for the breadboard:**
1. **The LOW band reaches down to sub-bass.** The low-pass passes everything under 225 Hz, so rumble and the low E's thump get distorted too, which can sound flabby. If it does, add a gentle high-pass to the LOW band at about **60–80 Hz**: a series cap ahead of R7, or one RC.
2. **The MID band overlaps its neighbours.** With Q ≈ 1.1 the skirts fall only 6 dB per octave, so mid frequencies are distorted in two bands at once. That's smoother, but chords separate less. Try a **higher MID Q (1.5–2)** for clearer separation and a more "voiced" mid. On the band-pass: Q = ½ √(R13 / R12), so 10k / 100k gives Q 1.6 (re-check f0 and the gain).
3. **Crossover phase:** see the section "Crossover phase (2026-10-09)" below. The dips are much deeper than first estimated.

**Creative option: the "vowel" fuzz.** Narrow band-passes with no low or high extremes (like the variant) give a vocal, nasal, formant-like fuzz, close to a fixed wah or a talk-box. Two ways to use it:
- **A toggle** that swaps the LOW and HIGH filters for band-passes (full-range ↔ vowel).
- **A separate pedal** with three or four narrow band-passes (Q 3–5) at vowel formant frequencies, with tunable centres. It might suit the "Haunting Mids" name family.

## Crossover phase (2026-10-09)

Prompted by the VFE Triumvirate question: does the phase difference between bands matter?

**How far apart the bands are.** Where two neighbouring bands overlap, they arrive at the mixer nearly **opposite in phase**:
- A 2nd-order low-pass lags toward −180° above its cutoff.
- A 2nd-order high-pass leads toward +180° below its cutoff.
- A band-pass sits between them: +90° below centre, −90° above.

| Frequency | LOW | MID | HIGH |
|---|---|---|---|
| 400 Hz (LOW/MID overlap) | −131° | +54° (185° from LOW) | |
| 1.3 kHz (MID/HIGH overlap) | | −52° | +130° (182° from MID) |

**Clean sum** (each band normalised to 0 dB; the response with gain set low or the note decaying):

| Hz | 150 | 200 | 300 | 400 | 735 | 1.1k | 1.6k | 2.26k | 3.5k |
|---|---|---|---|---|---|---|---|---|---|
| As drawn (all same polarity) | −2 | −5 | **−22** | −11 | −2 | −6 | **−34** | −8 | −2 |
| **MID inverted** | +0.6 | +0.3 | −0.8 | −1.0 | +1.4 | 0 | −0.6 | +0.1 | +0.6 |

This is the same rule as loudspeaker crossovers: with 2nd-order filters, flip one band's polarity, or the crossovers notch.

**Does it matter once the bands are clipping?**
- **Less than clean, but yes.** Clipping turns each band into its own near-square wave, so the sum isn't trying to rebuild the input.
- **But a note near a crossover** (roughly 250–450 Hz or 1.2–2 kHz: much of the guitar's middle register) appears in both bands at once, about 180° apart. Their fundamentals partly cancel, so those notes come out **thinner and quieter**, with mostly harmonics left.
- **As a note decays below the clipping level,** the bands stop squaring off, the cancellation returns, and **the note hollows out or drops faster** than notes elsewhere on the neck.
- **The level knobs can't fix it:** cancellation needs a polarity change, not a level change. Turning one band down only moves where the null falls.

**Fix:** flip the MID band. Two options:
1. **Make the MID clipper non-inverting.** Signal into U2B's + input, 3k3 from − to VB, keep 100k ∥ 220p ∥ LEDs in the feedback. Gain is 31 instead of −30, so the clip is the same, but with a gentler knee near zero; the Triumvirate's mid stage works this way.
2. **MID PHASE switch (SPDT), as an option to try.** In-phase gives a scooped "notched" voice; inverted gives full range. That's cheap, and could be a real control.

On the breadboard, sweep a clean sine with DRIVE at minimum and listen or scope for the two notches, then flip MID and compare. Then compare by ear at full DRIVE: chords, and single notes on the G and B strings around the 5th–12th frets.

## Reference: VFE Triumvirate (Peter Rutter; madbean doc, 2016)

`~/Documents/Guitar/Effects/Schematics/VFE_Triumvirate.pdf`. 1590B, ±9 V from a charge pump, 2× TLE2074 (TL074 reported comparable).

- **Input:** 1k / 0.22µ / 2M2, then a non-inverting PRE stage (1k + 10k trim: gain 1–11) feeding all three bands.
- **Filters:** passive, 2nd order, all trimmable (8 trimpots):
  - **Bass:** RC-RC low-pass (5k / 0.22µ, 50k / 22n), stock ~290 Hz.
  - **Mid:** CR-CR high-pass (0.22µ / 5k, 22n / 50k) → buffer → RC-RC low-pass (2k / 0.1µ, 20k / 10n); ~290 Hz–1.6 kHz.
  - **Treble:** CR-CR high-pass (47n / 5k, 4n7 / 50k), ~1.35 kHz.
  - The trimmers have no end-stop resistors: turned fully CCW, a high-pass shorts the band.
- **One gain stage per band:** non-inverting, 1k to ground + A500k GAIN (×1 to ×500), 100p across, **a different clipper in each band:**
  - **Treble:** two 1N4148 in series each way (±1.2 V).
  - **Mid:** red LEDs (±1.8 V); they visibly flash, even with MID volume down.
  - **Bass:** two BS170s used as diodes (body diodes / channels; ~±0.7 V).
  - Bass ground leg: 1k + 10µ (late-version fix: DC gain 1, to stop TLE2074 offset × 500 shifting the bass band).
- **Outputs:** each band through an A100k volume and a buffer (1n on the treble buffer). Then a mixer with a CUT trimmer (a treble cut on the mix; the mixer is off the scanned page).
- **Phase:** all non-inverting, so it has the same crossover notches (calculated: −17 dB at ~290 Hz, −12 dB at ~1.4 kHz clean). Inverting the mid flattens it to within 1 dB.

**Ideas to borrow for Tri-Fuzz:**
1. **Invert the MID band** (above).
2. **Different clipper per band:** Si pair for HIGH (tighter, less fizz), LEDs for MID, low-Vf (Schottky or MOSFET body diode) for LOW. That gives tight bass with a loud, open mid.
3. **Per-band GAIN** (each clipper's feedback as A500k + 1k) instead of the global DRIVE.
   - Too many knobs for a 1590B. A compromise: global DRIVE plus internal trims per band, or **two GAIN knobs** (LOW and HIGH) with MID fixed.
4. **Trim-adjustable crossovers** with **end-stop resistors**: the doc notes Triumvirate's high-passes short the band at full CCW.
5. **CUT** on the mix (a low-pass on the mixer feedback): a simple treble trim for the fizz that multiband fuzz produces.
6. **Gain-leg capacitor** in every high-gain stage (we already use 4u7 on U1A; add one per clipper if the gain goes up).
7. **"Boost mode"** (remove the clippers) = a 3-band EQ / exciter. A **CLIP/CLEAN toggle** per band, or one global toggle, would make Tri-Fuzz double as a multiband boost.

## v0.2: per-band controls, MID inverted (2026-10-09)

**What changed from v0.1:**

| Block | v0.1 | v0.2 |
|---|---|---|
| U1A input | DRIVE pot B500k: ×1.9 to ×215 | **PRE trim** 50k (3362P, internal), R5 470k → **22k**, C7 → 47p: ×1.4 to ×11. Sets how hard all the bands are hit. |
| Clippers U2A–C | 3k3 in, 100k fixed, LEDs always in | Feedback **10k + DRIVE A500k** (rheostat) ∥ Cf. Gain ×3 to ×155 (LOW/HIGH, inverting), ×4 to ×156 (MID, non-inverting). |
| Clipping | red LED pair only | **CLIP toggle per band (ON-OFF-ON):** red LED pair / centre = none (op-amp clips at its rails) / 1N4148W pair |
| MID polarity | inverting (same as LOW/HIGH) | **non-inverting:** MID_F into U2B +, gain leg R14 3k3 + C21 2u2 to VB. Flips MID against its neighbours, so the crossovers sum flat. |
| DC blocking | none on the clippers | C20 4u7 (LOW), C22 1u (HIGH) in series with the 3k3 inputs; C21 2u2 in the MID gain leg. At ×155, op-amp offsets would otherwise push the clipping off-centre. |
| Cf | 220p on all (7 kHz at 100k) | LOW 220p, MID 47p, HIGH 22p. The roll-off moves with DRIVE: at 510k, 1.4 / 6.6 / 14 kHz. |
| Output | VOLUME pot A100k | **OUTPUT trim** 100k (internal) |
| Mixer | 2k2 | + **CUT toggle** SW4: 22n across R23, about 3.3 kHz |

**Refs added:**
- C20–C23;
- RV6–RV8 (DRIVE LOW/MID/HIGH);
- D8–D13 (1N4148W);
- SW1–SW3 (CLIP), SW4 (CUT).

RV2–RV4 are now the band VOLUME pots. RV1 and RV5 are trimmers.

**CLIP positions and levels:**

| Position | Clips at | Character | Relative level |
|---|---|---|---|
| LED | ±1.8 V | open, loud, a bit of compression | reference |
| centre (none) | op-amp rails, ~±3 V (TL074 on 9 V; output can't get within ~1.5 V of the rails) | harsh, square, the loudest | about +4 dB |
| Si | ±0.65 V | tight, compressed, the quietest | about −9 dB |

The band VOLUME pots take up the level differences. At low DRIVE with CLIP in the centre, the band is just a clean, filtered boost: a 3-band EQ mode, as in the Triumvirate's "boost mod".

**Notes:**
- **MID gain law:** non-inverting gives 1 + Rf/R14, so the minimum is ×4 instead of ×3. That's close enough that the DRIVE knobs feel the same.
- **MID clipping knee:** with the diodes in the feedback of a non-inverting stage, the output is the input plus the diode drop. The clip knee is a little softer than in the inverting bands (the "Tube Screamer" shape), which suits mids.
- **Suggested per-band diode variants** to try on the breadboard, from the Triumvirate:
  - LOW: Schottky or MOSFET body diodes, for a tighter low end.
  - HIGH: two 1N4148 in series each way, for less fizz.
  - It's easy to swap one pair per band later.
- **Terrarium layout:** 125B, 6 pots (3 × 2), 4 mini toggles in a row, 2 footswitches.
  - We'd copy the hole positions from a Terrarium drill template when doing the PCB.
  - Footswitch 2 is spare. Ideas: a **band solo/mute** (e.g. mute LOW for tight rhythm), or an **ALT** that flips MID polarity back to get the "notched" voice.
- **Op-amp count:** still 2× TL074 (8 sections, all used). Anything more (a polarity switch on its own stage, a band mute buffer) needs a third op-amp. A TL072 fits.

## v0.3: clip types per band, trimmable crossovers, even-order option (2026-10-09)

**Controls are capped at 6 knobs + 3 toggles,** one column per band, so CUT is gone. The post-clip low-passes below do its job, per band.

**CLIP toggle per band:** up = symmetric / centre = op-amp rails / down = asymmetric (even-order).

| Band | Symmetric | Asymmetric (+ / −) | Why |
|---|---|---|---|
| LOW | red LED pair, ±1.8 V | LED / 1N4148: +1.8 / −0.65 V | Highest threshold: the most clean headroom for bass at a given DRIVE |
| MID | 2× 1N4148 each way, ±1.3 V | 2× Si / 1× Si: +1.3 / −0.65 V | The Triumvirate's treble type; between LOW and HIGH |
| HIGH | 1N4148 pair, ±0.65 V | 2× Si / 1× Si: +1.3 / −0.65 V | Lowest threshold: compresses the top and keeps it even. Use less HIGH DRIVE for less fizz |

- **Even-order alignment:** every asymmetric network puts the bigger drop on the **positive** side of its clipper output, so all three bands make even-order harmonics (and DC shift) of the same sign. See "Even order and band polarity" below.
- **Op-amp rails (centre):** about ±3 V, the hardest and loudest.

**Crossover trims** (3362P, one per band, in series with a fixed end-stop resistor so a trim at 0 can't short the band):

| Band | Trimmed part | Range | Q over the range | Nominal |
|---|---|---|---|---|
| LOW | RV9 20k + R8 4k7 (A→− of the MFB LP) | ~400 Hz → ~180 Hz | 0.74 → 0.66 | 225 Hz at ~10k |
| MID | RV10 50k + R24 4k7 shunt to VB (MFB BP; R12 now 22k, gain −1.07) | ~1.18 kHz → ~590 Hz | 1.7 → 0.9 (constant bandwidth) | 735 Hz at ~13k |
| HIGH | RV11 5k + R17 1k2 (A→VB of the MFB HP) | ~3.75 kHz → ~1.65 kHz | 1.2 → 0.5 | 2.26 kHz at ~2k |

Gain stays put in every band (one resistor tunes each filter).

**The polarity trick depends on the trims.** It only gives a flat sum when neighbours share a crossover. Spread the trims apart and you get a gap (a dip); overlap them and you get a bump. That's fine for voicing; set them by ear.

**After each clipper:**
- **1µ DC block:** asymmetric clipping shifts the band's average with playing level.
- **4k7 + C to VB:** a post-clip low-pass (LOW 33n ≈ 1.5 kHz, MID 6n8 ≈ 7 kHz, HIGH 4n7 ≈ 10 kHz), then the band VOLUME.
  - Clipping makes harmonics far above the band. Without these filters, a clipped LOW band sprays fizz across the mids and highs.
  - With them, each band's distortion stays mostly in its own region, which is the point of multiband.

### Q&A (2026-10-09)

**Would all-pass filters to line up the phase help?**

Not here.
- With MID inverted, the three bands already sum to a flat magnitude. That sum is itself an all-pass, meaning the bands agree at the crossovers, which is all that alignment buys.
- The remaining phase rotation is shared by the whole signal, and its group delay (under ~1 ms even in the LOW band) is inaudible as timing.
- Once the bands clip, the new harmonics are created *after* the filters, so pre-filter phase matters only through the polarity rule.
- All-pass stages also need op-amps we don't have (both TL074s are full).

All-pass alignment matters for higher-order or mixed-order crossovers (e.g. a 4th-order low band against 2nd-order neighbours). We aren't using those.

**LEDs on the bass, for more clean bass?** Yes, with one nuance.
- The threshold works relative to DRIVE: LEDs let the LOW band swing to ±1.8 V before clipping, so at a given DRIVE more of the bass stays clean and punchy, and LOW is louder.
- Why clean(er) bass is good:
  1. Clipped bass makes strong harmonics that land in the mid range: mud. The post-clip low-pass helps too.
  2. Two bass notes clipping together intermodulate into low, dissonant difference tones. That's the classic power-chord mush.
  3. The bass carries the punch, and clipping flattens its transient.
- The Triumvirate went the other way (low-threshold MOSFET diodes) for a tight, square, compressed bass. The LOW CLIP "rails" position covers that hard sound when you want it.

**Even-order harmonics:** yes, as an option per band (the CLIP "down" position) rather than baked in everywhere.
- Asymmetric clipping makes even harmonics. The 2nd harmonic is an octave, so it thickens and warms the sound without adding dissonance.
- **LOW and MID benefit most.** In HIGH, the 2nd harmonics of treble land at 4–10 kHz, which reads as fizz. That's why HIGH's symmetric pair is the default suggestion, with its post-clip low-pass at ~10 kHz.
- Asymmetric clipping also shifts the DC level with playing dynamics, a "bloom" on the attack. The 1µ caps after the clippers turn that into a short transient rather than a level shift.
- To make it fully baked in: replace each band's symmetric pair with its asymmetric one, and use the switch for asymmetric / rails / clean (centre = no clip, low DRIVE).

**Even order and band polarity.**
- Split a clipper's output into an odd part and an even part. **Flipping the input's polarity flips the odd part (fundamental, 3rd, 5th…) but not the even part.** In symbols: if f(x) = odd(x) + even(x), then f(−x) = −odd(x) + even(x).
- So inverting MID changes how the bands' fundamentals and odd harmonics add at the crossovers (that's what we wanted), but it doesn't flip MID's even harmonics.
- **The sign of each band's even-order products is set by which way its asymmetric diodes face**, independent of the band's polarity.
- So there are two independent choices:
  1. **Band polarity:** sets how the fundamentals/odd harmonics sum at the crossovers (MID inverted = flat).
  2. **Diode orientation:** sets whether the even harmonics of different bands reinforce or cancel where they overlap. For example, LOW's 2nd harmonic of a 200 Hz note lands at 400 Hz, inside MID.
- **v0.3 orients all three the same way** (bigger drop on the + side at each clipper output), so even harmonics reinforce and the attack bloom adds up across bands.
- **Experiment:** reverse one band's asymmetric pair (e.g. MID) and listen: the even content in the overlap regions partly cancels. It's thinner but cleaner, and is a possible variant.

## Before the PCB: open questions and decisions (2026-10-09)

**Status:** the schematic is complete (ERC 0), but no part of it has been heard. The items below would change parts or values on the board.

### Settle by listening (breadboard, or a simulation first)

1. **Does the multiband sound justify the parts count?** The core test: chords at full DRIVE, Tri-Fuzz vs a single-band fuzz.
2. **MID polarity by ear.** Inverted (flat sum) vs as before (notched). If notched sounds better, that's a free voicing change.
3. **Clip choices per band:**
   - LOW LEDs vs Schottky/MOSFET;
   - MID 2× Si vs LED;
   - whether the asymmetric positions are worth having, or should be baked in;
   - whether the centre "rails" position is useful or just harsh. A clean (no-clip) centre is the alternative.
4. **Crossover nominal values.** The trims cover the range, but the fixed defaults set where most people will leave them.
5. **Post-clip low-pass values** (1.5 kHz / 7 kHz / 10 kHz): too dark, or not enough?
6. **Noise at full DRIVE.** PRE ×11 × clipper ×155 ≈ ×1700 of TL074 hiss, worst in HIGH. The Triumvirate doc reports treble whine at max settings. That might mean a lower max DRIVE in HIGH (e.g. A250k), more HIGH post-filtering, or a quieter op-amp.

### Design decisions I'd make now (on paper)

7. **PRE stage headroom: DONE 2026-10-09** (R5 4k7, C7 220p: ×1.1 to ×3.1). At ×11, a hot pickup (~1 V peak) clips U1A at its rails *before* the bands split, which defeats the multiband idea (intermodulation comes back). Proposal: PRE ×1 to ×3 (R5 22k → 4k7 with the same 2k2 + 50k trim leg). The per-band DRIVE has plenty of gain.
8. **9 V vs 18 V (charge pump).**
   - At 9 V the TL074 swings about ±3 V, which is fine for diode clipping (±0.65 to ±1.8 V), and the rails position is the only one that uses the full swing.
   - Proposal: stay at 9 V. Simpler, and no pump whine near a high-gain HIGH band.
9. **Op-amps.**
   - TL074 is a JLC *extended* part (fee), and it's hissy.
   - Options:
     - 4× TL072 (basic, C6961), more board area;
     - 2× TL074 (one fee);
     - a quieter quad (e.g. OPA4134/OPA1679, extended).
   - Proposal: TL072 ×4 if it fits the 125B board, else TL074. Revisit if noise is a problem (item 6).
10. **Clip LED and diode parts.** 0805 red LEDs (C84256, used on Haunting Mids) and 1N4148W, all SMD at JLC; no hand-soldering.

### Mechanical decisions (needed before layout)

11. **Panel:** 125B with 6 pots in 2 rows of 3, 3 toggles, 1 footswitch.
    - **Pots:** 16 mm Alpha (our usual, board-mounted on the back) or 9 mm? Six 16 mm pots fit a 125B comfortably.
    - **Hole positions:** copy them from a Terrarium drill template (do you have one?), or lay out our own grid.
12. **Toggles:** Taiway 100 ON-OFF-ON on the board (as UF1 v1.2) vs panel-mounted and wired. On the board is simpler and needs the PCB to sit at the right height.
13. **Bypass:** the SwitchPCB 3PDT board + a 1×4 ribbon header (IN / LED / GND / OUT), as on UF1 / Flatline / Haunting Mids.
14. **Jacks and DC:** top-mounted in the 125B (IN, OUT, DC), wired.
15. **Trimmer access:** five 3362Ps (PRE, OUTPUT, 3 crossover). Put them where a screwdriver can reach with the board boxed, e.g. between the pot rows on the component side, or through access holes.
16. **Name:** "Tri-Fuzz" is a working name.

## Simulated audio (2026-10-09)

`docs/sim-audio/index.html` lists the clips. Open it in a browser from Finder.
- **Scripts:** `scripts/sim/`: `render.py <clip>|all`, `trifuzz_net.py` (netlist mirroring the schematic), `guitar.py` (synthetic DI), `ng.py`.
- **Model:** ngspice through KiCad's libngspice, with a behavioural TL07x-like op-amp (gain 1e5, GBW 3 MHz, output limited 1.5 V inside the rails) and 1N4148 / red LED models.
- **Input:** a Karplus-Strong low E, then an open E chord, peaks 150 / 250 mV.
- **Output:** clips are loudness-matched. `levels.txt` has the raw levels.
- **Gotcha learned:** in SPICE, `1M` is 1 milliohm. Write `1meg`.

**Raw output levels** (relative to 02, all bands symmetric at 3 o'clock):

| Clip | Level |
|---|---|
| Single full-range LED fuzz | −3.2 dB |
| MID **not** inverted | **−3.5 dB**: the crossover cancellation survives heavy clipping |
| Asymmetric | −2.2 dB |
| Rails | +3.4 dB |
| Clean bass (LOW DRIVE min) | −5.1 dB |
| Max DRIVE | +1.5 dB |
| LOW solo | −3.1 dB |
| MID solo | −7.0 dB |
| HIGH solo | **−15.3 dB** |
| Clean DI | −11 dB (so Tri-Fuzz at VOL 70 % is ~11 dB above the clean guitar; the OUTPUT trim has room) |

### Takeaways from the audio simulation (2026-10-09)

Measurements on the clips' chord section (`scripts/sim/analyse.py` band energies, `scripts/sim/imd.py` intermodulation). Clip 01 was re-rendered with neutral filtering (47p, ~10 kHz post-filter) so it's a fair single-band reference.

**Intermodulation in the chord** (energy *between* the six strings' harmonics ÷ energy *on* them, 40 Hz–5 kHz; lower = cleaner):

| Clip | Ratio | Read as |
|---|---|---|
| Clean DI (input) | −13.0 dB | The measurement floor (synthetic strings, window leakage) |
| Single full-range LED fuzz | **−10.6 dB** | Adds ~2.4 dB of intermodulation over the clean input |
| **Tri-Fuzz, symmetric** | **−13.2 dB** | At the floor: no measurable added intermodulation |
| Tri-Fuzz, MID not inverted | −12.8 dB | |
| Tri-Fuzz, asymmetric | −10.6 dB | Even-order clipping brings intermodulation back, as much as the single fuzz |
| Tri-Fuzz, rails | −12.4 dB | |
| Tri-Fuzz, max DRIVE | −11.7 dB | |
| Tri-Fuzz, DRIVE noon | −13.0 dB | |

**What we learned:**
1. **The multiband idea works on paper.** With symmetric clipping, Tri-Fuzz chords carry no measurable extra intermodulation, while one fuzz at the same drive does. That's the clarity the design is for. The ear still has the final say (breadboard question 1).
2. **Keep MID inverted.** Without it, the output is 3.5 dB quieter and the chord loses ~3 dB in 400 Hz–2 kHz: a mid hole, even while clipping hard.
3. **Asymmetric (even-order) clipping trades clarity for warmth.** It adds intermodulation back (difference tones, the attack "bloom"), plus ~3 dB more 2–5 kHz. Keep it as a switch position, not baked in. It's a character option, not the default.
4. **Tonal balance is similar to an ordinary fuzz** once the single fuzz has the same treble filtering (the band energies agree within ~1 dB). The difference is clarity, not EQ.
5. **The HIGH band is weak:** solo ~15 dB under the full mix, ~12 dB under LOW.
   - Part of that is the synthetic guitar, which is dark above 2 kHz.
   - Part is the gain structure: ±0.65 V Si clip → VOLUME → mixer ×0.22.
   - Fix candidates for the breadboard: R22 10k → 3k3, or HIGH symmetric → 2× Si.
6. **DRIVE changes each band's level a lot.**
   - At minimum DRIVE the LOW band doesn't clip, so it drops ~9 dB below the clipped bands ("clean bass" clip 06 sounds thin unless LOW VOLUME comes up).
   - Expect to rebalance VOLUME whenever a DRIVE moves. That's normal for this layout, and the column-per-band panel makes it obvious.
7. **The rails position is ~3.4 dB louder,** with intermodulation like the diode positions. It's a loudness and edge difference, not a clarity one.
8. **Level:** at VOL 70 % the output is ~11 dB above the clean guitar. The OUTPUT trim has room to match bypass.

**Limits (what the simulation can't tell us):**
- noise and hiss at high DRIVE;
- how a real pickup's brighter top end changes the HIGH band;
- the feel and dynamics under real playing;
- the true TL074 clipping edge. The model rounds the rail clip slightly.

All of these are breadboard items (`docs/Breadboard Test.md`).
