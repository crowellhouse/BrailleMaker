# Changelog

All notable changes to Braille Maker are documented here.

External releases follow [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`).
Internal revisions are tracked in the script header and cross-referenced below.

---

## [1.0.3] — 2026-03-29
**Internal revision: v3t**

### Fixed
- Grade 2 translation still incorrect after v1.0.2. The v1.0.2 fix replaced the old UEB literary table with the positional BRF formula (`N-32` in bits), but liblouis does not use positional BRF — it uses the **BANA BRF convention** (the embosser encoding defined by `en-us-brf.dis`). These are two different standards that share the same 64 ASCII characters but assign them different dot patterns. The critical difference: in BANA BRF, `','` (ASCII 44) = dot 6 (capital indicator ⠠), not dots 3,4 as the positional formula gives. This is why v1.0.2 still produced wrong output — the capital indicator was now dots 3,4 instead of dot 2 (v1.0.1) but still not the correct dot 6. The `ASCII_BRAILLE` dict has been replaced with the correct BANA BRF table derived from the liblouis `en-us-brf.dis` display table.

---

## [1.0.2] — 2026-03-29
**Internal revision: v3s**

### Fixed
- Attempted fix for Grade 2 dot pattern errors. Replaced UEB literary dot patterns with the positional BRF formula. This was an improvement but still incorrect — see v1.0.3 for the complete fix.

---

## [1.0.1] — 2026-03-28
**Internal revision: v3r**

### Fixed
- Braille orientation incorrect on vertical faces. On faces whose normal is not aligned with world Z, Fusion orients the sketch Y axis in an unpredictable direction (e.g. -Z instead of +Z on a face in the -Y range). Dot positions were computed assuming sketch X = "right" and sketch Y = "up", causing Braille to run in the wrong direction or flip vertically. Fix: after creating the first orientation sketch, read the projected construction line's direction vector in sketch space (`projected[0].geometry`), compute a unit vector along the line (`lineDir`) and a perpendicular unit vector rotated 90° CCW (`perpDir`), then use these to place all dot centers. Cells now always advance along the construction line direction and lines always step perpendicularly away from it, regardless of face orientation.

---

## [1.0.0] — 2026-03-28
**Internal revision: v3q**

First public release.

### Features
- Grade 1 UEB — letter-for-letter translation via built-in character map. Works with no external dependencies.
- Grade 2 UEB — full UEB contracted Braille via bundled liblouis loaded at runtime through Python's `ctypes` module. No pip install required. Supports 180+ contractions.
- Auto-detection of liblouis filename — any file matching `liblouis*.dylib` (macOS) or `liblouis*.dll` (Windows) in the `louis/` folder is found automatically, including versioned filenames.
- Dot geometry dialog — all five dot parameters presented as a comma-separated mm list with UEB standard defaults pre-filled. Validated before proceeding. Values are per-run only and not written to the Fusion model.
- Surface size check — warns if entered text exceeds face bounds, with option to proceed or re-enter.
- Multi-line text — use `|` to create multiple lines of Braille in a single run.
- Capital and numeric indicators applied automatically.
- Multiple independent runs on the same surface — position-based profile filter ensures only the current run's circles are extruded.
- One extrude per line of text (multi-profile feature) — one body per dot, one timeline feature per line.
- Hemisphere fillet on all dot tops — one fillet feature per line of text. Dialog enforces `dotHeight ≤ dotDia/2` to guarantee fillet success.
- Single combine per line joining all dot bodies to the target body.
- Named timeline group per run — `Braille-{first5chars}-{G1|G2}`.
- Works on any axis-aligned or arbitrarily angled planar face.
- Error dialog shows full traceback on script failure.

---

## Internal revision history

This section documents all internal revisions for contributors and anyone building on this project. Each entry describes what changed and why.

### v3t (→ public release v1.0.3)
Replaced `ASCII_BRAILLE` again with the correct BANA BRF table derived from the liblouis `en-us-brf.dis` display table. The v3s fix used the positional BRF formula (`N-32` in bits) which is a different standard — liblouis uses the BANA embosser convention where `','` = dot 6 (capital indicator), `'#'` = dots 3456 (number indicator), and letters A–Z map to standard braille letter patterns without dot 6. The positional formula and BANA BRF share the same 64 ASCII characters but assign entirely different dot patterns to most of them. The correct approach is to invert the unicode-braille-to-ASCII mapping from `en-us-brf.dis`.

### v3s (→ public release v1.0.2)
Replaced `ASCII_BRAILLE` with the positional BRF formula (`N-32` in bits). This was an improvement over the UEB literary values but still incorrect — liblouis uses BANA BRF, not positional BRF. See v3t.

### v3r (→ public release v1.0.1)
Fixed Braille orientation on vertical faces. Root cause: dot positions were computed as `origin + i*cellSpacingX` in raw sketch X/Y, assuming sketch X always points along the construction line and sketch Y always points "up". On vertical faces Fusion orients the sketch Y axis based on the face normal, which can point in -Z instead of +Z, causing Braille to run backwards or vertically. Fix: project the construction line into a temporary orientation sketch, read the resulting `Line3D` geometry to extract the line's direction vector in sketch space, normalise it to `lineDir`, compute `perpDir` as `lineDir` rotated 90° CCW. All dot centers are then placed using `lineDir` for cell-to-cell spacing and `-perpDir` for line-to-line stepping. The orientation sketch is deleted immediately after. This fix makes Braille follow the construction line direction correctly on any face orientation.

### v3q (→ public release v1.0.0)
Restored one-fillet-per-line behaviour (reverted the per-dot fillet loop from v3m). Root cause of `ASM_BL_CANNOT_REORDER` was confirmed to be `filletRadius > cylinderRadius` — a parameter mismatch — not the number of edges per fillet. With the v3p dialog guaranteeing `filletRadius ≤ radius`, all top rim edges for a line can be submitted to a single `fillets.add()`. Timeline per line: sketch → extrude → combine → fillet (4 features).

### v3p
Changed default `dotDia` from 1.5 mm to 1.6 mm. Loosened fillet validation: `dotHeight == dotDia/2` (perfect hemisphere) is now permitted; only `dotHeight > dotDia/2` is rejected. `filletRadius` clamp updated from `radius * 0.99` to `min(dotHeight, radius)`. Expanded `ask_dot_params()` prompt with full UEB standard ranges for each parameter.

### v3o
Removed all Fusion user parameter writes. Replaced with `ask_dot_params()`: a single inputBox dialog presenting all five parameters as a comma-separated mm list with UEB standard defaults pre-filled. Dialog validates `dotHeight ≤ dotDia/2` and rejects invalid entries with a clear explanation. `filletRadius` computed as `min(dotHeight, radius)`. Dot geometry dialog appears before surface selection. `DEFAULTS_MM` dict centralises UEB standard default values.

### v3n
Diagnostic version. Per-dot fillet try/except loop with full logging. Identified root cause of fillet failures: user had `dotDia=1.5mm` (radius=0.75mm) but `dotHeight=0.8mm`, making `filletRadius > cylinderRadius`. ACIS cannot compute a fillet that exceeds the cylinder radius.

### v3m
Attempted fix for `ASM_BL_CANNOT_REORDER` by filleting each dot individually. Still failed — root cause not yet identified at this point.

### v3l
Diagnostic version. Confirmed edge matching was exact (Δ=0.000mm). Failure was in the fillet call itself: `ASM_BL_CANNOT_REORDER` when all edges submitted simultaneously.

### v3k
Fixed fillet failures from v3j. Reverted to proven pre-combine top-edge identification: use face-normal projection on each dot body's circular edges before the combine to find the top rim, record its world-space XYZ center, then re-resolve those edges on the live `targetBody` after combine by matching centers within tight tolerance (`radius * 0.1`). Gives Fusion valid post-combine edge references while guaranteeing only true top rims are selected.

### v3j
Fixed `EDGE_REFERENCE_LOST` fillet failure from v3i. Root cause: combine feature rebuilds `targetBody` B-rep topology, invalidating all edge references collected from pre-combine dot bodies. Fix: removed pre-combine edge collection. Top-rim edges collected from live `targetBody` after combine, filtered by face-normal projection and dot center proximity.

### v3i
Restructured geometry loop from one-extrude-per-dot to one extrude per line. Filtered `circleProfiles` built as `ObjectCollection` and passed to `extrudes.createInput()` — produces one body per profile in a single feature. Combine and fillet now execute inside the per-line loop.

### v3h
Replaced YesNoCancel grade dialog with `inputBox` number entry. User types 1 or 2. Invalid entries show a clear error and exit.

### v3g
Replaced two opening dialogs (placement + grade) with a single combined dialog using `YesNoCancelButtonType`.

### v3f
First clean stable internal release. Confirmed working for single and multiple runs on the same surface. All diagnostics removed.

### v3e
Removed leftover `hiddenSketches` restore block after the fillet step (missed in v3d cleanup) causing `NameError`.

### v3d
Returned to one-sketch-per-line approach. Replaced profile structure filter with position-based filter: each profile's bounding box center is checked against newly placed dot centers. Profiles from previous runs are rejected by position. Removed all hide/suppress overhead from v2n–v3c.

### v3a–v3c
Multiple failed attempts to solve cross-sketch geometry inheritance using: `isComputeDeferred`, offset construction planes, `modelToSketchSpace`. All failed due to Fusion copying all circles from co-planar sketches into each new sketch.

### v2z
Added origin diagnostic confirming `projected[0].geometry.startPoint` is correct between runs — root cause was downstream in dot sketches.

### v2x–v2y
Attempted `modelToSketchSpace` for stable sketch-to-world coordinate mapping. Caused cylinders to appear off-surface as line start point was not exactly on face plane.

### v2v–v2w
Attempted persistent origin sketch (no `deleteMe`) to prevent stale projection accumulation. Still returned last dot position of previous run.

### v2u
Introduced `newDotCenters` set to record newly placed dot positions and restrict post-join edge scan to only new dots. `sketchKey()` updated to use face-normal subtraction.

### v2t
Fixed fillet applied to base edges instead of top edges. Root cause: bucket key included all three coordinates so top and base ended up in separate buckets. Fix: bucket key uses only in-plane position (center minus normal component) so top and base share one bucket; highest projection wins.

### v2s
Fixed entire surface being extruded. Root cause: `profiles.item(0)` returned the face remainder profile, not the circle. Fix: select profile with smallest bounding box area.

### v2r
Fixed `EDGE_REFERENCE_LOST` on fillet. Root cause: edges collected from dot bodies before join became invalid after merge. Fix: scan `targetBody.edges` after join, bucket by in-plane center, keep highest normal projection per bucket.

### v2q–v2p (one-sketch-per-dot attempts)
Multiple revisions attempting one sketch per dot to isolate profiles. Origin was computed correctly (confirmed by diagnostic) but dot positions were wrong — Fusion was copying all circles from all co-planar sketches into each new sketch regardless of `isComputeDeferred`.

### v2m
Abandoned Unicode braille output. Root cause: liblouis on macOS Homebrew outputs ASCII braille regardless of mode flags or display table. Fix: accept ASCII output and map via hardcoded ASCII braille lookup table.

### v2l
Switched to `lou_translate` with `unicode.dis` display table. Still produced ASCII — `unicode.dis` not applied by this liblouis build.

### v2k
Changed mode flag from 0 to 1 in `lou_translateString`. Still produced ASCII.

### v2j
Added raw codepoint diagnostic to identify what liblouis actually returns.

### v2g
Fixed `ValueError: character U+2c003b is not in range`. Root cause: `wchar_t` size mismatch between Python (4-byte on macOS) and liblouis (2-byte). Rewrote `translate_grade2()` using raw `c_char_p` byte buffers with UTF-16-LE encoding.

### v2f
Fixed `ValueError` from buffer overread. Used `out_buf.value` directly and filtered to valid braille Unicode block (U+2800–U+28FF).

### v2e
Changed outer `except` block to show `messageBox` with full traceback instead of only logging to `app.log`.

### v2d
Replaced hardcoded DLL filename with `find_dll()` which scans `louis/` for any matching `liblouis*.dylib` or `liblouis*.dll`. Versioned filenames detected automatically.

### v2c
Removed unused `import sys`. Fixed filename reference in setup comment block.

### v2b
Split `load_liblouis()` error handling into four discrete steps so the fallback message shows the exact failure point.

### v2a
Added UEB Grade 2 support via bundled liblouis loaded through Python's `ctypes` module. No pip install required. `load_liblouis()` resolves DLL and table paths relative to the script directory. `translate_grade2()` calls `lou_translateString` with `en-ueb-g2.ctb`. Timeline group name includes `-G1` or `-G2` suffix.

### v1i
No on the placement dialog now exits silently. Removed all free-standing XY code paths. Size check warning upgraded from OK-only to Yes/No.

### v1h
Added surface size check after text input. Computes required dot footprint from cell count and line count, compares against face bounding box. Warns with dimensions if text is too large. Loops back to input prompt with previous text pre-filled.

### v1g
Added timeline grouping. Group name is `Braille-` + first 5 characters of input text.

### v1f
Fixed dots 1 & 4 (top row) always missing. Root cause: `dot_positions` placed them at `dy=0`, exactly on the projected construction line. Fusion bisected those circles producing multi-loop profiles rejected by the filter. Fix: shift all dot Y positions down by `-radius`.

### v1e
Fixed dome fillet applied to base edge on non-XY surfaces. Root cause: bounding box maxZ comparison is world-space and fails when extrusion axis is not Z. Fix: use face normal projection to identify the top rim regardless of orientation.

### v1d
Replaced per-extrude join with a single combine feature at the end.

### v1c
Fixed fillet applied to base edge instead of top edge. Used `boundingBox.maxZ` against body's own `maxZ`. Restored Yes/No placement dialog with improved wording.

### v1b
Fixed dome not appearing in attach mode. Root cause: `JoinFeatureOperation` on extrude prevented bodies from being stored for fillet. Fix: extrude as `NewBody` first, collect top edge, then combine.

### v1a
Initial release. Consolidated from `brailletest v1e.6`. Features: parametric dot grid, UEB spacing standards, multi-line input, capitals and numbers, construction line + face selection, domed dots via top-edge fillet, per-line sketches.
### v3j
Fixed `EDGE_REFERENCE_LOST` fillet failure from v3i. Root cause: combine feature rebuilds `targetBody` B-rep topology, invalidating all edge references collected from pre-combine dot bodies. Fix: removed pre-combine edge collection. Top-rim edges collected from live `targetBody` after combine, filtered by face-normal projection and dot center proximity.

### v3i
Restructured geometry loop from one-extrude-per-dot to one extrude per line. Filtered `circleProfiles` built as `ObjectCollection` and passed to `extrudes.createInput()` — produces one body per profile in a single feature. Combine and fillet now execute inside the per-line loop.

### v3h
Replaced YesNoCancel grade dialog with `inputBox` number entry. User types 1 or 2. Invalid entries show a clear error and exit.

### v3g
Replaced two opening dialogs (placement + grade) with a single combined dialog using `YesNoCancelButtonType`.

### v3f
First clean stable internal release. Confirmed working for single and multiple runs on the same surface. All diagnostics removed.

### v3e
Removed leftover `hiddenSketches` restore block after the fillet step (missed in v3d cleanup) causing `NameError`.

### v3d
Returned to one-sketch-per-line approach. Replaced profile structure filter with position-based filter: each profile's bounding box center is checked against newly placed dot centers. Profiles from previous runs are rejected by position. Removed all hide/suppress overhead from v2n–v3c.

### v3a–v3c
Multiple failed attempts to solve cross-sketch geometry inheritance using: `isComputeDeferred`, offset construction planes, `modelToSketchSpace`. All failed due to Fusion copying all circles from co-planar sketches into each new sketch.

### v2z
Added origin diagnostic confirming `projected[0].geometry.startPoint` is correct between runs — root cause was downstream in dot sketches.

### v2x–v2y
Attempted `modelToSketchSpace` for stable sketch-to-world coordinate mapping. Caused cylinders to appear off-surface as line start point was not exactly on face plane.

### v2v–v2w
Attempted persistent origin sketch (no `deleteMe`) to prevent stale projection accumulation. Still returned last dot position of previous run.

### v2u
Introduced `newDotCenters` set to record newly placed dot positions and restrict post-join edge scan to only new dots. `sketchKey()` updated to use face-normal subtraction.

### v2t
Fixed fillet applied to base edges instead of top edges. Root cause: bucket key included all three coordinates so top and base ended up in separate buckets. Fix: bucket key uses only in-plane position (center minus normal component) so top and base share one bucket; highest projection wins.

### v2s
Fixed entire surface being extruded. Root cause: `profiles.item(0)` returned the face remainder profile, not the circle. Fix: select profile with smallest bounding box area.

### v2r
Fixed `EDGE_REFERENCE_LOST` on fillet. Root cause: edges collected from dot bodies before join became invalid after merge. Fix: scan `targetBody.edges` after join, bucket by in-plane center, keep highest normal projection per bucket.

### v2q–v2p (one-sketch-per-dot attempts)
Multiple revisions attempting one sketch per dot to isolate profiles. Origin was computed correctly (confirmed by diagnostic) but dot positions were wrong — Fusion was copying all circles from all co-planar sketches into each new sketch regardless of `isComputeDeferred`.

### v2m
Abandoned Unicode braille output. Root cause: liblouis on macOS Homebrew outputs ASCII braille regardless of mode flags or display table. Fix: accept ASCII output and map via hardcoded ASCII braille lookup table.

### v2l
Switched to `lou_translate` with `unicode.dis` display table. Still produced ASCII — `unicode.dis` not applied by this liblouis build.

### v2k
Changed mode flag from 0 to 1 in `lou_translateString`. Still produced ASCII.

### v2j
Added raw codepoint diagnostic to identify what liblouis actually returns.

### v2g
Fixed `ValueError: character U+2c003b is not in range`. Root cause: `wchar_t` size mismatch between Python (4-byte on macOS) and liblouis (2-byte). Rewrote `translate_grade2()` using raw `c_char_p` byte buffers with UTF-16-LE encoding.

### v2f
Fixed `ValueError` from buffer overread. Used `out_buf.value` directly and filtered to valid braille Unicode block (U+2800–U+28FF).

### v2e
Changed outer `except` block to show `messageBox` with full traceback instead of only logging to `app.log`.

### v2d
Replaced hardcoded DLL filename with `find_dll()` which scans `louis/` for any matching `liblouis*.dylib` or `liblouis*.dll`. Versioned filenames detected automatically.

### v2c
Removed unused `import sys`. Fixed filename reference in setup comment block.

### v2b
Split `load_liblouis()` error handling into four discrete steps so the fallback message shows the exact failure point.

### v2a
Added UEB Grade 2 support via bundled liblouis loaded through Python's `ctypes` module. No pip install required. `load_liblouis()` resolves DLL and table paths relative to the script directory. `translate_grade2()` calls `lou_translateString` with `en-ueb-g2.ctb`. Timeline group name includes `-G1` or `-G2` suffix.

### v1i
No on the placement dialog now exits silently. Removed all free-standing XY code paths. Size check warning upgraded from OK-only to Yes/No.

### v1h
Added surface size check after text input. Computes required dot footprint from cell count and line count, compares against face bounding box. Warns with dimensions if text is too large. Loops back to input prompt with previous text pre-filled.

### v1g
Added timeline grouping. Group name is `Braille-` + first 5 characters of input text.

### v1f
Fixed dots 1 & 4 (top row) always missing. Root cause: `dot_positions` placed them at `dy=0`, exactly on the projected construction line. Fusion bisected those circles producing multi-loop profiles rejected by the filter. Fix: shift all dot Y positions down by `-radius`.

### v1e
Fixed dome fillet applied to base edge on non-XY surfaces. Root cause: bounding box maxZ comparison is world-space and fails when extrusion axis is not Z. Fix: use face normal projection to identify the top rim regardless of orientation.

### v1d
Replaced per-extrude join with a single combine feature at the end.

### v1c
Fixed fillet applied to base edge instead of top edge. Used `boundingBox.maxZ` against body's own `maxZ`. Restored Yes/No placement dialog with improved wording.

### v1b
Fixed dome not appearing in attach mode. Root cause: `JoinFeatureOperation` on extrude prevented bodies from being stored for fillet. Fix: extrude as `NewBody` first, collect top edge, then combine.

### v1a
Initial release. Consolidated from `brailletest v1e.6`. Features: parametric dot grid, UEB spacing standards, multi-line input, capitals and numbers, construction line + face selection, domed dots via top-edge fillet, per-line sketches.
