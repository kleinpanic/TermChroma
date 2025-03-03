#!/usr/bin/env python3
import sys
import argparse
import curses
import math
import os

__version__ = "1.1.0"

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow (PIL) library not installed. Install via:")
    print("  pip install Pillow")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 1) Pre-defined ASCII character sets
# ---------------------------------------------------------------------------
CHAR_SETS = [
    " .:-=+*#%@",
    " .'`,^:\";!i~+_-?][}{1)(|\\lI<>rctvxyzuJCOAs238&%$W#@",
    "@%#*+=-:. ",
    " .oO@ "
]

# ---------------------------------------------------------------------------
# 2) Color gradients / modes
# ---------------------------------------------------------------------------

# 2a) "Kleinpanic" rainbow
KLEINPANIC_RAINBOW = [203, 198, 199, 164, 129, 93, 63, 33, 39, 44]

# 2b) A “blue to red” gradient example
def build_blue2red_gradient(steps=24):
    """
    Build a list of 256-color codes that smoothly transitions from a blue code to a red code.
    This is just a naive example; you can define more elaborate gradients if you like.
    """
    gradient = []
    blue_code = 21   # bright blue
    red_code = 196   # bright red
    for i in range(steps):
        frac = i / float(steps - 1)
        code = int(blue_code + frac * (red_code - blue_code))
        code = max(0, min(255, code))
        gradient.append(code)
    return gradient

BLUE2RED_GRADIENT = build_blue2red_gradient(24)

# 2c) The recognized modes
COLOR_MODES = [
    "none",
    "grayscale",
    "rainbow",
    "blue2red",
    "custom"
]

def grayscale_256_shade(pixel_value):
    """Map 0..255 -> 256 grayscale color codes (232..255)."""
    index = int((pixel_value / 255.0) * 23)
    return 232 + index

# ---------------------------------------------------------------------------
# 3) Utilities for computing final scale so the ASCII fits the terminal
# ---------------------------------------------------------------------------

def compute_ascii_size(original_w, original_h, user_scale):
    """
    Return (ascii_w, ascii_h) after scaling the original image to user_scale,
    factoring in the ~0.55 vertical compression for ASCII aspect ratio.
    """
    new_w = int(original_w * user_scale)
    new_h = int(original_h * user_scale * 0.55)
    # clamp
    if new_w < 1: new_w = 1
    if new_h < 1: new_h = 1
    return new_w, new_h

def fit_scale_to_terminal(original_w, original_h, current_scale, term_w, term_h, instruction_lines=1):
    """
    Ensure the ASCII art (after scaling) does not exceed the terminal dimensions.
    - term_w = width in columns
    - term_h = height in rows
    - instruction_lines: how many lines we reserve for instructions, etc.

    We compute new_w, new_h for the user’s desired scale.
    If it’s too big to fit (width > term_w or height > term_h-instruction_lines),
    we reduce the scale proportionally.

    Returns a possibly adjusted scale so it fits.
    """
    ascii_w, ascii_h = compute_ascii_size(original_w, original_h, current_scale)

    # How many lines do we have for the art?
    available_rows = term_h - instruction_lines
    if available_rows < 1:
        available_rows = 1

    # If ascii_w or ascii_h are bigger than the available space, we shrink
    # We'll find the factor needed in each dimension, then pick the smaller to ensure fit.
    factor_w = 1.0
    factor_h = 1.0

    if ascii_w > term_w:
        factor_w = term_w / float(ascii_w)
    if ascii_h > available_rows:
        factor_h = available_rows / float(ascii_h)

    factor = min(factor_w, factor_h)

    if factor < 1.0:
        current_scale = current_scale * factor

    # Also if scale < some minimal threshold, we clamp so it doesn’t go to zero.
    if current_scale < 0.01:
        current_scale = 0.01

    return current_scale

# ---------------------------------------------------------------------------
# 4) Convert an image to ASCII lines (with optional color)
# ---------------------------------------------------------------------------

