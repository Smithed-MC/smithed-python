from rich.console import Console
from rich.theme import Theme


def _brand():
    blue = accent = "#1B48C4"
    accent_light = "#23A3FF"
    locals()["bar.pulse"] = secondary = "#C41B9C"
    locals()["rule.line"] = green = success = "#1BC443"
    red = error = "#C41B1B"
    yellow = warning = "#E8AA03"

    white = foreground = "#FFF8F0"
    light_gray = border = "#4B4B4B"
    gray = highlight = "#2E2E31"
    dark_gray = section = "#1D1F21"
    background = "#121213"
    black = "#000000"

    return locals()


console = Console(theme=Theme(_brand()))
print = console.print
