"""Radar (spider) chart generation for 360° stakeholder scores."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server environments
import matplotlib.pyplot as plt
import numpy as np

from .config import (
    COLOR_ACCENT_BLUE,
    COLOR_BORDER,
    COLOR_MUTED_TEXT,
    COLOR_PRIMARY,
    STAKEHOLDER_LABELS,
    TEMP_DIR,
)


def generate_diamond_radar(
    stakeholder_scores: Dict[str, float],
    output_png: str = "temp_radar.png",
) -> str:
    """
    Generate a diamond-shaped radar chart of stakeholder scores.

    Parameters
    ----------
    stakeholder_scores : dict
        Mapping of stakeholder label to score (out of 70).
        Expected keys: ``Self``, ``Superior``, ``Peers``, ``Students``.
    output_png : str
        Filename for the output PNG. Saved to the temp directory.

    Returns
    -------
    str
        Absolute path to the generated PNG file.
    """
    labels = STAKEHOLDER_LABELS
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]  # Close the circle

    values = [stakeholder_scores[k] for k in labels] + [stakeholder_scores[labels[0]]]

    fig, ax = plt.subplots(figsize=(3.5, 3.5), subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # Cohesive Slate & Cool Blue Accent
    ax.plot(angles, values, color=COLOR_PRIMARY, linewidth=2)
    ax.fill(angles, values, color=COLOR_ACCENT_BLUE, alpha=0.15)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(
        [f"{l}\n({v:.1f})" for l, v in zip(labels, values[:4])],
        size=8,
        weight="bold",
        color=COLOR_PRIMARY,
    )

    ax.set_ylim(0, 70.0)
    ax.set_yticks([20, 40, 60])
    ax.set_yticklabels([], color=COLOR_MUTED_TEXT)
    ax.grid(True, linestyle="--", color=COLOR_BORDER, alpha=0.7)

    plt.tight_layout()

    output_path = TEMP_DIR / output_png
    plt.savefig(str(output_path), dpi=300, transparent=True)
    plt.close()
    return str(output_path)
