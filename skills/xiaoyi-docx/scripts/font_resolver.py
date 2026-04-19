import os
import platform


def _get_system_font_dirs() -> list:
    """Return list of system font directories for current platform."""
    system = platform.system()
    paths = []

    if system == "Windows":
        paths = [
            os.path.expandvars(r"%WINDIR%\Fonts"),
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts"),
        ]
    elif system == "Darwin":  # macOS
        paths = [
            os.path.expanduser("~/Library/Fonts"),
            "/System/Library/Fonts",
            "/Library/Fonts",
        ]
    else:  # Linux
        paths = [
            os.path.expanduser("~/.local/share/fonts"),
            "/usr/share/fonts",
            "/usr/local/share/fonts",
        ]

    return [p for p in paths if os.path.exists(p)]


_HARMONY_FONTS = {
    "HarmonyHeiTi": {
        "regular": ["Harmony-Regular.ttf", "Harmony-Regular.ttc", "HarmonyHeiTi.ttf"],
        "bold":    ["Harmony-Bold.ttf", "Harmony-Bold.ttc", "HarmonyHeiTi-Bold.ttf"],
    }
}

_CJK_FALLBACKS = [
    ("Noto Sans CJK SC", {"regular": ["NotoSansCJK-Regular.ttc"], "bold": ["NotoSansCJK-Bold.ttc"]}),
    ("WenQuanYi Zen Hei", {"regular": ["wqy-zenhei.ttc"], "bold": ["wqy-zenhei.ttc"]}),
]


def _find_font_file(candidates: list) -> str | None:
    """Search for font file in system font directories."""
    font_dirs = _get_system_font_dirs()
    for font_dir in font_dirs:
        for root, _dirs, files in os.walk(font_dir):
            for filename in files:
                if filename.lower() in [c.lower() for c in candidates]:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in (".ttf", ".ttc", ".otf"):
                        return os.path.join(root, filename)
    return None


def resolve_reportlab_fonts(target_name: str = "HarmonyHeiTi") -> dict | None:
    """Find regular+bold font files for ReportLab registration.

    Returns {"regular": str, "bold": str, "resolved_name": str} or None.
    """
    # 1. Try Harmony fonts first
    harmony = _HARMONY_FONTS.get(target_name)
    if harmony:
        regular_path = _find_font_file(harmony["regular"])
        bold_path = _find_font_file(harmony["bold"])
        if regular_path and bold_path:
            return {"regular": regular_path, "bold": bold_path, "resolved_name": target_name}

    # 2. Fallback to system CJK fonts
    for fallback_name, variants in _CJK_FALLBACKS:
        regular_path = _find_font_file(variants["regular"])
        bold_path = _find_font_file(variants["bold"])
        if regular_path and bold_path:
            return {"regular": regular_path, "bold": bold_path, "resolved_name": fallback_name}

    return None


def get_css_font_stack(primary: str = "HarmonyHeiTi") -> str:
    """Return CSS font-family string with CJK fallbacks."""
    fallbacks = [
        primary,
        '"Noto Sans CJK SC"',
        '"WenQuanYi Zen Hei"',
        '"Helvetica Neue"',
        "Helvetica",
        "Arial",
        "sans-serif",
    ]
    return ", ".join(fallbacks)
