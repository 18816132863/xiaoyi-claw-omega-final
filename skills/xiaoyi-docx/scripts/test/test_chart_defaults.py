import sys
import os
import inspect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from matplotlib_chart_utils import (
    add_column_chart,
    add_bar_chart,
    add_line_chart,
    add_pie_chart,
    add_area_chart,
    add_scatter_chart,
    add_radar_chart,
)


def _get_default_legend_pos(func):
    sig = inspect.signature(func)
    return sig.parameters["legend_pos"].default


def test_column_chart_default_legend_pos():
    assert _get_default_legend_pos(add_column_chart) == "right"


def test_bar_chart_default_legend_pos():
    assert _get_default_legend_pos(add_bar_chart) == "right"


def test_line_chart_default_legend_pos():
    assert _get_default_legend_pos(add_line_chart) == "right"


def test_pie_chart_default_legend_pos():
    assert _get_default_legend_pos(add_pie_chart) == "upper right"


def test_area_chart_default_legend_pos():
    assert _get_default_legend_pos(add_area_chart) == "right"


def test_scatter_chart_default_legend_pos():
    assert _get_default_legend_pos(add_scatter_chart) == "right"


def test_radar_chart_default_legend_pos():
    assert _get_default_legend_pos(add_radar_chart) == "upper right"
