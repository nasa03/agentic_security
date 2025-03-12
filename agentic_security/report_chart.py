import io
import string

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap, Normalize

from agentic_security.logutils import logger

from .primitives import Table


def plot_security_report(table: Table) -> io.BytesIO:
    try:
        return _plot_security_report(table=table)
    except (TypeError, ValueError, OverflowError, IndexError, Exception) as e:
        logger.error(f"Error in generating the security report: {e}")
    return io.BytesIO()


def generate_identifiers(data: pd.DataFrame) -> list[str]:
    try:
        _generate_identifiers(data=data)
    except (TypeError, ValueError, Exception) as e:
        logger.error(f"Error in generate_identifiers: {e}")
    return [""]


def _plot_security_report(table: Table) -> io.BytesIO:
    # Data preprocessing
    logger.info("Data preprocessing started.")

    data = pd.DataFrame(table)

    # Sort by failure rate and reset index
    data = data.sort_values("failureRate", ascending=False).reset_index(drop=True)
    data["identifier"] = generate_identifiers(data)

    # Plot setup
    fig, ax = plt.subplots(figsize=(12, 10), subplot_kw={"projection": "polar"})
    fig.set_facecolor("#f0f0f0")
    ax.set_facecolor("#f0f0f0")
    logger.info("Plot setup complete.")

    # Styling parameters
    colors = ["#6C5B7B", "#C06C84", "#F67280", "#F8B195"][::-1]  # Pastel palette
    cmap = LinearSegmentedColormap.from_list("custom", colors, N=256)
    norm = Normalize(vmin=data["tokens"].min(), vmax=data["tokens"].max())

    # Compute angles for the polar plot
    angles = np.linspace(0, 2 * np.pi, len(data), endpoint=False)

    # Plot bars
    bars = ax.bar(
        angles,
        data["failureRate"],
        width=0.5,
        color=[cmap(norm(t)) for t in data["tokens"]],
        alpha=0.8,
        label="Failure Rate %",
    )

    # Customize polar plot
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_ylim(0, max(data["failureRate"]) * 1.1)  # Add some headroom

    # Add labels (now using identifiers)
    ax.set_xticks(angles)
    ax.set_xticklabels(data["identifier"], fontsize=10, fontweight="bold")

    # Add circular grid lines
    ax.yaxis.grid(True, color="gray", linestyle=":", alpha=0.5)
    ax.set_yticks(np.arange(0, max(data["failureRate"]), 20))
    ax.set_yticklabels(
        [f"{x}%" for x in range(0, int(max(data["failureRate"])), 20)], fontsize=8
    )

    # Add radial lines
    ax.vlines(
        angles,
        0,
        max(data["failureRate"]) * 1.1,
        color="gray",
        linestyle=":",
        alpha=0.5,
    )

    # Color bar for token count
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, orientation="horizontal", pad=0.08, aspect=30)
    cbar.set_label("Token Count (k)", fontsize=10, fontweight="bold")

    # Title and caption
    fig.suptitle(
        "Security Report for Different Modules",
        fontsize=16,
        fontweight="bold",
        y=1.02,
    )
    caption = "Report generated by https://github.com/msoedov/agentic_security"
    fig.text(
        0.5,
        0.02,
        caption,
        fontsize=8,
        ha="center",
        va="bottom",
        alpha=0.7,
        fontweight="bold",
    )

    # Add failure rate values on the bars
    for angle, radius, bar, identifier in zip(
        angles, data["failureRate"], bars, data["identifier"]
    ):
        ax.text(
            angle,
            radius,
            f"{identifier}: {radius:.1f}%",
            ha="center",
            va="bottom",
            rotation=angle * 180 / np.pi - 90,
            rotation_mode="anchor",
            fontsize=7,
            fontweight="bold",
            color="black",
        )

    # Add a table with identifiers and dataset names
    table_data = [["Threat"]] + [
        [f"{identifier}: {module} ({fr:.1f}%)"]
        for identifier, fr, module in zip(
            data["identifier"], data["failureRate"], data["module"]
        )
    ]
    table = ax.table(cellText=table_data, loc="right", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(8)

    # Adjust table style
    table.scale(1, 0.7)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("none")
        cell.set_facecolor("#f0f0f0" if row % 2 == 0 else "#e0e0e0")
        cell.set_alpha(0.8)
        cell.set_text_props(wrap=True)
        if row == 0:
            cell.set_text_props(fontweight="bold")

    # Adjust layout and save
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    logger.info("Report successfully generated and saved to buffer.")
    return buf


def _generate_identifiers(data: pd.DataFrame) -> list[str]:
    data_length = len(data)

    alphabet = string.ascii_uppercase
    num_letters = len(alphabet)

    identifiers = []
    for i in range(data_length):
        letter_index = i // num_letters
        number = (i % num_letters) + 1
        identifier = f"{alphabet[letter_index]}{number}"
        identifiers.append(identifier)

    return identifiers
