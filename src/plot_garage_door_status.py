import datetime as dt
import os
from typing import Protocol

from box import Box
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
)  # , NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.config.config_logging import log_cfg, logger
from src.config.config_main import load_config
from src.tk_plot import tk_xy_plot


class LoggerProto(Protocol):
    def debug(self, msg: str) -> None:
        ...

    def warning(self, msg: str) -> None:
        ...

    def error(self, msg: str) -> None:
        ...


DOORS: list[str] = ["ONE_CAR", "TWO_CAR"]
EXCLUDED_ACTIONS: list[str] = ["created"]
POSITION_VALUE: dict[str, float] = {
    "closed": 0,
    "unknown": 0.5,
    "Unknown": 0.5,
    "un_open": 0.5,
    "un_closed": 0.5,
    "open": 1,
    "opened": 1,
}


def load_garage_door_history() -> dict[str, pd.DataFrame]:
    config_filename_base: str = log_cfg.handler.history.filename.split(".")[0]
    history_filenames: list[str] = [
        fn
        for fn in os.listdir(log_cfg.handler.history.folder)
        if (fn.startswith(config_filename_base) and "example" not in fn)
    ]

    door_status_history: dict[str, pd.DataFrame] = {}  # a dict for each door
    door_name: str
    line_list: list[str]
    timestamp: dt.datetime
    new_status: pd.DataFrame

    for history_filename in history_filenames:
        history_filepath = os.path.join(
            log_cfg.handler.history.folder, history_filename
        )
        with open(file=history_filepath) as file:
            for a_line in file:
                if a_line.endswith("\n"):
                    a_line = a_line[:-1]
                line_list = a_line.split(":")
                if (
                    len(line_list) < 7
                    or line_list[5] not in DOORS
                    or line_list[6] in EXCLUDED_ACTIONS
                ):
                    continue
                # logger.debug(msg=f"{line_list=}")

                door_name = line_list[5]
                if door_name not in door_status_history:
                    door_status_history[door_name] = pd.DataFrame(
                        columns=["datetime", "position"]
                    )
                try:
                    timestamp = dt.datetime.strptime(
                        ":".join(line_list[:3]), "%Y-%m-%d %H:%M:%S,%f"
                    )
                except ValueError:  # invalid date time
                    logger.debug(f"Invalid Timestamp: {line_list=}")
                    continue
                new_status = pd.DataFrame(
                    {"datetime": [timestamp], "position": [line_list[6]]}
                )

                # logger.debug(msg=f"{new_status=}")

                door_status_history[door_name] = pd.concat(
                    [door_status_history[door_name], new_status], ignore_index=True
                )

    return door_status_history


def clean_garage_door_history(
    door_status_history: dict[str, pd.DataFrame]
) -> dict[str, pd.DataFrame]:
    new_dsh: pd.DataFrame
    temp_door_status: pd.DataFrame
    added_timestamp: dt.datetime
    cfg: Box = load_config()
    clean_gdh: dict[str, pd.DataFrame] = {}
    transition_time: float

    # logger.debug(msg=f"{door_status_history=}")

    for a_door, a_door_status_history in door_status_history.items():
        a_door_status_history.sort_values(by="datetime", inplace=True)
        a_door_status_history.drop_duplicates(
            subset="datetime", inplace=True, ignore_index=True
        )
        a_door_status_history.reset_index()

        # logger.debug(msg=f"{a_door=}")
        # logger.debug(msg=f"{a_door_status_history=}")
        # logger.debug(msg=f"{a_door_status_history.shape=}")

        new_dsh = a_door_status_history.iloc[:1]

        for _, row in a_door_status_history.iloc[1:].iterrows():
            # logger.debug(msg=f"{a_door=}:{new_dsh=}:{new_dsh.iloc[-1]=}")
            transition_time = (
                row["datetime"] - new_dsh.iloc[-1]["datetime"]
            ).total_seconds()
            # logger.debug(msg=f"{transition_time=}, {cfg.GRAPHING.MAX_TRANSITION_TIME=}")

            if (
                transition_time > cfg.GRAPHING.MAX_TRANSITION_TIME
                and row["position"] != new_dsh.iloc[-1]["position"]
            ):
                added_timestamp = row["datetime"] - dt.timedelta(
                    seconds=cfg.GRAPHING.MAX_TRANSITION_TIME
                )
                temp_door_status = pd.DataFrame(
                    {
                        "datetime": [added_timestamp],
                        "position": [new_dsh.iloc[-1]["position"]],
                    }
                )
                # Add added row, if necessary
                new_dsh = pd.concat([new_dsh, temp_door_status], ignore_index=True)
            # Add next original row
            new_dsh = pd.concat([new_dsh, row.to_frame().T], ignore_index=True)

        new_dsh["position_value"] = new_dsh["position"].map(POSITION_VALUE)
        new_dsh.reset_index()

        clean_gdh[a_door] = new_dsh

    return clean_gdh


