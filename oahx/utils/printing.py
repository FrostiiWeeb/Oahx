from __future__ import annotations

from typing import Tuple

try:
    import colorama

    colorama.init()
except ImportError:
    pass

ColorT = Tuple[int, int]

PREFIX = "\u001b["
SUFFIX = "m"


class Colors:
    BLACK: ColorT = (30, 40)
    RED: ColorT = (31, 41)
    GREEN: ColorT = (32, 42)
    YELLOW: ColorT = (33, 43)
    BLUE: ColorT = (34, 44)
    MAGENTA: ColorT = (35, 45)
    CYAN: ColorT = (36, 46)
    WHITE: ColorT = (37, 47)


RESET = PREFIX + "0" + SUFFIX


def format_cint(num: int, bright: bool = False) -> str:
    return PREFIX + str(num) + (";1" if bright else "") + SUFFIX


def format_cint_with_name(cname: str, indx: int, bright: bool = False) -> str:
    cint = getattr(Colors, cname.upper())[indx]
    return format_cint(cint, bright)


def startswith_bright(text: str) -> Tuple[bool, str]:
    text = text.upper()
    if text[:2] == "B_":
        return (True, text[2:])
    else:
        return (False, text)


def creturn(
    text: str, foreground: str | None = None, background: str | None = None
) -> str:
    fg, bg = RESET, RESET
    if foreground:
        fb, fg = startswith_bright(foreground)
        fg = format_cint_with_name(fg, 0, fb)
    if background:
        bb, bg = startswith_bright(background)
        bg = format_cint_with_name(bg, 1, bb)
    return f"{bg}{fg}{text}{RESET}"


def cprint(
    text: str, foreground: str | None = None, background: str | None = None
) -> None:
    print(creturn(text, foreground, background))


def tprint(
    talker: str,
    text: str,
    talker_fg: str | None = None,
    talker_bg: str | None = None,
    text_fg: str | None = None,
    text_bg: str | None = None,
) -> None:
    talker = creturn(f"[{talker}]:", talker_fg, talker_bg)
    text = creturn(text, text_fg, text_bg)
    print(f"{talker} {text}")


def bot(text: str, **kwargs):
    tprint("BOT", text, **kwargs)


def launcher(text: str, talker_color: str | None = None, text_color: str | None = None):
    tprint("LAUNCHER", text, text_fg=text_color, talker_fg=talker_color)


def cog(text: str, talker_color: str | None = None, text_color: str | None = None):
    tprint("COG", text, text_fg=text_color, talker_fg=talker_color)
