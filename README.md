# TermChroma

**TermChroma** is a powerful command-line utility for converting images into ASCII art, complete with an interactive TUI, multiple color gradients, and the ability to save the output (including ANSI color escape codes) to a file.

- **Version:** 1.1.0
- **License:** MIT (or your choice)

## Features

- **Multiple ASCII Sets**: Choose from built-in sets or define your own with `--chars`.
- **Multiple Color Modes**: None, grayscale, rainbow, blue2red, or custom color mapping.
- **Interactive TUI**:  
  - Resize your ASCII art on the fly.  
  - Change character sets with arrow keys.  
  - Toggle color modes with `C`.  
  - Press `Q` to quit.  
  - Art is always scaled to fit the terminal window, so it never overflows.
- **Single-shot Conversion**: Use `--no-tui` to simply convert and print or save the ASCII art.
- **Save to a File**: Use `-o/--save <file>` to write ASCII output (with color codes) to disk (implies `--no-tui`).
- **256-Color Table**: `--random-colors` displays a color swatch chart.

## Dependencies

- **Python 3.11+** (required by the pinned Pillow version)
- [**Pillow**](https://pypi.org/project/Pillow/) for image processing  

```bash
pip install -r requirements.txt
```

## Installation

1. Clone or download this repository.
2. Install the dependencies: `pip install -r requirements.txt`.
3. Run `python3 ascii_art.py` from the repository, or copy `ascii_art.py` into a
   directory on your `$PATH` (e.g. as `termchroma`) and `chmod +x` it.

## Usage

```bash
python3 ascii_art.py [OPTIONS] [IMAGE]
```


**Key Options**:

- `-o, --save <FILE>`  
  Save the ASCII art to `FILE` (including ANSI color if any). Implies `--no-tui`.
- `--scale <FLOAT>`  
  Initial scale factor, must be > 0 (default `0.5`).
- `--chars <STRING>`  
  Override the default ASCII characters for brightness mapping.
- `--gradient {none,grayscale,rainbow,blue2red,custom}`  
  Pick a color mode. 
- `--no-tui`  
  Disable interactive TUI; convert once and print/save ASCII art.
- `--random-colors`  
  Display a 256‐color demonstration table, then exit.
- `--resize-filter {nearest,bilinear,bicubic,lanczos}`  
  Pillow resize method (default `lanczos`).
- `-v, --version`  
  Print version and exit.
- `-h, --help`  
  Show help message and exit.

### Interactive TUI Controls

- **Up/Down**: Increase/decrease scale.
- **Left/Right**: Cycle through different ASCII character sets.
- **C** (or `c`): Cycle color modes.
- **Q** (or `q`): Quit TUI.

### Examples

#### Basic TUI:

```bash
python3 ascii_art.py myphoto.jpg
```

#### No TUI:

```bash
python3 ascii_art.py myphoto.jpg --no-tui --gradient rainbow
```

#### Saving to file:

```bash
python3 ascii_art.py myphoto.jpg --scale 0.4 --gradient rainbow --save out.txt
```

#### Show 256-color table:

```bash
python3 ascii_art.py --random-colors
```

## Development

```bash
pip install -r requirements-dev.txt
ruff check .
mypy ascii_art.py
pytest
```

CI (`.github/workflows/ci.yml`) runs the same steps on every push and pull request.

## License

MIT License (or whichever license you prefer). See LICENSE file for details.
Contributing

    Fork the repo and create your branch from main.
    Make changes or add new features.
    Submit a pull request.

Author

    Kleinpanic

Enjoy TermChroma for your ASCII art needs!


---

