from dataclasses import dataclass
import datetime as dt
from enum import Enum
from time import sleep

from box import Box
from typing import Callable, Protocol

import pytz


class DoorSensorProto(Protocol):
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
    open_sensor: DoorSensorProto
    closed_sensor: DoorSensorProto
    load_config: Callable[[], Box]
    debug_logger: LoggerProto
    history_logger: LoggerProto

    def __post_init__(self) -> None:
        self.old_state: GarageStatus = GarageStatus.undefined  # prime
        self.app_cfg: Box = self.load_config().APP
        self.TIME_ZONE = pytz.timezone(zone=self.app_cfg.TIME_ZONE)
        self.status_change_time: dt.datetime = dt.datetime.now(self.TIME_ZONE)
        self.door_cfg: Box = self.load_config().DOORS[self.name]
        self.open_time_limit = self.door_cfg.OPEN.TIME_LIMIT  # reset to baseline
        self.last_alarm_time: dt.datetime = dt.datetime.now() - dt.timedelta(
            weeks=52
        )  # a long time ago
        msg = f"DOOR:{self.name}:created"
        self.debug_logger.debug(msg=msg)
        self.history_logger.info(msg=msg)

    @property
    def state(self) -> GarageStatus:
        sensor_open_value: bool = bool(self.open_sensor.value)
        sensor_closed_value: bool = bool(self.closed_sensor.value)
        match (sensor_open_value, sensor_closed_value):
            case (True, False):  # DOOR IS OPEN!
                if self.old_state != GarageStatus.open:
                    self.status_change_time = dt.datetime.now(self.TIME_ZONE)
                    self.old_state = GarageStatus.open  # for the next time
                    msg = f"DOOR:{self.name}:opened"
                    self.debug_logger.debug(msg=msg)
                    self.history_logger.info(msg=msg)
                return GarageStatus.open
            case (False, True):  # DOOR IS CLOSED!
                if self.old_state != GarageStatus.closed:
                    self.status_change_time = dt.datetime.now(self.TIME_ZONE)
                    self.old_state = GarageStatus.closed  # for the next time
                    msg = f"DOOR:{self.name}:closed"
                    self.debug_logger.debug(msg=msg)
                    self.history_logger.info(msg=msg)
                # Reset open_time_limit to baseline
                self.open_time_limit = self.door_cfg.OPEN.TIME_LIMIT
                return GarageStatus.closed
            case (False, False):  # DOOR IS NEITHER OPEN NOR CLOSED!
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
                    self.status_change_time = dt.datetime.now(self.TIME_ZONE)
                    self.old_state = GarageStatus.unknown  # for the next time
                    msg = f"DOOR:{self.name}:unknown"
                    self.debug_logger.debug(msg=msg)
                    self.history_logger.info(msg=msg)
                return GarageStatus.unknown
            case (True, True):  # DOOR IS BOTH OPEN AND CLOSED, PLEASE DRIVE THROUGH!
                msg = f"For door {self}, both Open and Closed Sensors are Active"
                self.debug_logger.debug(msg=msg)
                self.history_logger.info(msg=msg)
                return GarageStatus.unknown
            case _:
                raise SyntaxError(
                    f"Should never get here. {sensor_open_value=}, {sensor_closed_value=}"
                )

    @property
    def seconds_at_state(self) -> int:
        now_time = dt.datetime.now(self.TIME_ZONE)
        time_delta: int = int((now_time - self.status_change_time).total_seconds())
        self.debug_logger.debug(f"{self.name}:seconds_at_state: {time_delta} seconds")
        return time_delta

    @property
    def door_open_longer_than_time_limit(self) -> bool:
        self.door_cfg = self.load_config().DOORS[self.name]
        time_since_last_open_alarm = (
            dt.datetime.now() - self.last_alarm_time
        ).total_seconds()
        if (
            # Is door open?
            self.state == GarageStatus.open
            # comparing minutes - Has door been open long enough?
            and self.seconds_at_state > self.door_cfg.OPEN.TIME_LIMIT
            # comparing minutes - Has it been long enough since last alarm?
            and time_since_last_open_alarm > self.open_time_limit
        ):
            # Reset last alarm time
            self.last_alarm_time = dt.datetime.now()
            # Increase open_time_limit for next alarm
            self.open_time_limit = (
                self.open_time_limit * self.door_cfg.OPEN.ALARM_INC_MULT
                + self.door_cfg.OPEN.ALARM_INC_ADD
            )
            self.debug_logger.debug(
                msg=(
                    f"door_open_longer_than_time_limit=True. "
                    f"Increasing open_time_limit to {self.open_time_limit} seconds."
                )
            )
            return True
        return False

    def __str__(self) -> str:
        return f"DOOR:{self.name}:{self.state.name}"
