from dataclasses import dataclass
import datetime as dt
from enum import Enum

# from typing import Optional

import pytz

TIME_ZONE = pytz.timezone(zone="America/Detroit")


class GarageStatus(Enum):
    open = 1
    unknown = 2
    closed = 3


@dataclass
class GarageDoor:
    name: str
    status: GarageStatus = GarageStatus.unknown

    def __post_init__(self):
        self.status_change_time: dt.datetime = dt.datetime.now(tz=TIME_ZONE)

    def open(self) -> None:
        self.status = GarageStatus.open
        self.status_change_time = dt.datetime.now(tz=TIME_ZONE)

    def un_open(self) -> None:
        self.status = GarageStatus.unknown
        self.status_change_time = dt.datetime.now(tz=TIME_ZONE)

    def un_close(self) -> None:
        self.status = GarageStatus.unknown
        self.status_change_time = dt.datetime.now(tz=TIME_ZONE)

    def close(self) -> None:
        self.status = GarageStatus.closed
        self.status_change_time = dt.datetime.now(tz=TIME_ZONE)

    def time_as_status(self) -> dt.timedelta:
        now_time = dt.datetime.now(tz=TIME_ZONE)
        return now_time - self.status_change_time

    def __str__(self) -> str:
        return f"{self.name} garage has been {self.status.name} for {self.time_as_status().total_seconds():.0f} seconds"


if __name__ == "__main__":
    import time

    a_door = GarageDoor(name="2-Car")
    print(a_door)
    a_door.close()
    print(a_door)
    time.sleep(3.5)
    print(a_door)
