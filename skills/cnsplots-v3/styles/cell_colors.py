"""Cell Press color palette definitions and helpers for matplotlib / seaborn.

Provides the 10-color Cell journal palette, individual color hex codes,
and convenience functions for applying the palette to seaborn and matplotlib.
"""

from __future__ import annotations

# Cell Press 10-color qualitative palette (hex codes)
CELL_HEX: list[str] = [
    "#c84c3a",  # 0: Cell Red / Rust
    "#2f7e8f",  # 1: Teal / Ocean Blue
    "#e1a22e",  # 2: Ochre / Amber Gold
    "#4e5a8a",  # 3: Slate / Indigo
    "#5f9862",  # 4: Sage Green
    "#d07a6a",  # 5: Terracotta / Salmon
    "#8b6fa8",  # 6: Soft Purple / Lavender
    "#7b8c9e",  # 7: Steel Blue / Grey-Blue
    "#b85f7a",  # 8: Muted Rose / Berry
    "#6b6b6b",  # 9: Neutral Grey
]

# Named constants for semantic assignment
CELL_RED = CELL_HEX[0]
CELL_TEAL = CELL_HEX[1]
CELL_OCHRE = CELL_HEX[2]
CELL_SLATE = CELL_HEX[3]
CELL_SAGE = CELL_HEX[4]
CELL_SALMON = CELL_HEX[5]
CELL_PURPLE = CELL_HEX[6]
CELL_STEEL = CELL_HEX[7]
CELL_ROSE = CELL_HEX[8]
CELL_GREY = CELL_HEX[9]

# RGB float tuples (0.0 to 1.0)
CELL_RGB: list[tuple[float, float, float]] = [
    (0.7843137, 0.2980392, 0.2274510),
    (0.1843137, 0.4941176, 0.5607843),
    (0.8823529, 0.6352941, 0.1803922),
    (0.3058824, 0.3529412, 0.5411765),
    (0.3725490, 0.5960784, 0.3843137),
    (0.8156863, 0.4784314, 0.4156863),
    (0.5450980, 0.4352941, 0.6588235),
    (0.4823529, 0.5490196, 0.6196078),
    (0.7215686, 0.3725490, 0.4784314),
    (0.4196078, 0.4196078, 0.4196078),
]


def get_cell_colors(n: int | None = None) -> list[str]:
    """Return the first n colors of the Cell palette as hex strings.

    If n is None or exceeds 10, returns all 10 colors.
    """
    if n is None or n >= len(CELL_HEX):
        return list(CELL_HEX)
    return list(CELL_HEX[:n])


def apply_cell_palette_to_seaborn() -> None:
    """Register and set the Cell palette as the active seaborn palette."""
    try:
        import seaborn as sns

        sns.set_palette(sns.color_palette(CELL_HEX))
    except ImportError:
        pass
