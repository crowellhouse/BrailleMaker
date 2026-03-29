# ============================================================
# Script Name:      Braille Maker
# Public Release:   v1.0.1
# Internal Revision: v3r
#
# Full revision history: see CHANGELOG.md
#
# Description: Surface-aligned UEB Braille with domed dots.
#              Grade 1 built-in. Grade 2 via bundled liblouis
#              (no pip install — place files in louis/ folder).
# ============================================================
#
# GRADE 2 SETUP — one-time file placement:
#
#   1. Download the liblouis release from:
#      https://github.com/liblouis/liblouis/releases
#
#      Windows: liblouis-X.X.X-win64.zip
#      macOS:   brew install liblouis
#
#   2. Create a folder called  louis/  next to this script.
#
#   3. Copy into that folder:
#        louis/liblouis.dll      (Windows — from zip's bin/ folder)
#        louis/liblouis.dylib    (macOS  — copy the real versioned
#                                 file, not the symlink)
#        louis/tables/           (the entire tables/ folder)
#
#   macOS quarantine fix (run once in Terminal):
#        xattr -d com.apple.quarantine \
#            "/path/to/BrailleMaker/louis/liblouis.dylib"
#
#   Final layout:
#        BrailleMaker.py
#        louis/
#            liblouis.dll   or   liblouis.dylib
#            tables/
#                en-ueb-g2.ctb
#                en-ueb-g1.ctb
#                en-ueb-chardefs.uti
#                unicode.dis
#                ... (all other table files)
#
#   The script auto-detects the platform and any versioned
#   filename matching liblouis*.dylib / liblouis*.dll.
#
# ============================================================

import os
import ctypes
import traceback
import platform
import adsk.core
import adsk.fusion

app = adsk.core.Application.get()
ui  = app.userInterface

# ============================================================
# LIBLOUIS LOADER
# ============================================================

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
LOUIS_DIR    = os.path.join(SCRIPT_DIR, "louis")
TABLES_DIR   = os.path.join(LOUIS_DIR, "tables")

def find_dll():
    ext = ".dylib" if platform.system() == "Darwin" else ".dll"
    if not os.path.isdir(LOUIS_DIR):
        return None
    candidates = [
        f for f in os.listdir(LOUIS_DIR)
        if f.startswith("liblouis") and f.endswith(ext)
    ]
    if not candidates:
        return None
    if f"liblouis{ext}" in candidates:
        return os.path.join(LOUIS_DIR, f"liblouis{ext}")
    return os.path.join(LOUIS_DIR, candidates[0])


DLL_PATH   = find_dll()
TABLE_FILE = os.path.join(TABLES_DIR, "en-ueb-g2.ctb")

BRAILLE_UNICODE_OFFSET = 0x2800


def unicode_to_dots(braille_char):
    bits = ord(braille_char) - BRAILLE_UNICODE_OFFSET
    return [i + 1 for i in range(6) if bits & (1 << i)]


def load_liblouis():
    if not DLL_PATH or not os.path.isfile(DLL_PATH):
        return None, (
            f"liblouis DLL not found at:\n{DLL_PATH}\n\n"
            "Please follow the GRADE 2 SETUP instructions at the top of this script."
        )
    if not os.path.isfile(TABLE_FILE):
        return None, (
            f"UEB Grade 2 table not found at:\n{TABLE_FILE}\n\n"
            "Please copy the full tables/ folder from the liblouis release "
            "into the louis/ subfolder next to this script."
        )
    try:
        if platform.system() == "Windows":
            os.add_dll_directory(LOUIS_DIR)
        lib = ctypes.CDLL(DLL_PATH)
    except Exception as e:
        return None, f"ctypes failed to load the dylib:\n{DLL_PATH}\n\nError: {e}"
    try:
        lib.lou_setDataPath.restype  = None
        lib.lou_setDataPath.argtypes = [ctypes.c_char_p]
        lib.lou_setDataPath(LOUIS_DIR.encode("utf-8"))
    except Exception as e:
        return None, f"lou_setDataPath failed:\n{e}"
    try:
        lib.lou_translateString.restype  = ctypes.c_int
        lib.lou_translateString.argtypes = [
            ctypes.c_char_p, ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_int),
            ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_int),
            ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int,
        ]
    except Exception as e:
        return None, f"lou_translateString binding failed:\n{e}"
    try:
        test_text = "a"
        in_bytes  = test_text.encode("utf-16-le")
        in_chars  = ctypes.c_int(len(test_text))
        out_buf   = ctypes.create_string_buffer(32)
        out_chars = ctypes.c_int(16)
        lib.lou_translateString.restype  = ctypes.c_int
        lib.lou_translateString.argtypes = [
            ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int),
            ctypes.c_char_p, ctypes.POINTER(ctypes.c_int),
            ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int,
        ]
        result = lib.lou_translateString(
            TABLE_FILE.encode("utf-8"),
            in_bytes, ctypes.byref(in_chars),
            out_buf,  ctypes.byref(out_chars),
            None, None, 1
        )
        if result == 0:
            return None, "lou_translateString smoke test returned 0 (translation failed)."
    except Exception as e:
        return None, f"lou_translateString smoke test raised an exception:\n{e}"
    return lib, None