def image_to_ascii(
    img,
    char_set,
    scale,
    color_mode,
    term_w=None,
    term_h=None,
    resize_filter=Image.LANCZOS
):
    """
    1) We have an open PIL image (img).
    2) We'll possibly adjust scale so it fits term_w x term_h (if both are given).
    3) Convert each pixel to ASCII with optional color.
    4) Return a list of lines.
    """
    original_w, original_h = img.size

    # If terminal size is known, fit the scale so it doesn't overflow
    if term_w is not None and term_h is not None:
        scale = fit_scale_to_terminal(original_w, original_h, scale, term_w, term_h, instruction_lines=1)

    # Now compute final size
    new_w, new_h = compute_ascii_size(original_w, original_h, scale)

    # Resize the image
    resized = img.resize((new_w, new_h), resize_filter)

    # Generate ASCII lines
    ascii_lines = []
    color_index = 0  # for rainbow, etc.

    for y in range(new_h):
        row_chars = []
        for x in range(new_w):
            r, g, b = resized.getpixel((x, y))
            gray = int(0.299*r + 0.587*g + 0.114*b)
            idx = int((gray / 255.0) * (len(char_set) - 1))
            ascii_char = char_set[idx]

            if color_mode == "none":
                row_chars.append(ascii_char)
            elif color_mode == "grayscale":
                cc = grayscale_256_shade(gray)
                row_chars.append(f"\x1b[38;5;{cc}m{ascii_char}\x1b[0m")
            elif color_mode == "rainbow":
                c = KLEINPANIC_RAINBOW[color_index % len(KLEINPANIC_RAINBOW)]
                row_chars.append(f"\x1b[1;38;5;{c}m{ascii_char}\x1b[0m")
                color_index += 1
            elif color_mode == "blue2red":
                c = BLUE2RED_GRADIENT[color_index % len(BLUE2RED_GRADIENT)]
                row_chars.append(f"\x1b[1;38;5;{c}m{ascii_char}\x1b[0m")
                color_index += 1
            elif color_mode == "custom":
                top = max(r, g, b)
                if top == 0:
                    color_code = 16
                else:
                    if top == r:   color_code = 196
                    elif top == g: color_code = 46
                    else:          color_code = 21
                row_chars.append(f"\x1b[1;38;5;{color_code}m{ascii_char}\x1b[0m")

        ascii_lines.append("".join(row_chars))

    return ascii_lines, scale

# ---------------------------------------------------------------------------
# 5) Show a 256-color table, plus a sample ASCII char for each
# ---------------------------------------------------------------------------

def display_ansi_color_table():
    print("256-color ANSI escape codes demonstration:\n")
    ascii_chars = (
        " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
    )
    idx_char = 0
    for c in range(256):
        ch = ascii_chars[idx_char % len(ascii_chars)]
        idx_char += 1
        sys.stdout.write(f"\x1b[38;5;{c}m {c:3d}({ch}) \x1b[0m")
        if (c + 1) % 8 == 0:
            sys.stdout.write("\n")
    print("\n\x1b[0m")

# ---------------------------------------------------------------------------
# 6) A TUI that uses curses only for keys, and prints ANSI color
# ---------------------------------------------------------------------------

def tui_main(stdscr, args, pil_img):
    curses.curs_set(0)  
    stdscr.nodelay(True)  # we can do non-blocking getch

    scale = args.scale
    char_set_idx = 0
    color_mode_idx = 0
    resize_filter = parse_resize_filter(args.resize_filter)

    # We'll store the current ascii lines and an *actual* scale used (if it was clamped)
    ascii_lines, actual_scale = image_to_ascii(
        pil_img, CHAR_SETS[char_set_idx], scale, "none"
    )

    def redraw():
        """
        Redraw the screen (instructions + the ASCII art).
        We do a fresh conversion so that the ASCII definitely fits in the
        current terminal size.
        """
        nonlocal ascii_lines, actual_scale, scale

        # 1) Get current terminal size from curses
        term_h, term_w = stdscr.getmaxyx()

        # 2) Convert image to ASCII (with color) that fits term size
        lines, new_scale = image_to_ascii(
            pil_img,
            CHAR_SETS[char_set_idx],
            scale,
            COLOR_MODES[color_mode_idx],
            term_w=term_w,
            term_h=term_h,
            resize_filter=resize_filter
        )
        ascii_lines = lines
        actual_scale = new_scale

        # 3) Clear the screen via ANSI
        sys.stdout.write("\x1b[2J\x1b[H")

        # 4) Print instructions on top
        instructions = (
            f"[TUI Mode]  Scale={actual_scale:.2f}  |  CharSet={char_set_idx}  "
            f"|  ColorMode={COLOR_MODES[color_mode_idx]}  "
            f"|  (Arrows=Adjust, C=Colors, Q=Quit)\n"
        )
        print(instructions)

        # 5) Print each line of ASCII
        for line in ascii_lines:
            print(line)

        sys.stdout.flush()

    # Initial draw
    redraw()

    while True:
        c = stdscr.getch()
        if c == -1:
            continue  # no key pressed
        if c in (ord('q'), ord('Q')):
            break
        elif c == curses.KEY_UP:
            scale += 0.05
            redraw()
        elif c == curses.KEY_DOWN:
            scale -= 0.05
            if scale < 0.01:
                scale = 0.01
            redraw()
        elif c == curses.KEY_LEFT:
            char_set_idx = (char_set_idx - 1) % len(CHAR_SETS)
            redraw()
        elif c == curses.KEY_RIGHT:
            char_set_idx = (char_set_idx + 1) % len(CHAR_SETS)
            redraw()
        elif c in (ord('c'), ord('C')):
            color_mode_idx = (color_mode_idx + 1) % len(COLOR_MODES)
            redraw()
        # ignore all other keys

