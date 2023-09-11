import datetime as dt
from os import listdir
from typing import Protocol

from box import Box
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


DOORS: list[str] = ["one_car", "two_car"]
EXCLUDED_ACTIONS: list[str] = ["created"]
POSITION_VALUE: dict[str, float] = {
    "closed": 0,
    "unknown": 0.5,
    "Unknown": 0.5,
    "un_open": 0.5,
    "un_closed": 0.5,
    "open": 1,
}


def load_garage_door_history() -> dict[str, pd.DataFrame]:
    config_filename_base: str = log_cfg.handler.history.filename.split(".")[0]
    history_filenames: list[str] = [
        fn
        for fn in listdir(log_cfg.handler.history.folder)
        if (fn.startswith(config_filename_base) and "example" not in fn)
    ]

    door_status_history: dict[str, pd.DataFrame] = {}  # a dict for each door
    door_name: str
    line_list: list[str]
    timestamp: dt.datetime
    new_status: pd.DataFrame

    for history_filename in history_filenames:
        with open(file=history_filename) as file:
            for a_line in file:
                line_list = a_line.split(":")
                if (
                    len(line_list) < 7
                    or line_list[5] not in DOORS
                    or line_list[6] in EXCLUDED_ACTIONS
                ):
                    continue
                door_name = a_line[5]
                if door_name not in door_status_history:
                    door_status_history[door_name] = pd.DataFrame(
                        columns=["datetime", "position"]
                    )
                try:
                    timestamp = dt.datetime.strptime(
                        ":".join(a_line[:3]), "%Y-%m-%d %H:%M:%S,%f"
                    )
                except ValueError:  # invalid date time
                    continue
                new_status = pd.DataFrame(
                    {"datetime": timestamp, "position": line_list[6]}
                )
                door_status_history[door_name] = pd.concat(
                    [door_status_history[door_name], new_status], ignore_index=True
                )
    return door_status_history


def clean_garage_door_history(
    door_status_hisotry: dict[str, pd.DataFrame]
) -> dict[str, pd.DataFrame]:
    new_dsh: pd.DataFrame
    temp_door_status: pd.DataFrame
    added_timestamp: dt.datetime
    cfg: Box = load_config()
    clean_gdh: dict[str, pd.DataFrame] = {}
    for a_door, a_door_status_history in door_status_hisotry.items():
        a_door_status_history.sort_values(by="datetime", inplace=True)
        a_door_status_history.drop_duplicates(
            subset="datetime", inplace=True, ignore_index=True
        )
        a_door_status_history.reset_index()

        new_dsh = a_door_status_history.iloc[0]

        for _, row in a_door_status_history.iloc[1:].iterrows():
            if (
                row["datetime"] - new_dsh.iloc[-1]["datetime"]
            ).total_seconds() > cfg.GRAPHING.MAX_TRANSITION_TIME and row[
                "position"
            ] != new_dsh.iloc[
                -1
            ][
                "position"
            ]:
                added_timestamp = row["datetime"] - dt.timedelta(
                    seconds=cfg.GRAPHING.MAX_TRANSITION_TIME
                )
                temp_door_status = pd.DataFrame(
                    {
                        "datetime": added_timestamp,
                        "position": new_dsh.iloc[-1]["position"],
                    }
                )
                # Add added row, if necessary
                new_dsh = pd.concat([new_dsh, temp_door_status], ignore_index=True)
            # Add next original row
            new_dsh = pd.concat([new_dsh, row.to_frame().T], ignore_index=True)

        new_dsh["position_value"] = POSITION_VALUE[new_dsh["position"]]
        new_dsh.reset_index()

        clean_gdh[a_door] = new_dsh

    return clean_gdh


def create_garage_door_status_plot(
    door_status_hisotry: dict[str, pd.DataFrame]
) -> None:
    # Create a Tkinter window
    root = tk.Tk()

    # Create a Matplotlib figure
    fig = plt.figure()

    for door, door_history_data in door_status_hisotry.items():
        a_plot: Figure = tk_xy_plot(
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

        # Display the figure in the Tkinter window
        canvas = FigureCanvasTkAgg(a_plot, fig)
        canvas.get_tk_widget().pack(side="top", fill="both", expand=1)

        # canvas = tk.Canvas(
        #     root, width=fig.get_width_inches(), height=fig.get_height_inches()
        # )
        # canvas.pack()

        # Draw the figure on the canvas
        canvas.create_image(0, 0, anchor="nw", image=fig.canvas.tostring_rgb())

        # Start the mainloop
        root.mainloop()


def plot_garage_door_status() -> None:
    door_status_history: dict[str, pd.DataFrame] = load_garage_door_history()

    door_status_history = clean_garage_door_history(door_status_history)

    create_garage_door_status_plot(door_status_history)


if __name__ == "__main__":
    plot_garage_door_status()
