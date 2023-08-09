from dataclasses import dataclass
import datetime as dt
from enum import Enum

from typing import Protocol  # Optional

import pytz

from src.config.config_logging import logger

TIME_ZONE = pytz.timezone(zone="America/Detroit")


class LoggerProto(Protocol):
    def debug(self, msg: str) -> None:
        ...

    def info(self, msg: str) -> None:
        ...


class GarageStatus(Enum):
    open = 1
    un_open = 2
    unknown = 3
    un_closed = 4
    closed = 5


@dataclass
class GarageDoor:
    name: str
    debug_logger: LoggerProto
    data_logger: LoggerProto
    status: GarageStatus = GarageStatus.unknown

    def __post_init__(self):
        self.status_change_time: dt.datetime = dt.datetime.now(tz=TIME_ZONE)
        msg = f"DOOR:{self.name}:created"
        self.debug_logger.debug(msg=msg)
        self.data_logger.info(msg=msg)

    def report_status(self):
        msg: str = f"DOOR:{self.name}:{self.status.name}"
        self.data_logger.info(msg=msg)
        self.debug_logger.debug(msg=msg)

    def update_status(self,
            open_sensor_state: bool,
            closed_sensor_state: bool,
        ):
        if open_sensor_state and not closed_sensor_state:
            open_door(self)
            # self.data_logger.info(f"DOOR:{self.name}:opened")
            return
        if not open_sensor_state and closed_sensor_state:
            close_door(self)
            # self.data_logger.info(f"DOOR:{self.name}:closed")
            return
        if not open_sensor_state and not closed_sensor_state:
            self.status = GarageStatus.unknown
            # self.debug_logger.debug(msg=f"{self} is neither Open nor Closed")
            # self.data_logger.info(f"DOOR:{self.name}:Unknown")
            return
        if open_sensor_state and closed_sensor_state:
            msg = f"For door {self}, both Open and Closed Sensors are Active"
            self.debug_logger.debug(msg=msg)
            raise ValueError(msg)
        raise SyntaxError(f"Should never get here")

    def time_as_status(self) -> dt.timedelta:
        now_time = dt.datetime.now(tz=TIME_ZONE)
        return now_time - self.status_change_time

    def __str__(self) -> str:
        return f"{self.name} garage has been {self.status.name} for {self.time_as_status().total_seconds():.0f} seconds"


def open_door(door: GarageDoor) -> None:
    door.status = GarageStatus.open
    door.status_change_time = dt.datetime.now(tz=TIME_ZONE)
    msg = f"Open Door: {door.name}"
    door.debug_logger.debug(msg=msg)


def close_door(door: GarageDoor) -> None:
    door.status = GarageStatus.closed
    door.status_change_time = dt.datetime.now(tz=TIME_ZONE)
    msg = f"Close Door: {door.name}"
    door.debug_logger.debug(msg=msg)


def un_open_door(door: GarageDoor) -> None:
    door.status = GarageStatus.unknown
    door.status_change_time = dt.datetime.now(tz=TIME_ZONE)
    msg = f"Un-Open Door: {door.name}"
    door.debug_logger.debug(msg=msg)


def un_close_door(door: GarageDoor) -> None:
    door.status = GarageStatus.unknown
    door.status_change_time = dt.datetime.now(tz=TIME_ZONE)
    msg = f"Un-Close Door: {door.name}"
    door.debug_logger.debug(msg=msg)


if __name__ == "__main__":
    import time

    a_door = GarageDoor(name="2-Car")
    print(a_door)
    a_door.close()
    print(a_door)
    time.sleep(3.5)
    print(a_door)
