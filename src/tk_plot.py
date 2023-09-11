"""
pyplot wrapper of x/y plot \for use in tkinter
This returns a 'a_plot' to be applied as:
    canvas = figureCanvasTkAgg(a_plot, master=whatever)
"""

import re
import math
from typing import Optional, Protocol

import numpy as np
import numpy.typing as npt
import pandas as pd
from matplotlib.axis import Axis
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt

from src.color_as_hex_string import color_as_hex_string


class LoggerProto(Protocol):
    def debug(self, msg: str) -> None:
        ...

    def warning(self, msg: str) -> None:
        ...

    def error(self, msg: str) -> None:
        ...


def tk_xy_plot(
    *,
    x1_data: Optional["list[float] | pd.Series[float] | npt.ArrayLike"] = None,
    y1_data: Optional["list[float] | pd.Series[float] | npt.ArrayLike"] = None,
    data1_color: str = "#0000ff",  # blue
    data1_linestyle: str = "solid",
    data1_markerstyle: str = "",
    x2_data: Optional["list[float] | pd.Series[float] | npt.ArrayLike"] = None,
    y2_data: Optional["list[float] | pd.Series[float] | npt.ArrayLike"] = None,
    data2_color: str = "#00ff00",  # green
    data2_linestyle: str = "solid",
    data2_markerstyle: str = "",
    xlim: tuple[Optional[float], Optional[float]] = (None, None),
    y1lim: tuple[Optional[float], Optional[float]] = (None, None),
    y2lim: tuple[Optional[float], Optional[float]] = (
        None,
        None,
    ),  # if these are set, plot y2 axis
    x_label: str = "x-axis",
    y1_label: str = "y1-axis",
    y2_label: str = "y2-axis",
    title: str = "A Title",
    show_x_grid: bool = False,
    show_y1_grid: bool = False,
    show_y2_grid: bool = False,
    bg_color: str = "w",
    fig_width: float | int = 5,  # in inches but affected by dpi
    fig_height: float | int = 4,  # in inches but affected by dpi
    logger: LoggerProto,
) -> Figure:
    """
    pyplot wrapper for use in tkinter
    This returns a 'a_plot' to be applied as:
        canvas = figureCanvasTkAgg(a_plot, master=whatever)
    """
    x1_data = pd.Series(x1_data, dtype=np.float64)
    y1_data = pd.Series(y1_data, dtype=np.float64)
    x2_data = pd.Series(x2_data, dtype=np.float64)
    y2_data = pd.Series(y2_data, dtype=np.float64)
    if (x1_data.empty or y1_data.empty) and (x2_data.empty or y2_data.empty):
        raise ValueError(
            "Both X1/Y1 and X2/Y2 inputs cannot be None/empty. " + "You must have data"
        )

    a_fig = Figure(figsize=(fig_width, fig_height), dpi=100)
    a_plot = a_fig.add_subplot(1, 1, 1)

    if not y1_data.empty:
        a_plot.plot(
            x1_data,
            y1_data,
            color=data1_color,
            linestyle=data1_linestyle,
            marker=data1_markerstyle,
        )
    a_plot.set_title(title)
    bg_color = re.sub(r"[^A-Za-z]+", "", bg_color)
    if bg_color == "":
        bg_color = "white"
    a_plot.set_facecolor(bg_color)

    # Set-up X-Axis
    if xlim[0] is not None and xlim[1] is not None:
        a_plot.set_xlim(xlim)
    a_plot.set_xlabel(x_label)
    if show_x_grid:
        a_plot.xaxis.grid(
            visible=True, which="major", color="k", linestyle="--", linewidth=0.25
        )

    # Set-up Left/Primary Y-Axis
    if not y1_data.empty:
        if y1lim[0] is not None and y1lim[1] is not None:
            a_plot.set_ylim(y1lim)
        y1label_color = data1_color
        if y1label_color == "":
            y1label_color = "b"
        a_plot.set_ylabel(y1_label, color=y1label_color)
        a_plot.tick_params("y", colors=y1label_color)
        if show_y1_grid:
            a_plot.yaxis.grid(
                visible=True,
                which="major",
                color=y1label_color,
                linestyle="--",
                linewidth=0.25,
            )

    # Set-up right/Secondary Y-Axis
    if y2lim[0] is not None and y2lim[1] is not None:
        ax2 = a_plot.twinx()
        ax2.set_ylim(y2lim)
        if not x2_data.empty and not y2_data.empty:
            ax2.plot(
                x2_data,
                y2_data,
                color=data2_color,
                linestyle=data2_linestyle,
                marker=data2_markerstyle,
            )
        y2label_color = data2_color
        if y2label_color == "":
            y2label_color = "g"
        ax2.set_ylabel(y2_label, color=y2label_color)
        ax2.tick_params("y", colors=y2label_color)
        if show_y2_grid:
            ax2.yaxis.grid(
                visible=True,
                which="major",
                color=y2label_color,
                linestyle="--",
                linewidth=0.25,
            )
    elif not x2_data.empty and not y2_data.empty:
        logger.debug(msg=f"{y2_data=}")
        a_plot.plot(
            x2_data,
            y2_data,
            color=data2_color,
            linestyle=data2_linestyle,
            marker=data2_markerstyle,
        )

    return a_fig


