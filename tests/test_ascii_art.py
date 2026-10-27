import curses
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image

import ascii_art

SCRIPT = Path(__file__).resolve().parent.parent / "ascii_art.py"


@pytest.fixture
def png(tmp_path):
    path = tmp_path / "img.png"
    Image.new("RGB", (40, 40), (200, 10, 10)).save(path)
    return path


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, stdin=subprocess.DEVNULL,
    )


# --- CLI input validation -------------------------------------------------

def test_empty_chars_is_rejected(png):
    res = run_cli(str(png), "--no-tui", "--chars", "")
    assert res.returncode == 2
    assert "Traceback" not in res.stderr
    assert "--chars" in res.stderr


@pytest.mark.parametrize("scale", ["inf", "nan", "0", "-1", "abc"])
def test_bad_scale_is_rejected(png, scale):
    res = run_cli(str(png), "--no-tui", "--scale", scale)
    assert res.returncode == 2
    assert "Traceback" not in res.stderr
    assert "--scale" in res.stderr


def test_unknown_resize_filter_is_rejected(png):
    res = run_cli(str(png), "--no-tui", "--resize-filter", "bogus")
    assert res.returncode == 2
    assert "--resize-filter" in res.stderr


def test_resize_filter_is_case_insensitive(png):
    res = run_cli(str(png), "--no-tui", "--resize-filter", "NEAREST")
    assert res.returncode == 0, res.stderr


# --- saving -----------------------------------------------------------------

def test_save_failure_exits_nonzero(png, tmp_path):
    res = run_cli(str(png), "--no-tui", "-o", str(tmp_path / "missing" / "out.txt"))
    assert res.returncode == 1
    assert "Could not save" in res.stderr


def test_save_without_no_tui_writes_file(png, tmp_path):
    # Previously --save was silently ignored unless --no-tui was also given
    # (and the TUI needs a real terminal, so this would fail outright).
    out = tmp_path / "out.txt"
    res = run_cli(str(png), "--gradient", "rainbow", "-o", str(out))
    assert res.returncode == 0, res.stderr
    assert "\x1b[" in out.read_text(encoding="utf-8")


# --- TUI ----------------------------------------------------------------------

class FakeScreen:
    def __init__(self, keys, size=(24, 80)):
        self.keys = list(keys)
        self.size = size
        self.nodelay_calls = []

    def nodelay(self, flag):
        self.nodelay_calls.append(flag)

    def getmaxyx(self):
        return self.size

    def getch(self):
        return self.keys.pop(0)


def run_tui(monkeypatch, capsys, keys, size=(24, 80), img_size=(400, 400), **arg_overrides):
    monkeypatch.setattr(curses, "curs_set", lambda _: None, raising=False)
    args = SimpleNamespace(scale=0.5, resize_filter="lanczos", gradient=None)
    vars(args).update(arg_overrides)
    screen = FakeScreen(keys, size)
    img = Image.new("RGB", img_size, (128, 128, 128))
    ascii_art.tui_main(screen, args, img)
    frames = capsys.readouterr().out.split("\x1b[2J\x1b[H")[1:]
    return screen, frames


def test_tui_blocks_on_input_instead_of_busy_polling(monkeypatch, capsys):
    screen, _ = run_tui(monkeypatch, capsys, [ord("q")])
    assert True not in screen.nodelay_calls


def test_tui_honours_gradient_flag(monkeypatch, capsys):
    _, frames = run_tui(monkeypatch, capsys, [ord("q")], gradient="rainbow")
    assert "ColorMode=rainbow" in frames[0]
    assert "\x1b[1;38;5;" in frames[0]


def test_tui_frame_fits_terminal(monkeypatch, capsys):
    rows, cols = 10, 40
    _, frames = run_tui(monkeypatch, capsys, [ord("q")], size=(rows, cols))
    lines = frames[0].split("\n")
    # Every newline moves down a row; rows+1 lines would scroll the header away.
    assert len(lines) <= rows
    assert len(lines[0]) < cols  # header does not wrap


def test_tui_redraws_on_resize(monkeypatch, capsys):
    _, frames = run_tui(monkeypatch, capsys, [curses.KEY_RESIZE, ord("q")])
    assert len(frames) == 2


def test_tui_scale_does_not_drift_past_terminal_limit(monkeypatch, capsys):
    # Image is already clamped to the terminal; pressing Up then Down should
    # visibly shrink it instead of only cancelling the unseen extra Up.
    keys = [curses.KEY_UP] * 5 + [curses.KEY_DOWN, ord("q")]
    _, frames = run_tui(monkeypatch, capsys, keys)
    assert frames[-1].count("\n") < frames[0].count("\n")
