import platform
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from font_resolver import _get_system_font_dirs


def test_get_system_font_dirs_returns_existing_paths():
    dirs = _get_system_font_dirs()
    assert isinstance(dirs, list)
    for d in dirs:
        assert os.path.exists(d), f"Font dir should exist: {d}"


def test_get_system_font_dirs_matches_platform():
    dirs = _get_system_font_dirs()
    system = platform.system()
    if system == "Windows":
        assert any("Windows" in d or "Fonts" in d for d in dirs)
    elif system == "Darwin":
        assert any("Library/Fonts" in d for d in dirs)
    else:
        assert any("usr/share/fonts" in d for d in dirs)


from font_resolver import resolve_reportlab_fonts


def test_resolve_reportlab_fonts_finds_fallback_on_windows():
    if platform.system() != "Windows":
        return
    result = resolve_reportlab_fonts("HarmonyHeiTi")
    assert result is not None
    assert "regular" in result
    assert "bold" in result
    assert "resolved_name" in result
    assert os.path.exists(result["regular"])
    assert os.path.exists(result["bold"])
    # Should fall back to a known open-source CJK font if Harmony is absent
    assert result["resolved_name"] in ["HarmonyHeiTi", "Noto Sans CJK SC", "WenQuanYi Zen Hei"]