def tk_histogram_plot(
    *,
    x_data: "Optional[list[float] | tuple[float] | pd.Series[float] | npt.ArrayLike]" = None,
    bar_color: str = "#000000",  # 'black'
    labels_on_bars: bool = True,
    xlim: tuple[Optional[float], Optional[float]] = (None, None),
    y1lim: tuple[Optional[float], Optional[float]] = (None, None),
    x_label: str = "x-axis",
    y_label: str = "y1-axis",
    title: str = "A Title",
    show_y1_grid: bool = False,
    show_labels_on_bars: bool = False,
    bg_color: str = "w",
    fig_width: float = 5,  # in inches but affected by dpi
    fig_height: float = 4,  # in inches but affected by dpi
    num_bins: Optional[int] = None,
    logger: LoggerProto,
):
    """
    pyplot wrapper of histogram for use in tkinter
    This returns a 'a_plot' to be applied as:
        canvas = figureCanvasTkAgg(a_plot, master=whatever)
    """

    x_data = pd.Series(x_data)

    if x_data.empty:
        raise ValueError("You must have data")

    if num_bins is None:
        num_bins = min(int(len(x_data) / 7), 50)

    a_fig = Figure(figsize=(fig_width, fig_height), dpi=100)
    a_plot = a_fig.add_subplot(1, 1, 1)

    a_plot.set_title(title)

    try:
        bar_color = color_as_hex_string(bar_color)
    except ValueError:
        bar_color = "#000000"  # Black?

    # n is the count in each bin, bins is the lower-limit of the bin
    n: int
    bins: float
    patches: Rectangle
    n, bins, patches = a_plot.hist(
        x=x_data,
        bins=num_bins,
        range=xlim,
        histtype="bar",
        color=bar_color,
        ec="black",
        lw=0.5,
        rwidth=1,
        label=title,
    )

    a_plot.set_xlabel(x_label)
    a_plot.set_ylabel(y_label)

    logger.debug(msg=f"{n=}\n{bins=}\n{patches=}\n{patches[0]=}")

    rects = [
        rect
        for rect in patches.get_children()
        if isinstance(rect, Rectangle) and rect.get_height() > 1
    ]

    if show_labels_on_bars:
        add_bar_plot_bars_labels(
            axis=a_plot,
            rects=rects,
            # rect_heights=n,
            # rect_x=bins,
            # rect_width=bins[1] - bins[0],
            bar_color=bar_color,
            logger=logger,
        )

    # y1 Grid
    if show_y1_grid:
        a_plot.grid(
            visible=show_y1_grid,
            which="major",
            axis="y",
            color=bar_color,
            linestyle=":",
            linewidth=0.5,
        )

    # a_fig.tight_layout()

    return a_fig


