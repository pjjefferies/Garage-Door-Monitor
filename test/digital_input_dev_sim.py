from dataclasses import dataclass
import datetime as dt
from typing import Any, Optional

from box import Box
import pandas as pd

from src.config.config_main import cfg
from test.config.config_test_main import test_cfg


@dataclass
class DoorSensorSim:
    pin: int
    pull_up: bool
    bounce_time: float
    active_state: Optional[bool] = None  # ignore for now
    pin_factory: Optional[Any] = None  # ignore

    def __post_init__(self) -> None:
        _time_elapsed: int  # seconds
        input_file = test_cfg.TEST.DIGITAL_INPUT_DATE_PATH
        self.door_input_history: pd.DataFrame = pd.read_csv(
            filepath_or_buffer=input_file
        )
        self.start_time: dt.datetime = dt.datetime.now()
        garage_door_config: Box = cfg.DOORS
        pin_index_sensors: dict[int, dict[str, str]] = {}
        for garage_door in garage_door_config.keys():
            for sensor in garage_door_config[garage_door].keys():
                pin_index_sensors[garage_door_config[garage_door][sensor]["NUMBER"]] = {
                    "door": garage_door,
                    "sensor": sensor,
                }
        self._sensor_door = pin_index_sensors[self.pin]["door"]
        self._sensor_sensor = pin_index_sensors[self.pin]["sensor"]

    @property
    def _time_elapsed(self) -> int:
        return int(round((dt.datetime.now() - self.start_time).total_seconds(), 0))

    # TODO
    @property
    def value(self) -> float:
        # get value from door_input_history based on time elapsed and self.sensor_door
        return float(
            self.door_input_history[
                self.door_input_history.seconds_from_start <= self._time_elapsed
            ].iloc[-1, :][f"{self._sensor_door}_{self._sensor_sensor}"]
        )
