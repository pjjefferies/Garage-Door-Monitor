from dataclasses import dataclass
import datetime as dt
from enum import Enum
from time import sleep

from box import Box
from typing import Protocol

import pytz

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
    app_cfg: Box
    door_cfg: Box
    debug_logger: LoggerProto
    history_logger: LoggerProto

    def __post_init__(self) -> None:
        self.status_change_time: dt.datetime = dt.datetime.now(tz=TIME_ZONE)
        self.old_state: GarageStatus = GarageStatus.undefined  # prime
        self.old_state = self.state
        self.open_time_limit = self.door_cfg.OPEN.TIME_LIMIT  # reset to baseline
        self.last_open_alarm: int = 1_000  # minutes (a really big no.)
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
                self.open_time_limit = (
                    self.door_cfg.OPEN.TIME_LIMIT
                )  # reset to baseline
                msg = f"DOOR:{self.name}:closed"
                self.debug_logger.debug(msg=msg)
                self.history_logger.info(msg=msg)
            return GarageStatus.closed
        if not self.open_sensor.value and not self.closed_sensor.value:
            self.debug_logger.debug(
                msg=f"Door, {self.name}, neither open nor closed, pausing and rechecking"
            )
            # Give door a chance to finish opening or closing
            sleep(self.app_cfg.DOOR_MIDSTATE_RE_EVAL_TIME)
            if self.open_sensor.value or self.closed_sensor.value:
                self.debug_logger.debug(
                    msg=f"Door, {self.name}, is now open and/or closed"
                )
                return self.state  # if open or closed, recursively run state
            if self.old_state != GarageStatus.unknown:
                self.status_change_time = dt.datetime.now(tz=TIME_ZONE)
                self.old_state = GarageStatus.unknown
                self.open_time_limit = (
                    self.door_cfg.OPEN.TIME_LIMIT
                )  # reset to baseline
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

    @property
    def door_open_longer_than_time_limit(self) -> bool:
        if (
            self.state == GarageStatus.open
            and self.time_at_state > self.door_cfg.OPEN.TIME_LIMIT
            and self.last_open_alarm > self.door_cfg.OPEN.ALARM_SPACING
        ):
            self.open_time_limit = (
                self.open_time_limit * self.door_cfg.OPEN.ALARM_INC_MULT
                + self.door_cfg.OPEN.ALARM_INC_ADD
            )
            return True
        return False

    def __str__(self) -> str:
        return f"DOOR:{self.name}:{self.state.name}"
