# Braille Maker for Autodesk Fusion 360

A Fusion 360 Python script that automatically generates raised UEB Braille dots on any flat surface of a 3D model. Choose a grade, configure dot geometry, pick a construction line and face, type your text, and the script extrudes precision domed dot cylinders ready for 3D printing or CNC machining.


<img width="455" height="450" alt="Braille Baseball Field Diagram" src="https://github.com/user-attachments/assets/bbe1c5f3-076f-441c-8b74-8812bf4d524f" />


https://github.com/user-attachments/assets/af1b1b4a-9ee7-4435-a450-52b84d87e649


---

## Features

- **Grade 1 and Grade 2 UEB** — Grade 1 is letter-for-letter and works out of the box. Grade 2 uses full UEB contractions (180+) via the bundled liblouis library with no pip install required.
- **Any flat surface** — works on XY, YZ, XZ, and arbitrarily angled faces. Dots always extrude outward from the selected face regardless of orientation.
- **Configurable dot geometry** — all five dot and spacing parameters are presented in a dialog at the start of each run with UEB standard defaults pre-filled. Values are validated against UEB ranges before proceeding.
- **Multi-line text** — use the `|` character to place multiple lines of Braille in a single run.
- **Multiple independent runs** — run the script as many times as needed on the same surface. Each run is fully isolated; previous dots are never re-extruded or re-filleted.
- **Domed dots** — each dot cylinder receives a hemisphere fillet. The dialog enforces `dotHeight ≤ dotDia/2` so the fillet always succeeds.
- **Clean timeline** — all features for each run are grouped under a named timeline group (`Braille-XXXXX-G1` or `Braille-XXXXX-G2`). Each line of text produces exactly four features: sketch → extrude → combine → fillet.
- **Surface size check** — warns if the entered text exceeds the face bounds, with the option to proceed or re-enter.
- **Capital and number indicators** — UEB capital and numeric mode indicators are applied automatically.
- **macOS and Windows** — auto-detects platform and loads the correct liblouis binary filename automatically.

---

## How it works

### Workflow

```
Run script → Choose grade → Set dot geometry → Select construction line → Select face → Enter text → Braille created
```

1. The opening dialog asks for Grade 1 or Grade 2 and shows the steps ahead.
2. A dot geometry dialog presents five parameters as comma-separated mm values with UEB defaults. You can edit any value. The dialog validates that `dotHeight ≤ dotDia/2` before allowing you to proceed.
3. You select a construction line — its start point becomes the top-left origin of the first Braille cell.
4. You select the flat face where dots will be placed.
5. You enter your text. The script checks whether it fits the face bounds.
6. The text is translated into UEB dot patterns — Grade 1 via built-in character map, Grade 2 via liblouis.
7. For each line of text one sketch is created containing all dot circles for that line.
8. A position-based profile filter selects only the newly placed circles, ignoring any circles inherited from previous runs on the same face.
9. All circles in each sketch are extruded together as a single multi-profile feature (one body per dot).
10. All dot bodies for the line are joined to the target body in one combine operation.
11. Top edges are re-resolved from the live body after the combine by matching recorded world-space center coordinates, then filleted in one operation per line.
12. All features are grouped in the timeline under a named group.

### Dot cell layout

Each Braille character occupies a cell with up to 6 dots arranged in a 2×3 grid following the UEB standard:

```
Dot 1 · Dot 4
Dot 2 · Dot 5
Dot 3 · Dot 6
```

### Grade 1 vs Grade 2

| | Grade 1 | Grade 2 |
|---|---|---|
| Translation | Letter-for-letter | UEB contractions |
| "the" | 3 cells (t, h, e) | 1 cell (dots 2,3,4,6) |
| Contractions | None | 180+ via liblouis |
| Requires liblouis | No | Yes |
| Best for | Part numbers, codes, short labels | Running text, instructions |

---

## Requirements

