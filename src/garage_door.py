from dataclasses import dataclass
import datetime as dt
from enum import Enum

from typing import Protocol  # Optional

import pytz

from src.config.config_logging import logger

TIME_ZONE = pytz.timezone(zone="America/Detroit")


class DigitalSensorProto(Protocol):
    value: bool


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
    undefined = 6


@dataclass
class GarageDoor:
    name: str
    open_sensor: DigitalSensorProto
    closed_sensor: DigitalSensorProto
    debug_logger: LoggerProto
    history_logger: LoggerProto

    def __post_init__(self):
        self.status_change_time: dt.datetime = dt.datetime.now(tz=TIME_ZONE)
        self.old_state: GarageStatus = GarageStatus.undefined  # prime
        self.old_state: GarageStatus = self.state
        msg = f"DOOR:{self.name}:created"
        self.debug_logger.debug(msg=msg)
        self.history_logger.info(msg=msg)

    @property
    def state(self) -> GarageStatus:
        if self.open_sensor.value and not self.closed_sensor.value:
            if self.old_state != GarageStatus.open:
                self.status_change_time = dt.datetime.now(tz=TIME_ZONE)
                self.old_state = GarageStatus.open
                msg = f"DOOR:{self.name}:opened"
                self.debug_logger.debug(msg=msg)
                self.history_logger.info(msg=msg)
            return GarageStatus.open
        if not self.open_sensor.value and self.closed_sensor.value:
            if self.old_state != GarageStatus.closed:
                self.status_change_time = dt.datetime.now(tz=TIME_ZONE)
                self.old_state = GarageStatus.closed
                msg = f"DOOR:{self.name}:closed"
                self.debug_logger.debug(msg=msg)
                self.history_logger.info(msg=msg)
            return GarageStatus.closed
        if not self.open_sensor.value and not self.closed_sensor.value:
            if self.old_state != GarageStatus.unknown:
                self.status_change_time = dt.datetime.now(tz=TIME_ZONE)
                self.old_state = GarageStatus.unknown
                msg = f"DOOR:{self.name}:unknown"
                self.debug_logger.debug(msg=msg)
                self.history_logger.info(msg=msg)
            return GarageStatus.unknown
        if self.open_sensor.value and self.closed_sensor.value:
            msg = f"For door {self}, both Open and Closed Sensors are Active"
            self.debug_logger.debug(msg=msg)
            self.history_logger.info(msg=msg)
            return GarageStatus.unknown
        raise SyntaxError(f"Should never get here")

    @property
    def time_at_state(self) -> int:  # seconds
        now_time = dt.datetime.now(tz=TIME_ZONE)
        return int((now_time - self.status_change_time).total_seconds())

    def __str__(self) -> str:
        return f"DOOR:{self.name}:{self.status.name}"


if __name__ == "__main__":
    import time

    a_door = GarageDoor(name="2-Car")
    print(a_door)
    a_door.close()
    print(a_door)
    time.sleep(3.5)
    print(a_door)
