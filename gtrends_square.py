import argparse
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pytrends.request import TrendReq


# ─────────────────────────────────────────────
#  Core function
# ─────────────────────────────────────────────

def plot_trend(
    term: str,
    start_date: str,
    *,
    line_color: str = "#00C2FF",
    bg_color: str = "#0A0A0A",
    line_width: float = 2.5,
    output_path: str | None = None,
    size_px: int = 800,
    dpi: int = 150,
) -> str:
    """
    Fetch Google Trends data for *term* from *start_date* to today
    and save a clean square line chart.

    Parameters
    ----------
    term        : Search term, e.g. "machine learning"
    start_date  : ISO date string, e.g. "2020-01-01"
    line_color  : Any matplotlib color string for the trend line
    bg_color    : Any matplotlib color string for the background
    line_width  : Thickness of the line
    output_path : Where to save the PNG (defaults to "<term>_trend.png")
    size_px     : Width & height of the output image in pixels
    dpi         : Dots per inch for the saved PNG

    Returns
    -------
    Path to the saved PNG file.
    """
    end_date = date.today().isoformat()
    timeframe = f"{start_date} {end_date}"

    # ── Fetch data ────────────────────────────────────────────────────
    pytrends = TrendReq(hl="en-US", tz=0)
    pytrends.build_payload([term], timeframe=timeframe)
    df = pytrends.interest_over_time()

    if df.empty:
        raise ValueError(
            f"No trend data returned for '{term}' between {start_date} and {end_date}.\n"
            "Try a broader date range or a different search term."
        )

    values = df[term]

    # ── Build chart ───────────────────────────────────────────────────
    fig_size = size_px / dpi
    fig, ax = plt.subplots(figsize=(fig_size, fig_size), dpi=dpi)

    # Background
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    # Line
    ax.plot(values.index, values.values, color=line_color, linewidth=line_width)

    # Strip everything visual except the line itself
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(False)
    ax.margins(x=0, y=0.05)          # flush left/right, breathing room top/bottom
    ax.set_xlim(values.index[0], values.index[-1])  # pin exactly to data edges

    plt.tight_layout(pad=0)

    # ── Save ──────────────────────────────────────────────────────────
    if output_path is None:
        safe_term = term.replace(" ", "_").lower()
        output_path = f"{safe_term}_trend.png"

    fig.savefig(output_path, facecolor=bg_color, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    print(f"✓ Saved → {output_path}")
    return output_path


# ─────────────────────────────────────────────
#  CLI entry-point
# ─────────────────────────────────────────────

def _parse_args():
    parser = argparse.ArgumentParser(
        description="Save a clean Google Trends line chart as a square PNG."
    )
    parser.add_argument(
        "--term", "-t",
        type=str,
        default=None,
        help="Search term (prompted interactively if omitted)",
    )
    parser.add_argument(
        "--start", "-s",
        type=str,
        default=None,
        help="Start date in YYYY-MM-DD format (prompted interactively if omitted)",
    )
    parser.add_argument(
        "--line-color", "-l",
        type=str,
        default="#00C2FF",
        help="Line color — any matplotlib color string (default: #00C2FF)",
    )
    parser.add_argument(
        "--bg-color", "-b",
        type=str,
        default="#0A0A0A",
        help="Background color — any matplotlib color string (default: #0A0A0A)",
    )
    parser.add_argument(
        "--line-width", "-w",
        type=float,
        default=2.5,
        help="Line thickness in points (default: 2.5)",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output PNG path (default: <term>_trend.png)",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=800,
        help="Image width & height in pixels (default: 800)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="PNG DPI (default: 150)",
    )
    return parser.parse_args()


def main():
    args = _parse_args()

    term = args.term or input("Search term: ").strip()
    if not term:
        raise SystemExit("Error: search term cannot be empty.")

    start = args.start
    if not start:
        start = input("Start date (YYYY-MM-DD): ").strip()
    # Basic validation
    try:
        date.fromisoformat(start)
    except ValueError:
        raise SystemExit(f"Error: '{start}' is not a valid YYYY-MM-DD date.")

    # ── Color customization dialogue ──────────────────────────────────
    # If colors were passed as CLI flags, use them directly and skip the
    # prompt. If running interactively (no flags), offer a quick dialogue.
    line_color = args.line_color
    bg_color   = args.bg_color

    cli_colors_provided = (
        "--line-color" in __import__("sys").argv
        or "-l" in __import__("sys").argv
        or "--bg-color" in __import__("sys").argv
        or "-b" in __import__("sys").argv
    )

    if not cli_colors_provided:
        customize = input("\nCustomize colors? [y/N]: ").strip().lower()
        if customize == "y":
            print("Enter any matplotlib color: hex (#FF4500), name (white), etc.")
            print(f"  Current line color  : {line_color}")
            new_line = input("  New line color      : ").strip()
            if new_line:
                line_color = new_line

            print(f"  Current background  : {bg_color}")
            new_bg = input("  New background color: ").strip()
            if new_bg:
                bg_color = new_bg

    plot_trend(
        term=term,
        start_date=start,
        line_color=line_color,
        bg_color=bg_color,
        line_width=args.line_width,
        output_path=args.output,
        size_px=args.size,
        dpi=args.dpi,
    )


if __name__ == "__main__":
    main()