- Autodesk Fusion 360 (any recent version)
- Python — bundled with Fusion 360, no separate install needed
- liblouis — optional, required for Grade 2 only (see [Grade 2 Setup](#grade-2-setup))

---

## Installation

### 1. Add the script to Fusion 360

1. Download or clone this repository.
2. In Fusion 360 go to **Utilities → Scripts and Add-ins** (or press `Shift+S`).
3. Click the **+** button next to **My Scripts**.
4. Navigate to and select the `BrailleMaker` folder.
5. The script will appear in the My Scripts list.

**Default script locations:**

| Platform | Path |
|---|---|
| macOS | `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/Scripts` |
| Windows | `C:\Users\YourName\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\Scripts` |

### 2. Grade 2 Setup

Grade 2 requires liblouis to be placed in a `louis/` subfolder next to the script file.

#### Required folder layout

```
BrailleMaker/
├── BrailleMaker.py
└── louis/
    ├── liblouis.dll          ← Windows
    ├── liblouis.dylib        ← macOS  (any versioned filename is detected automatically)
    └── tables/
        ├── en-ueb-g2.ctb
        ├── en-ueb-g1.ctb
        ├── en-ueb-chardefs.uti
        ├── unicode.dis
        └── ... (all other table files from the liblouis release)
```

#### macOS

```bash
# Install liblouis via Homebrew
brew install liblouis

# Find the real versioned dylib (not the symlink)
ls -la /opt/homebrew/lib/liblouis*.dylib

# Copy the versioned file (the one without an arrow →) into louis/
cp /opt/homebrew/lib/liblouis.20.0.0.dylib \
    "/path/to/BrailleMaker/louis/liblouis.dylib"

# Copy the tables folder
cp -r /opt/homebrew/share/liblouis/tables \
    "/path/to/BrailleMaker/louis/tables"

# Clear the quarantine flag so macOS allows the dylib to load
xattr -d com.apple.quarantine \
    "/path/to/BrailleMaker/louis/liblouis.dylib"
```

> **Note:** Copy the real versioned `.dylib` — not the symlink. The version number varies depending on what Homebrew installed. The script auto-detects any filename matching `liblouis*.dylib`.

#### Windows

1. Download the latest release zip from [github.com/liblouis/liblouis/releases](https://github.com/liblouis/liblouis/releases) — look for `liblouis-X.X.X-win64.zip`.
2. Create a `louis\` folder inside `BrailleMaker\`.
3. Copy `liblouis.dll` from the zip's `bin\` folder into `louis\`.
4. Copy the entire `tables\` folder from the zip into `louis\`.

---

## Usage

### Before you run the script — create a construction line

Before running the script you need a construction line in your Fusion 360 model. The start point of this line defines the top-left origin of the first Braille cell.

1. Open the model containing the face where you want Braille.
2. Create a new sketch on that face.
3. Draw a straight line starting at the exact position where the Braille text should begin. Length does not matter — only the start point is used.
4. Finish the sketch.

> **Tip:** If you plan to place multiple blocks of Braille on the same face you can prepare all your construction lines before running the script at all — either by moving a single line between runs, or by laying out a grid of lines in one sketch covering all the positions you need.

---

### Step 1 — Run the script

Go to **Utilities → Scripts and Add-ins** (Shift+S), select **Braille Maker**, and click **Run**.

### Step 2 — Choose a grade

An input dialog opens showing the full workflow and asking for a grade. The field is pre-filled with `1`.

```
1 — Grade 1 (letter-for-letter, no contractions)
2 — Grade 2 (UEB contractions — requires liblouis)
```

Type `1` or `2` and click OK. Cancel exits without making any changes. If liblouis is not found the dialog explains this and offers Grade 1 only.

### Step 3 — Set dot geometry

A parameter dialog presents the five dot geometry values as a comma-separated list with UEB standard defaults pre-filled:

```
dotDia, dotSpacing, cellSpacingX, cellSpacingY, dotHeight
1.6,    2.5,        6.1,          10.0,         0.8
```

Edit any value and click OK. The dialog validates your input and re-prompts if any value is invalid. These values are used only for the current run — nothing is written to the Fusion model.

> **Important:** `dotHeight` must be ≤ `dotDia / 2`. A dotHeight equal to dotDia/2 produces a perfect hemisphere — the maximum allowed. Exceeding this causes the fillet to fail.

### Step 4 — Select the construction line

Click the construction line you prepared before running the script. Only sketch lines are selectable at this prompt.

### Step 5 — Select the face

Click the flat face where dots will be placed. The Braille dots will be permanently joined to this face's body.

### Step 6 — Enter text

Type your text. Use `|` to start a new line of Braille.

```
Single line:    Exit only
Multiple lines: Exit only|No entry|Authorised staff
```

The script checks if the text fits the selected face and shows a warning with dimensions if not. You can proceed anyway or re-enter shorter text.

### Step 7 — Done

The script creates all dots, domes them, joins them to the body, and groups the timeline features. A completion message confirms the grade used.

> **Moving dots after placement:** The dot circles in each sketch have no dimensions or constraints tying them together. If you need to reposition a group of dots after the script runs, open the sketch, select all the circles together, and move them as a group. Moving individual circles will break the cell layout.

---

## Dot geometry parameters

All five parameters are presented in the dot geometry dialog at the start of each run. UEB standard ranges are shown for reference.

| Parameter | Default | UEB Standard Range | Description |
|---|---|---|---|
| `dotDia` | 1.6 mm | 1.44–1.60 mm | Dot diameter |
| `dotSpacing` | 2.5 mm | 2.34–2.50 mm | Centre-to-centre distance between dots within a cell. Must be > dotDia to avoid overlap. |
| `cellSpacingX` | 6.1 mm | 6.10–7.60 mm | Horizontal distance between cell origins |
| `cellSpacingY` | 10.0 mm | 10.00–10.16 mm | Vertical distance between line origins |
| `dotHeight` | 0.8 mm | 0.48–0.90 mm | Cylinder height before hemisphere doming. Must be ≤ dotDia/2. |

> Parameters are not saved to the Fusion model. Each run starts fresh from the defaults. Adjust values in the dialog before clicking OK.

---

## Multiple runs on the same surface

You can place multiple independent blocks of Braille on the same surface:

1. Create a new construction line for the next text block — or reposition the original line before running again. Another option is to lay out a grid of construction lines in a single sketch before starting, covering all the positions you need, then select each one in turn for each run.
2. Run the script again and select the new line and the same face.
3. Configure dot geometry, enter text, and proceed as normal.

A position-based profile filter ensures only the current run's dot circles are extruded — all previous Braille groups on the same face are untouched.

---

## Timeline structure

Each run produces one named timeline group. Inside the group, each line of text produces four features:

```
▼ Braille-Hello-G2
    Sketch           ← all dot circles for line 1
    Extrude          ← all dots for line 1 in one feature (one body per dot)
    Combine          ← joins all line 1 dots to the target body
    Fillet           ← domes all line 1 dot tops in one feature
    Sketch           ← all dot circles for line 2 (if multi-line)
    Extrude
    Combine
    Fillet
```

Group names follow the pattern `Braille-{first5chars}-{G1|G2}`.

---

## Troubleshooting

### Grade 2 is unavailable
- Confirm the `louis/` folder exists next to the script.
- Confirm a file matching `liblouis*.dylib` (macOS) or `liblouis*.dll` (Windows) is inside `louis/`.
- Confirm the `tables/` folder containing `en-ueb-g2.ctb` is inside `louis/`.
- macOS: ensure you copied the real versioned `.dylib`, not the symlink.
- macOS: run the `xattr -d` quarantine command shown above.

### Fillet fails / script errors on fillet step
- Confirm `dotHeight` is not greater than `dotDia / 2`. The dialog enforces this but double-check your values.
- The default values (dotDia=1.6, dotHeight=0.8) produce a perfect hemisphere and are guaranteed to work.

### Dots appear in the wrong position
- Use a sketch line on the face as the construction line — not a body edge.
- The start point of the line sets the Braille origin — check its position in the sketch.

### All dots land on the same spot on second run
- Create a new construction line for each run — do not reuse the same line from a previous run.

### Text too large warning
- Use `|` to split text across more lines to reduce the required width.
- Click **Yes** to proceed anyway and trim overhanging dots manually if needed.

---

## Supported characters

| Input | Grade 1 | Grade 2 |
|---|---|---|
| a–z | ✓ | ✓ |
| A–Z (with capital indicator) | ✓ | ✓ |
| 0–9 (with numeric indicator) | ✓ | ✓ |
| Punctuation ( . , ? and more ) | ✓ | ✓ |
| UEB whole-word contractions | — | ✓ |
| UEB part-word contractions | — | ✓ |
| UEB letter contractions | — | ✓ |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

liblouis is licensed under the GNU Lesser General Public License. See [liblouis/COPYING.LESSER](https://github.com/liblouis/liblouis/blob/master/COPYING.LESSER). Braille Maker loads liblouis as an external runtime library and does not incorporate its source code.

---

## Acknowledgements

- [liblouis](https://github.com/liblouis/liblouis) — open-source Braille translator and back-translator used for Grade 2 UEB support.
- [Unified English Braille (UEB)](https://www.iceb.org/ueb.html) — Braille standard maintained by the International Council on English Braille.
