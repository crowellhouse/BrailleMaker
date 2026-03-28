# BrailleMaker for Autodesk Fusion 360

A Fusion 360 Python script that automatically generates raised UEB Braille dots on any flat surface of a 3D model. Select a grade, pick a construction line and face, type your text, and the script extrudes precision domed dot cylinders ready for 3D printing or CNC machining.

-----

## Features

- **Grade 1 and Grade 2 UEB** — Grade 1 is letter-for-letter and works out of the box. Grade 2 uses full UEB contractions (180+) via the bundled liblouis library with no pip install required.
- **Any flat surface** — works on XY, YZ, XZ, and arbitrarily angled faces. Dots always extrude outward from the selected face regardless of orientation.
- **Multi-line text** — use the `|` character to place multiple lines of Braille in a single run.
- **Multiple independent runs** — run the script as many times as needed on the same surface. Each run is fully isolated; previous dots are never re-extruded or re-filleted.
- **Domed dots** — each dot cylinder receives a hemisphere fillet matching the UEB standard profile for tactile readability.
- **Parametric dimensions** — all dot and spacing values are stored as Fusion 360 user parameters (`dotDia`, `dotSpacing`, `cellSpacingX`, `cellSpacingY`, `dotHeight`) and can be edited at any time.
- **Clean timeline** — all features for each run are grouped under a named timeline group (`Braille-XXXXX-G1` or `Braille-XXXXX-G2`). One extrude per line of text keeps the timeline lean.
- **Surface size check** — warns if the entered text exceeds the face bounds, with the option to proceed or re-enter.
- **Capital and number indicators** — UEB capital and numeric mode indicators are applied automatically.
- **macOS and Windows** — auto-detects platform and loads the correct liblouis binary.

-----

## How it works

### Overview

```
Run script → Choose grade → Select construction line → Select face → Enter text → Braille created
```

1. The script reads five Fusion user parameters for dot dimensions.
1. The opening dialog lets you choose Grade 1 or Grade 2 and explains the steps.
1. You select a construction line — its start point becomes the top-left origin of the first Braille cell.
1. You select the flat face where dots will be placed.
1. The script translates your text into UEB dot patterns (Grade 1 via built-in map, Grade 2 via liblouis).
1. For each line of text one sketch is created on the face containing all the dot circles for that line.
1. A position-based profile filter selects only the newly placed circles, ignoring any circles from previous runs.
1. All circles in each sketch are extruded together as a single multi-profile feature.
1. All dot bodies are joined to the target body in one combine operation.
1. Top edges of all dot cylinders are identified by projecting onto the face normal and filleted in one operation.
1. All features are grouped in the timeline under a named group.

### Dot cell layout

Each Braille character occupies a cell with up to 6 dots arranged in a 2×3 grid following the UEB standard:

```
Dot 1 · Dot 4
Dot 2 · Dot 5
Dot 3 · Dot 6
```

### Grade 1 vs Grade 2

|                 |Grade 1                          |Grade 2                   |
|-----------------|---------------------------------|--------------------------|
|Translation      |Letter-for-letter                |UEB contractions          |
|“the”            |3 cells (t, h, e)                |1 cell (dots 2,3,4,6)     |
|Contractions     |None                             |180+ via liblouis         |
|Requires liblouis|No                               |Yes                       |
|Best for         |Part numbers, codes, short labels|Running text, instructions|

-----

## Requirements