def translate_grade2(lib, text):
    ASCII_BRAILLE = {
        ' ': [],
        'A': [1], 'B': [1,2], 'C': [1,4], 'D': [1,4,5], 'E': [1,5],
        'F': [1,2,4], 'G': [1,2,4,5], 'H': [1,2,5], 'I': [2,4], 'J': [2,4,5],
        'K': [1,3], 'L': [1,2,3], 'M': [1,3,4], 'N': [1,3,4,5], 'O': [1,3,5],
        'P': [1,2,3,4], 'Q': [1,2,3,4,5], 'R': [1,2,3,5], 'S': [2,3,4], 'T': [2,3,4,5],
        'U': [1,3,6], 'V': [1,2,3,6], 'W': [2,4,5,6], 'X': [1,3,4,6],
        'Y': [1,3,4,5,6], 'Z': [1,3,5,6],
        '1': [1], '2': [1,2], '3': [1,4], '4': [1,4,5], '5': [1,5],
        '6': [1,2,4], '7': [1,2,4,5], '8': [1,2,5], '9': [2,4], '0': [2,4,5],
        'a': [1], 'b': [1,2], 'c': [1,4], 'd': [1,4,5], 'e': [1,5],
        'f': [1,2,4], 'g': [1,2,4,5], 'h': [1,2,5], 'i': [2,4], 'j': [2,4,5],
        'k': [1,3], 'l': [1,2,3], 'm': [1,3,4], 'n': [1,3,4,5], 'o': [1,3,5],
        'p': [1,2,3,4], 'q': [1,2,3,4,5], 'r': [1,2,3,5], 's': [2,3,4], 't': [2,3,4,5],
        'u': [1,3,6], 'v': [1,2,3,6], 'w': [2,4,5,6], 'x': [1,3,4,6],
        'y': [1,3,4,5,6], 'z': [1,3,5,6],
        '!': [2,3,4,6], '"': [5], '#': [3,4,5,6], '$': [1,2,4,6],
        '%': [1,4,6], '&': [1,2,3,4,6], "'": [3], '(': [1,2,3,5,6],
        ')': [2,3,4,5,6], '*': [1,6], '+': [3,4,6], ',': [2],
        '-': [3,6], '.': [2,5,6], '/': [3,4], ':': [2,5],
        ';': [2,3], '<': [1,2,6], '=': [1,2,3,4,5,6], '>': [3,4,5],
        '?': [2,6], '@': [4], '[': [2,4,6], '\\': [1,2,5,6],
        ']': [1,2,4,5,6], '^': [4,5], '_': [4,5,6], '`': [4],
    }
    table     = TABLE_FILE.encode("utf-8")
    in_bytes  = text.encode("utf-16-le")
    in_chars  = ctypes.c_int(len(text))
    max_out   = len(text) * 4
    out_buf   = ctypes.create_string_buffer(max_out * 2)
    out_chars = ctypes.c_int(max_out)
    lib.lou_translateString.restype  = ctypes.c_int
    lib.lou_translateString.argtypes = [
        ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int),
        ctypes.c_char_p, ctypes.POINTER(ctypes.c_int),
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int,
    ]
    result = lib.lou_translateString(
        table, in_bytes, ctypes.byref(in_chars),
        out_buf, ctypes.byref(out_chars), None, None, 0
    )
    if result == 0:
        raise RuntimeError(f"liblouis translation failed for: {text!r}")
    num_chars = out_chars.value
    raw_bytes = out_buf.raw[:num_chars * 2]
    ascii_str = raw_bytes.decode("utf-16-le")
    cells = []
    for ch in ascii_str:
        dots = ASCII_BRAILLE.get(ch)
        if dots is not None:
            cells.append(dots)
    return cells