def tk_bar_plot(
    *,
    y1_data: "Optional[list[float] | tuple[float] | pd.Series[float] | npt.ArrayLike]" = None,
    y2_data: "Optional[list[float] | tuple[float] | pd.Series[float] | npt.ArrayLike]" = None,
    stacked: bool = False,
    bar_labels: "Optional[pd.Series[str]]" = None,
    bar1_color: str = "#0000ff",  # blue
    bar2_color: str = "#008800",  # green
    bar_edge_color: str = "#000000",  # black
    bar_width: Optional[float] = None,
    show_labels_on_bars: bool = True,
    # xlim=(None, None),
    # ylim=(None, None),
    # y1_lim=(None, None),
    # y2_lim=(None, None),
    x_label: str = "x-axis",
    y1_label: str = "y1-axis",
    y2_label: Optional[str] = None,
    title: str = "A Title",
    show_y1_grid: bool = False,
    show_y2_grid: bool = False,
    bg_color: str = "w",
    fig_width: float = 5,  # in inches but affected by dpi
    fig_height: float = 4,  # in inches but affected by dpi
    logger: LoggerProto,
) -> Figure:
    """
    pyplot wrapper of bar plot for use in tkinter
    This returns a 'a_plot' to be applied as:
        canvas = figureCanvasTkAgg(a_plot, master=whatever)
    """
    y1_data = pd.Series(y1_data, dtype=np.float64)
    y2_data = pd.Series(y2_data, dtype=np.float64)
    if y1_data.empty and y2_data.empty:
        raise ValueError(
            "Both X1/Y1 and X2/Y2 inputs cannot be None/empty. You must have data"
        )

    if y1_data.empty or y2_data.empty:
        stacked = False

    bar_labels = pd.Series(bar_labels) if not pd.Series(bar_labels).empty else None

    # Set Bar Widths
    bar_width = (
        bar_width
        if bar_width is not None
        else (0.4 if (not y1_data.empty and not y2_data.empty and not stacked) else 0.7)
    )

    a_fig: Figure
    ax1: Axis
    a_fig, ax1 = plt.subplots(
        nrows=1, ncols=1, frameon=True, figsize=(fig_width, fig_height)
    )

    # Set Plot Title
    ax1.set_title(title)

    # Plot X-Axes Labels
    ax1.set_xlabel(x_label)

    if not y1_data.empty:
        if bar_labels is not None:
            bar_labels.name = x_label
        # y1 Bars
        y1_data_bar_pos = 0.5 if stacked or y2_data.empty else 1

        if bar_labels is not None:
            y1_data.index = bar_labels

        try:
            bar1_color = color_as_hex_string(bar1_color)
        except ValueError:
            bar1_color = "#000000"  # Black

        logger.debug(msg=f"{y1_data=}")
        y1_subplot = y1_data.plot(
            kind="bar",
            ax=ax1,
            color=bar1_color,
            edgecolor=bar_edge_color,
            width=bar_width,
            position=y1_data_bar_pos,
            use_index=True,
        )

        # Add value labels on bars
        if show_labels_on_bars:
            rects: list[Rectangle] = [
                rect
                for rect in y1_subplot.get_children()
                if isinstance(rect, Rectangle) and rect.get_height() > 1
            ]
            add_bar_plot_bars_labels(
                axis=ax1, rects=rects, bar_color=bar1_color, logger=logger
            )

        # y1 Axis Labels
        if stacked:
            y1_plot_label: str = f"{y1_label} & {y2_label}"
        else:
            y1_plot_label: str = y1_label
        ax1.set_ylabel(ylabel=y1_plot_label, color=bar1_color)

        # Color y1 tick labels
        for tl in ax1.get_yticklabels():
            tl.set_color(bar1_color)

        # y1 Grid
        if show_y1_grid:
            ax1.grid(
                visible=show_y1_grid,
                which="major",
                axis="y",
                color=bar1_color,
                linestyle=":",
                linewidth=0.5,
            )

    if not y2_data.empty and (
        y1_data.empty or not stacked
    ):  # i.e. IF there IS a y2-axis
        try:
            bar2_color = color_as_hex_string(bar2_color)
        except ValueError:
            bar2_color = "#000000"  # Black?

        # Create y2 Axis
        ax2: Axis = ax1.twinx()

        # y2 Bars
        y2_data_bar_pos = 0.5 if stacked or y1_data.empty else 0
        y2_subplot = y2_data.plot(
            kind="bar",
            ax=ax2,
            color=bar2_color,
            edgecolor=bar_edge_color,
            width=bar_width,
            position=y2_data_bar_pos,
        )

        # Add value labels on bars
        if show_labels_on_bars:
            logger.debug(
                msg=f"{y2_subplot.properties()['default_bbox_extra_artists']=}"
            )
            rects = [
                rect
                for rect in y2_subplot.get_children()
                if isinstance(rect, Rectangle) and rect.get_height() > 1
            ]

            add_bar_plot_bars_labels(
                axis=ax2, rects=rects, bar_color=bar2_color, logger=logger
            )

            # y2 Axis Labels
            ax2.set_ylabel(ylabel=y2_label, color=bar2_color)

            # Color y2 tick Labels
            for tl in ax2.get_yticklabels():
                tl.set_color(bar2_color)

            # y2 Grid
            if show_y2_grid:
                ax2.grid(
                    visible=show_y2_grid,
                    which="major",
                    axis="y",
                    color=bar2_color,
                    linestyle=":",
                    linewidth=0.5,
                )
        elif stacked:
            bottom = y1_data
            y2_data.plot(
                kind="bar",
                ax=ax2,
                color=bar2_color,
                edgecolor=bar_edge_color,
                width=bar_width,
                position=0.5,
                bottom=bottom,
            )

    a_fig.tight_layout = {"w_pad": 0.1, "h_pad": 0.1}

    # a_fig.show(warn=False)
    return a_fig


