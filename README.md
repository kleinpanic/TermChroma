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
- **Save to a File**: Use `-o/--save <file>` to write ASCII output (with color codes) to disk.
- **256-Color Table**: `--random-colors` displays a color swatch chart.

## Dependencies

- **Python 3.6+**
- [**Pillow**](https://pypi.org/project/Pillow/) for image processing  

```bash
pip install Pillow
```

## Installation

1. Clone or download this repository.
2. Place `termchroma.py` in a directory within your `$PATH`, or just run it locally.
3. Ensure you have Python 3 and Pillow installed.

## Usage

termchroma.py [OPTIONS] [IMAGE]


**Key Options**:

- `-o, --save <FILE>`  
  Save the ASCII art to `FILE` (including ANSI color if any).
- `--scale <FLOAT>`  
  Initial scale factor (default `0.5`).
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

1. **Basic TUI**:
   ```bash
   termchroma.py myphoto.jpg
```
    No TUI:

termchroma.py myphoto.jpg --no-tui --gradient rainbow

Saving to file:

termchroma.py myphoto.jpg --no-tui --scale 0.4 --gradient rainbow --save out.txt

Show 256-color table:

    termchroma.py --random-colors

License

MIT License (or whichever license you prefer). See LICENSE file for details.
Contributing

    Fork the repo and create your branch from main.
    Make changes or add new features.
    Submit a pull request.

Author

    You (or your organization)

Enjoy TermChroma for your ASCII art needs!


---