- Autodesk Fusion 360 (any recent version)
- Python — bundled with Fusion 360, no separate install needed
- liblouis — optional, required for Grade 2 only (see [Grade 2 Setup](#grade-2-setup))

-----

## Installation

### 1. Add the script to Fusion 360

1. Download or clone this repository.
1. In Fusion 360 go to **Utilities → Scripts and Add-ins** (or press `Shift+S`).
1. Click the **+** button next to **My Scripts**.
1. Navigate to and select the `BrailleMaker_v2` folder.
1. The script will appear in the My Scripts list.

**Default script locations:**

|Platform|Path                                                                        |
|--------|----------------------------------------------------------------------------|
|macOS   |`~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/Scripts`    |
|Windows |`C:\Users\YourName\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\Scripts`|

### 2. Grade 2 Setup

Grade 2 requires liblouis to be placed in a `louis/` subfolder next to the script file.

#### Required folder layout

```
BrailleMaker_v2/
├── BrailleMaker_v2.py
└── louis/
    ├── liblouis.dll          ← Windows
    ├── liblouis.dylib        ← macOS
    └── tables/
        ├── en-ueb-g2.ctb
        ├── en-ueb-g1.ctb
        ├── en-ueb-chardefs.uti
        ├── unicode.dis
        └── ... (all other table files)
```

#### macOS

```bash
# Install liblouis
brew install liblouis

# Find the real versioned dylib (not the symlink)
ls -la /opt/homebrew/lib/liblouis*.dylib

# Copy the versioned file into the louis/ folder
cp /opt/homebrew/lib/liblouis.20.0.0.dylib \
    "/path/to/BrailleMaker_v2/louis/liblouis.dylib"

# Copy the tables folder
cp -r /opt/homebrew/share/liblouis/tables \
    "/path/to/BrailleMaker_v2/louis/tables"

# Clear quarantine flag
xattr -d com.apple.quarantine \
    "/path/to/BrailleMaker_v2/louis/liblouis.dylib"
```

> **Note:** Copy the real versioned `.dylib` file — not the symlink. The version number in the filename will vary depending on what Homebrew installed.

#### Windows

1. Download the latest release zip from [github.com/liblouis/liblouis/releases](https://github.com/liblouis/liblouis/releases) — look for `liblouis-X.X.X-win64.zip`.
1. Create a `louis\` folder inside `BrailleMaker_v2\`.
1. Copy `liblouis.dll` from the zip’s `bin\` folder into `louis\`.
1. Copy the entire `tables\` folder from the zip into `louis\`.

-----

## Usage

### Step 1 — Prepare your model

Create a **construction line** on the face where you want Braille. The line’s start point becomes the top-left origin of the first Braille cell. The line length does not matter — only the start point is used.

### Step 2 — Run the script

Go to **Utilities → Scripts and Add-ins**, select **BrailleMaker_v2**, and click **Run**.

### Step 3 — Choose a grade

An input dialog opens with instructions. Type `1` for Grade 1 or `2` for Grade 2 and click OK. Cancel exits without making any changes.

> If liblouis is not found, the dialog explains this and offers Grade 1 only.

### Step 4 — Select entities

- Click the **construction line** when prompted.
- Click the **flat face** when prompted.

### Step 5 — Enter text

Type your text in the input dialog. Use `|` to create a new line of Braille.

```
Example single line:   Exit only
Example multi-line:    Exit only|No entry|Authorised staff
```

### Step 6 — Done

The script creates all dots, domes them, joins them to the body, and groups the timeline features. A completion message confirms the grade used.

-----

## User parameters

All dot dimensions are stored as Fusion 360 user parameters and can be changed at any time via **Modify → Change Parameters**.

|Parameter     |Default|Description                                         |
|--------------|-------|----------------------------------------------------|
|`dotDia`      |1.5 mm |Dot diameter                                        |
|`dotSpacing`  |2.5 mm |Centre-to-centre distance between dots within a cell|
|`cellSpacingX`|6.5 mm |Horizontal distance between cell origins            |
|`cellSpacingY`|10 mm  |Vertical distance between line origins              |
|`dotHeight`   |0.7 mm |Cylinder height before hemisphere doming            |


> Parameters are created on first run and never overwritten by subsequent runs.

-----

## Multiple runs on the same surface

You can place multiple independent blocks of Braille on the same surface:

1. Create a new construction line for the next text block.
1. Run the script again and select the new line and the same face.
1. Enter the new text.

Each run produces its own named timeline group. A position-based profile filter ensures only the current run’s circles are extruded — all previous dots are untouched.

-----

## Timeline structure

Each run produces the following timeline features, all grouped together:

```
▼ Braille-Hello-G2
    Sketch (origin)
    Extrude 1        ← all dots for line 1 in one feature
    Extrude 2        ← all dots for line 2 (if multi-line)
    Combine
    Fillet
```

Group names follow the pattern `Braille-{first5chars}-{G1|G2}`.

-----

## Troubleshooting

### Grade 2 is unavailable

- Confirm the `louis/` folder exists next to the script.
- Confirm `liblouis.dylib` (macOS) or `liblouis.dll` (Windows) is inside `louis/`.
- Confirm the `tables/` folder with `en-ueb-g2.ctb` is inside `louis/`.
- macOS: ensure you copied the real versioned `.dylib`, not the symlink.
- macOS: run the `xattr -d` quarantine command shown above.

### Dots appear in the wrong position

- Use a sketch line on the face as the construction line — not a body edge.
- The start point of the line sets the Braille origin — check its position in the sketch.

### Text too large warning

- Use `|` to split text across more lines to reduce the required width.
- Click **Yes** to proceed anyway and trim overhanging dots manually if needed.

-----

## Supported characters

|Input                       |Grade 1|Grade 2|
|----------------------------|-------|-------|
|a–z                         |✓      |✓      |
|A–Z (with capital indicator)|✓      |✓      |
|0–9 (with numeric indicator)|✓      |✓      |
|Punctuation ( . , ? )       |✓      |✓      |
|UEB whole-word contractions |—      |✓      |
|UEB part-word contractions  |—      |✓      |
|UEB letter contractions     |—      |✓      |

-----

## License

This project is open source. See <LICENSE> for details.

liblouis is licensed under the GNU Lesser General Public License. See [liblouis/COPYING.LESSER](https://github.com/liblouis/liblouis/blob/master/COPYING.LESSER).

-----

## Acknowledgements

- [liblouis](https://github.com/liblouis/liblouis) — open-source Braille translator used for Grade 2 UEB support.
- [Unified English Braille (UEB)](https://www.iceb.org/ueb.html) — Braille standard maintained by the International Council on English Braille.