def add_bar_plot_bars_labels(
    *,
    axis: Axis,
    rects: list[Rectangle],
    bar_color="0x888888",
    logger: LoggerProto,
):
    """
    Attach a text label above each bar in *rects*, displaying its height.

    axis: axis that bars are attached to
    rects: rectangles from bar plots
    bar_color: 0x000000 format
    """

    bar_heights: list[float] = [rect.get_height() for rect in rects]
    no_bars = len(rects)  # if rect_heights is None else len(rect_heights)
    bar_width: float = rects[0].get_width()
    bar_x_locs: list[float] = [rect.get_x() for rect in rects]
    fontsize = min(max(21.176 - 0.4706 * no_bars, 4.5), 12)

    color_amount = (
        int(f"0x{bar_color[1:3]}", 16)
        + int(f"0x{bar_color[3:5]}", 16)
        + int(f"0x{bar_color[5:7]}", 16)
    )
    text_color = (
        "#000000" if color_amount > 381 else "#ffffff"  # Black text for light bars
    )  # White text for dark bars

    if fontsize < 7:
        y_loc_mult = 1.01
        vert_alignment = "bottom"
        text_color = "black"
    else:
        y_loc_mult = 0.99
        vert_alignment = "top"
        text_color = (
            "#000000" if color_amount > 381 else "#ffffff"  # Black text for light bars
        )  # White text for dark bars

    max_bar_height: float = float(axis.properties()["ylim"][1])

    label_dec_places: str = str(max(math.ceil(2 - math.log(max_bar_height, 10)), 0))

    total_bar_height: float = sum(bar_heights)
    for rect_no in range(no_bars):
        height: float = bar_heights[rect_no]
        height_percent: float = height / total_bar_height * 100
        x_loc: float = bar_x_locs[rect_no] + bar_width * 0.55
        axis.text(
            x=x_loc,
            y=y_loc_mult * height,
            s=f"{height:0.{label_dec_places}f} ({height_percent:0.1f}%)",
            ha="center",
            va=vert_alignment,
            rotation="vertical",
            color=text_color,
            fontsize=fontsize,
        )