# ============================================================
# PARAMETER DIALOG
# Presents dot geometry defaults to the user as an editable
# dialog. Values are used only for this run — nothing is
# written to the Fusion model. Returns a dict of float
# values in internal units (cm), or None if cancelled.
# ============================================================

DEFAULTS_MM = {
    "dotDia":       1.6,
    "dotSpacing":   2.5,
    "cellSpacingX": 6.1,
    "cellSpacingY": 10.0,
    "dotHeight":    0.8,
}

def ask_dot_params():
    defaults_str = (
        f"{DEFAULTS_MM['dotDia']},"
        f"{DEFAULTS_MM['dotSpacing']},"
        f"{DEFAULTS_MM['cellSpacingX']},"
        f"{DEFAULTS_MM['cellSpacingY']},"
        f"{DEFAULTS_MM['dotHeight']}"
    )

    prompt = (
        "Dot geometry parameters (all values in mm):\n"
        "  dotDia, dotSpacing, cellSpacingX, cellSpacingY, dotHeight\n\n"
        "Edit any value then click OK. UEB standard defaults are pre-filled.\n\n"
        "── Parameter guide ──────────────────────────────────────\n"
        "  dotDia       Dot diameter\n"
        "               UEB standard: 1.44–1.60 mm\n"
        "               Tactile range: 1.2–1.8 mm\n\n"
        "  dotSpacing   Centre-to-centre spacing between dots in a cell\n"
        "               UEB standard: 2.34–2.50 mm\n"
        "               Must be > dotDia to avoid overlap\n\n"
        "  cellSpacingX Horizontal centre-to-centre distance between cells\n"
        "               UEB standard: 6.10–7.60 mm\n\n"
        "  cellSpacingY Vertical centre-to-centre distance between lines\n"
        "               UEB standard: 10.00–10.16 mm\n\n"
        "  dotHeight    Raised dot height (extrusion before doming)\n"
        "               UEB standard: 0.48–0.90 mm\n"
        "               Must be ≤ dotDia/2 (dome fillet cannot exceed\n"
        "               the cylinder radius — max hemisphere)\n"
        "─────────────────────────────────────────────────────────"
    )

    while True:
        raw, cancelled = ui.inputBox(prompt, "Dot Parameters", defaults_str)
        if cancelled:
            return None

        parts = [p.strip() for p in raw.split(",")]
        if len(parts) != 5:
            ui.messageBox(
                "Please enter exactly 5 comma-separated values.",
                "Invalid input"
            )
            continue

        try:
            vals = [float(p) for p in parts]
        except ValueError:
            ui.messageBox(
                "All values must be numbers (e.g. 1.6, 2.5, 6.1, 10.0, 0.8).",
                "Invalid input"
            )
            continue

        dotDia, dotSpacing, cellSpacingX, cellSpacingY, dotHeight = vals

        if dotDia <= 0 or dotSpacing <= 0 or cellSpacingX <= 0 or cellSpacingY <= 0:
            ui.messageBox(
                "Diameter and spacing values must be greater than zero.",
                "Invalid input"
            )
            continue

        if dotHeight <= 0:
            ui.messageBox("dotHeight must be greater than zero.", "Invalid input")
            continue

        radius = dotDia / 2.0
        if dotHeight > radius:
            ui.messageBox(
                f"dotHeight ({dotHeight} mm) exceeds dotDia/2 ({radius} mm).\n\n"
                "The dome fillet radius cannot be greater than the cylinder radius.\n"
                "A perfect hemisphere (dotHeight = dotDia/2) is the maximum.\n\n"
                "Please reduce dotHeight or increase dotDia.",
                "Invalid input — fillet would fail"
            )
            continue

        # Convert mm → cm (Fusion internal units)
        return {
            "dotDia":       dotDia       / 10.0,
            "dotSpacing":   dotSpacing   / 10.0,
            "cellSpacingX": cellSpacingX / 10.0,
            "cellSpacingY": cellSpacingY / 10.0,
            "dotHeight":    dotHeight    / 10.0,
        }


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def run(_context: str):
    try:
        design   = app.activeProduct
        rootComp = design.rootComponent

        # ============================================================
        # GRADE SELECTION
        # ============================================================
        lib, load_error = load_liblouis()

        if lib is not None:
            gradePrompt = (
                "Braille Maker\n\n"
                "After selecting a grade you will be prompted to:\n"
                "  1. Set dot geometry parameters\n"
                "  2. Select a construction line (Braille origin)\n"
                "  3. Select the planar face to place dots on\n"
                "  4. Enter your text\n\n"
                "Enter grade:\n"
                "  1 — Grade 1 (letter-for-letter)\n"
                "  2 — Grade 2 (UEB contractions)"
            )
            gradeInput, cancelled = ui.inputBox(gradePrompt, "Braille Maker", "1")
            if cancelled:
                return
            if gradeInput.strip() == "2":
                use_grade2 = True
            elif gradeInput.strip() == "1":
                use_grade2 = False
            else:
                ui.messageBox("Invalid entry — please enter 1 or 2.", "Braille Maker")
                return
        else:
            gradePrompt = (
                "Braille Maker  —  Grade 1 only\n"
                f"(Grade 2 unavailable: {load_error})\n\n"
                "After clicking OK you will be prompted to:\n"
                "  1. Set dot geometry parameters\n"
                "  2. Select a construction line (Braille origin)\n"
                "  3. Select the planar face to place dots on\n"
                "  4. Enter your text"
            )
            confirmed, cancelled = ui.inputBox(gradePrompt, "Braille Maker", "OK")
            if cancelled:
                return
            use_grade2 = False

        # ============================================================
        # DOT GEOMETRY PARAMETERS
        # ============================================================
        params = ask_dot_params()
        if params is None:
            return

        dotDia       = params["dotDia"]
        dotSpacing   = params["dotSpacing"]
        cellSpacingX = params["cellSpacingX"]
        cellSpacingY = params["cellSpacingY"]
        dotHeight    = params["dotHeight"]
        radius       = dotDia / 2.0
        filletRadius = min(dotHeight, radius)

        # ============================================================
        # SURFACE SELECTION
        # ============================================================
        selectedLine = ui.selectEntity(
            "Select a construction line for Braille origin", "SketchLines"
        ).entity
        selectedFace = ui.selectEntity(
            "Select the planar face to attach Braille to", "PlanarFaces"
        ).entity
        targetBody = selectedFace.body

        # ============================================================
        # GRADE 1 BRAILLE MAP
        # ============================================================
        braille_map = {
            "a":[1],"b":[1,2],"c":[1,4],"d":[1,4,5],"e":[1,5],
            "f":[1,2,4],"g":[1,2,4,5],"h":[1,2,5],"i":[2,4],"j":[2,4,5],
            "k":[1,3],"l":[1,2,3],"m":[1,3,4],"n":[1,3,4,5],"o":[1,3,5],
            "p":[1,2,3,4],"q":[1,2,3,4,5],"r":[1,2,3,5],"s":[2,3,4],"t":[2,3,4,5],
            "u":[1,3,6],"v":[1,2,3,6],"w":[2,4,5,6],"x":[1,3,4,6],
            "y":[1,3,4,5,6],"z":[1,3,5,6],
            " ":[], ".":[2,5,6], ",":[2], "?":[2,6]
        }
        NUMBER_MAP     = {"1":"a","2":"b","3":"c","4":"d","5":"e",
                          "6":"f","7":"g","8":"h","9":"i","0":"j"}
        CAPITAL_PREFIX = [6]
        NUMBER_PREFIX  = [3,4,5,6]

        dot_positions = {
            1:(0,          -radius),
            2:(0,          -radius - dotSpacing),
            3:(0,          -radius - 2*dotSpacing),
            4:(dotSpacing, -radius),
            5:(dotSpacing, -radius - dotSpacing),
            6:(dotSpacing, -radius - 2*dotSpacing)
        }

        def expand_grade1(line):
            cells = []
            number_mode = False
            for ch in line:
                if ch.isdigit():
                    if not number_mode:
                        cells.append(NUMBER_PREFIX)
                        number_mode = True
                    cells.append(braille_map[NUMBER_MAP[ch]])
                else:
                    number_mode = False
                    if ch.isupper():
                        cells.append(CAPITAL_PREFIX)
                        ch = ch.lower()
                    cells.append(braille_map.get(ch, []))
            return cells

        def expand(line):
            if use_grade2:
                return translate_grade2(lib, line)
            return expand_grade1(line)

        # ============================================================
        # TEXT INPUT + SURFACE SIZE CHECK
        # ============================================================
        defaultText = "Hello|world"

        while True:
            text, cancelled = ui.inputBox(
                "Enter Braille text (use | for new lines):",
                "Braille Input",
                defaultText
            )
            if cancelled:
                return

            linesOfText = text.split("|")
            maxCells    = max(len(expand(l)) for l in linesOfText)
            numLines    = len(linesOfText)
            requiredW   = (maxCells - 1) * cellSpacingX + dotSpacing + dotDia
            requiredH   = (numLines  - 1) * cellSpacingY + 2 * dotSpacing + dotDia

            faceBB = selectedFace.boundingBox
            bbW    = faceBB.maxPoint.x - faceBB.minPoint.x
            bbH    = faceBB.maxPoint.y - faceBB.minPoint.y
            bbD    = faceBB.maxPoint.z - faceBB.minPoint.z
            dims   = sorted([abs(bbW), abs(bbH), abs(bbD)], reverse=True)
            faceW, faceH = dims[0], dims[1]

            if requiredW > faceW or requiredH > faceH:
                proceed = ui.messageBox(
                    f"The text may not fit on the selected surface.\n\n"
                    f"Required:  {requiredW*10:.1f} mm wide × {requiredH*10:.1f} mm tall\n"
                    f"Available: {faceW*10:.1f} mm × {faceH*10:.1f} mm\n\n"
                    "Proceed anyway, or click No to re-enter the text.",
                    "Text Too Large",
                    adsk.core.MessageBoxButtonTypes.YesNoButtonType
                )
                if proceed != adsk.core.DialogResults.DialogYes:
                    defaultText = text
                    continue
            break

        expandedLines = [expand(l) for l in linesOfText]

        # ============================================================
        # TIMELINE MARKER
        # ============================================================
        timeline      = design.timeline
        timelineStart = timeline.count

        extrudes = rootComp.features.extrudeFeatures
        fillets  = rootComp.features.filletFeatures

        faceNormal = selectedFace.geometry.normal
        faceNormal.normalize()

        # ============================================================
        # ONE SKETCH + ONE EXTRUDE + ONE COMBINE + ONE FILLET PER LINE
        # ============================================================

        # Read the construction line's direction in sketch space from the
        # first sketch we create. All subsequent sketches on the same face
        # share the same orientation so we only need to do this once.
        #
        # lineDir  = unit vector along the construction line in sketch space
        #            → Braille cells spread in this direction
        # perpDir  = unit vector perpendicular to the line, rotated 90° CCW
        #            → lines of Braille step in this direction
        #
        # This replaces the assumption that sketch X = "right" and sketch
        # Y = "up", which breaks on vertical faces where Fusion may orient
        # the sketch Y axis in -Z instead of +Z.
        _orient_sketch = rootComp.sketches.add(selectedFace)
        _projected     = _orient_sketch.project(selectedLine)
        _curve         = _projected[0].geometry        # Line3D in sketch space
        _dx = _curve.endPoint.x - _curve.startPoint.x
        _dy = _curve.endPoint.y - _curve.startPoint.y
        _len = (_dx**2 + _dy**2) ** 0.5
        if _len < 1e-10:
            ui.messageBox(
                "Construction line has zero length in sketch space — "
                "cannot determine Braille direction.",
                "Braille Maker Error"
            )
            return
        # Unit vector along the line (cell-to-cell direction)
        lineDir  = (_dx / _len, _dy / _len)
        # Unit vector perpendicular, rotated 90° CCW (line-to-line direction)
        # Rotating (a, b) by 90° CCW gives (-b, a)
        perpDir  = (-lineDir[1], lineDir[0])
        _orient_sketch.deleteMe()

        for lineIndex, cells in enumerate(expandedLines):

            # SKETCH
            sketch    = rootComp.sketches.add(selectedFace)
            projected = sketch.project(selectedLine)
            origin    = projected[0].startSketchPoint.geometry
            circles   = sketch.sketchCurves.sketchCircles

            newCenters = []
            for i, pattern in enumerate(cells):
                for dot in pattern:
                    # dot_positions gives (dx, dy) offsets in "cell space":
                    #   dx = offset along the dot-column axis (within a cell)
                    #   dy = offset along the dot-row axis (within a cell)
                    # We map these onto the actual sketch axes using lineDir
                    # and perpDir so the cell layout always follows the line.
                    raw_dx, raw_dy = dot_positions[dot]

                    # Cell origin: step i cells along lineDir from the
                    # construction line origin, then step lineIndex lines
                    # along -perpDir (lines advance away from the line).
                    cell_along  = i * cellSpacingX
                    line_across = lineIndex * cellSpacingY

                    # Within each cell: raw_dx advances along lineDir,
                    # raw_dy advances along -perpDir (dot rows go away
                    # from the construction line, matching the v1f offset
                    # convention where dy is negative).
                    x = (origin.x
                         + (cell_along + raw_dx) * lineDir[0]
                         + (-line_across + raw_dy) * perpDir[0])
                    y = (origin.y
                         + (cell_along + raw_dx) * lineDir[1]
                         + (-line_across + raw_dy) * perpDir[1])

                    circles.addByCenterRadius(
                        adsk.core.Point3D.create(x, y, 0), radius
                    )
                    newCenters.append((x, y))

            circleProfiles = adsk.core.ObjectCollection.create()
            for i in range(sketch.profiles.count):
                prof = sketch.profiles.item(i)
                if not (prof.profileLoops.count == 1 and
                        prof.profileLoops.item(0).profileCurves.count == 1):
                    continue
                bb = prof.boundingBox
                cx = (bb.minPoint.x + bb.maxPoint.x) / 2.0
                cy = (bb.minPoint.y + bb.maxPoint.y) / 2.0
                if any(abs(cx - nx) < radius * 1.5 and abs(cy - ny) < radius * 1.5
                       for nx, ny in newCenters):
                    circleProfiles.add(prof)

            if circleProfiles.count == 0:
                continue

            # EXTRUDE — all dots on this line, one body per profile
            extInput = extrudes.createInput(
                circleProfiles,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )
            extInput.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(dotHeight)
            )
            ext = extrudes.add(extInput)

            # Record top rim centers before combine invalidates references
            topCenters = []
            for j in range(ext.bodies.count):
                dotBody = ext.bodies.item(j)
                circularEdges = [
                    e for e in dotBody.edges
                    if e.geometry.curveType == adsk.core.Curve3DTypes.Circle3DCurveType
                ]
                if not circularEdges:
                    continue

                def projection(edge):
                    c = edge.geometry.center
                    return (c.x * faceNormal.x +
                            c.y * faceNormal.y +
                            c.z * faceNormal.z)

                topEdge = max(circularEdges, key=projection)
                tc = topEdge.geometry.center
                topCenters.append((tc.x, tc.y, tc.z))

            # COMBINE — join all dots on this line to the target body
            toolBodies = adsk.core.ObjectCollection.create()
            for j in range(ext.bodies.count):
                toolBodies.add(ext.bodies.item(j))

            combineInput = rootComp.features.combineFeatures.createInput(
                targetBody, toolBodies
            )
            combineInput.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
            rootComp.features.combineFeatures.add(combineInput)

            # FILLET — re-resolve top rim edges from live body after combine
            tol = radius * 0.1
            lineTopEdges = adsk.core.ObjectCollection.create()
            for (tx, ty, tz) in topCenters:
                for edge in targetBody.edges:
                    if edge.geometry.curveType != adsk.core.Curve3DTypes.Circle3DCurveType:
                        continue
                    ec = edge.geometry.center
                    if (abs(ec.x - tx) < tol and
                        abs(ec.y - ty) < tol and
                        abs(ec.z - tz) < tol):
                        lineTopEdges.add(edge)
                        break

            if lineTopEdges.count > 0:
                filletInput = fillets.createInput()
                filletInput.addConstantRadiusEdgeSet(
                    lineTopEdges,
                    adsk.core.ValueInput.createByReal(filletRadius),
                    True
                )
                fillets.add(filletInput)

        # ============================================================
        # TIMELINE GROUP
        # ============================================================
        timelineEnd = timeline.count - 1
        if timelineEnd >= timelineStart + 1:
            timelineGroup = timeline.timelineGroups.add(timelineStart, timelineEnd)
            rawLabel  = text.replace("|", " ").strip()
            safeLabel = rawLabel[:5].replace(" ", "_")
            grade_tag = "G2" if use_grade2 else "G1"
            timelineGroup.name = f"Braille-{safeLabel}-{grade_tag}"

        grade_label = "Grade 2 (UEB)" if use_grade2 else "Grade 1"
        ui.messageBox(f"Braille complete — {grade_label}!")

    except:
        err = traceback.format_exc()
        app.log(f'Failed:\n{err}')
        ui.messageBox(f"Script error:\n\n{err}", "Braille Maker Error",
                      adsk.core.MessageBoxButtonTypes.OKButtonType)