def parse_resize_filter(filter_str):
    """
    Map user-provided string to a Pillow resize filter constant.
    """
    if not filter_str:
        return Image.LANCZOS
    f = filter_str.lower()
    if f == "nearest":
        return Image.NEAREST
    elif f == "bilinear":
        return Image.BILINEAR
    elif f == "bicubic":
        return Image.BICUBIC
    elif f == "lanczos":
        return Image.LANCZOS
    else:
        print(f"Warning: unknown --resize-filter '{filter_str}', using lanczos.")
        return Image.LANCZOS

# ---------------------------------------------------------------------------
# 7) Main CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="ASCII Art Converter — with TUI, color, and file saving.\n"
                    "Examples:\n"
                    "  ascii_art.py myphoto.jpg\n"
                    "  ascii_art.py --random-colors\n",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("image", nargs="?",
                        help="Path to an input image (jpg/png/gif, etc.).")

    parser.add_argument("-o", "--save",
                        help="Write the resulting ASCII art (with ANSI colors) to a text file.")

    parser.add_argument("--scale", type=float, default=0.5,
                        help="Initial scaling factor (default=0.5).")

    parser.add_argument("--chars", type=str, default=None,
                        help="Custom ASCII characters (overrides CHAR_SETS[0]).")

    parser.add_argument("--gradient", type=str, default=None, choices=COLOR_MODES,
                        help="Color mode: none/grayscale/rainbow/blue2red/custom")

    parser.add_argument("--no-tui", action="store_true",
                        help="Disable TUI; just convert once and print/save ASCII.")

    parser.add_argument("--random-colors", action="store_true",
                        help="Show a 256-color table (plus sample ASCII), then exit.")

    parser.add_argument("--resize-filter", type=str, default="lanczos",
                        help="Resize filter: nearest/bilinear/bicubic/lanczos (default lanczos).")

    parser.add_argument("-v", "--version", action="store_true",
                        help="Show version info and exit.")

    args = parser.parse_args()

    # --version
    if args.version:
        print(f"ascii_art.py version {__version__}")
        sys.exit(0)

    # --random-colors
    if args.random_colors:
        display_ansi_color_table()
        sys.exit(0)

    # If user didn't provide an image, print help
    if not args.image:
        parser.print_help()
        sys.exit(1)

    if not os.path.exists(args.image):
        print(f"ERROR: Image file not found: {args.image}")
        sys.exit(1)

    # Possibly override the first CHAR_SETS entry with user-provided
    if args.chars is not None:
        CHAR_SETS[0] = args.chars

    # Open the image once, in color
    try:
        pil_img = Image.open(args.image)
        pil_img = pil_img.convert("RGB")
    except Exception as e:
        print(f"ERROR: could not open image '{args.image}': {e}")
        sys.exit(1)

    # Decide color mode from --gradient
    color_mode = "none"
    if args.gradient:
        color_mode = args.gradient

    # If user says --no-tui, just do a single pass
    if args.no_tui:
        resize_filter = parse_resize_filter(args.resize_filter)
        # We'll do a single pass of image_to_ascii
        # We don't know the user's terminal size here, but let's at least
        # see if we can read it from os.get_terminal_size (not always reliable).
        term_size = None
        try:
            term_size = os.get_terminal_size()
        except:
            pass

        if term_size:
            term_w = term_size.columns
            term_h = term_size.lines
        else:
            # fallback to something
            term_w, term_h = (80, 24)

        lines, _actual_scale = image_to_ascii(
            pil_img,
            CHAR_SETS[0],
            args.scale,
            color_mode,
            term_w=term_w,
            term_h=term_h,
            resize_filter=resize_filter
        )

        # Save or print
        if args.save:
            try:
                with open(args.save, "w", encoding="utf-8") as f:
                    for ln in lines:
                        f.write(ln + "\n")
                print(f"Saved ASCII art to: {args.save}")
            except Exception as e:
                print(f"ERROR: Could not save file '{args.save}': {e}")
        else:
            for ln in lines:
                print(ln)
        sys.exit(0)

    # Otherwise, we run the TUI
    # We'll wrap in curses.wrapper
    try:
        curses.wrapper(tui_main, args, pil_img)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()

