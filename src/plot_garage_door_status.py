import datetime as dt
from os import listdir

from box import Box
import pandas as pd

from src.config.config_logging import log_cfg
from src.config.config_main import load_config

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


def plot_garage_door_status(door_status_hisotry: dict[str, pd.DataFrame]) -> None:
    pass


def plot_garage_door_status() -> None:
    door_status_history: dict[str, pd.DataFrame] = load_garage_door_history()

    door_status_history = clean_garage_door_history(door_status_history)

    plot_garage_door_status(door_status_history)