def create_garage_door_status_plot(
    door_status_hisotry: dict[str, pd.DataFrame]
) -> None:
    # Create a Tkinter window
    root = tk.Tk()

    # Create a Matplotlib figure
    # fig = plt.figure()
    # fig = tk.Frame()

    for door, door_history_data in door_status_hisotry.items():
        fig, ax = plt.subplots()
        # ax.plotplt.figure(figsize=(4, 4), dpi=260, facecolor="cornflowerblue")
        ax.plot(
            door_history_data["datetime"],
            door_history_data["position_value"],
            color="blue",
            # linestyle="solid",
            # linewidth=2,
        )
        ax.set(
            xlabel="Date",
            ylabel="Door Position(0=Close, 1=Open)",
            title=f"Door, {door}, Position History",
        )
        """
        fig: Figure = tk_xy_plot(
            x1_data=door_history_data["datetime"],
            y1_data=door_history_data["position_value"],
            # data1_style='b.-',
            # x2_data=None,
            # y2_data=None,
            # data2_style='g.-',
            # xlim=,
            # y1lim=,
            # y2lim=y2lim,
            x_label="Date",
            y1_label="Door Position (0=Closed, 1=Open)",
            # y2_label="",
            title=f"Door, {door}, Position History",
            show_x_grid=False,
            show_y1_grid=False,
            # show_y2_grid=False,
            bg_color="w",
            fig_width=500,
            fig_height=300,
            logger=logger,
        )
        """
        plt.show()

        # Display the figure in the Tkinter window
        # canvas = FigureCanvasTkAgg(a_plot, fig)
        # canvas.show()
        # canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        # toolbar = NavigationToolbar2TkAgg(canvas, fig)
        # toolbar.update()
        # canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        """
        canvas = tk.Canvas(
            master=root, width=fig.get_figwidth(), height=fig.get_figheight()
        )
        canvas.c.add_widget(fig)
        canvas.pack()
        """
        # canvas.get_tk_widget().pack(side="top", fill="both", expand=1)

        # canvas = tk.Canvas(
        #     root, width=fig.get_width_inches(), height=fig.get_height_inches()
        # )
        # canvas.pack()

        # Draw the figure on the canvas
        # canvas.create_image(0, 0, anchor="nw", image=fig.canvas.tostring_rgb())
        # canvas.create_image(a_plot)
        # canvas.pack()

        # Start the mainloop
        # root.mainloop()
        logger.debug(
            msg=f"{door_history_data['datetime']}, {door_history_data['position_value']}"
        )


def plot_garage_door_status() -> None:
    logger.debug(f"Starring plot_garage_door_status")
    door_status_history: dict[str, pd.DataFrame] = load_garage_door_history()

    door_status_history = clean_garage_door_history(door_status_history)

    create_garage_door_status_plot(door_status_history)


if __name__ == "__main__":
    plot_garage_door_status()
