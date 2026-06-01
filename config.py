import tkinter.font as tkfont


APP_TITLE = "SENTINEL"
WINDOW_GEOMETRY = "1240x780"
MIN_WINDOW_SIZE = (1050, 680)

COLORS = {
    "app_bg": "#F5F5F7",
    "card": "#FFFFFF",
    "text": "#1D1D1F",
    "muted": "#6E6E73",
    "line": "#E5E5EA",
    "sidebar": "#FFFFFF",
    "accent": "#007AFF",
    "accent_dark": "#005FCC",
    "green": "#34C759",
    "red": "#FF3B30",
    "orange": "#FF9500",
    "soft_blue": "#EAF3FF",
    "soft_red": "#FFF0EF",
    "input": "#F9F9FB",
}


def get_apple_like_font():
    available_fonts = list(tkfont.families())

    preferred_fonts = [
        "SF Pro Display",
        "SF Pro Text",
        "Segoe UI Variable",
        "Segoe UI",
        "Helvetica Neue",
        "Arial",
    ]

    for font in preferred_fonts:
        if font in available_fonts:
            return font

    return "Arial"