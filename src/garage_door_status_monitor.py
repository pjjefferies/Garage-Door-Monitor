from dataclasses import dataclass
import datetime as dt
import signal
from time import sleep
from typing import Any, Protocol

from box import Box
from gpiozero import DigitalInputDevice

from src.send_notification import send_notification
from src.config.config_main import load_config
from src.config.config_logging import history_logger
from src.config.config_logging import logger
from src.garage_door import (
    GarageDoor,
    GarageStatus,
)


class LoggerProto(Protocol):
    def debug(self, msg: str) -> None:
        ...

    def info(self, msg: str) -> None:
        ...


@dataclass
class GarageStatusHistoryDatum:
    name: str
    position: GarageStatus
    timestamp: dt.datetime


def exit_handler(signum: signal.Signals, frame: signal.Handlers) -> Any:
    msg = "Stopping Garage Door Monitor"
    logger.info(msg=msg)
    history_logger.info(msg=msg)
    exit(0)


def main() -> None:
    global logger, history_logger
    msg: str = f"Starting Garage Door Monitor"
    history_logger.info(msg=msg)
    logger.debug(msg=msg)
    cfg: Box = load_config()
    garage_door_config: Box = cfg.DOORS
    garage_doors: Box = Box({})
    for a_door_name in garage_door_config.keys():
        garage_doors[a_door_name] = Box({})

    # Create DigitalInputDevice Door Open/Closed Sensors
    for garage_door in garage_door_config.keys():
        garage_doors[garage_door]["open_sensor"] = DigitalInputDevice(
            pin=int(garage_door_config[garage_door].OPEN.NUMBER),
            pull_up=garage_door_config[garage_door].OPEN.PULL_UP,
            bounce_time=garage_door_config[garage_door].OPEN.BOUNCE_TIME,
        )
        garage_doors[garage_door]["closed_sensor"] = DigitalInputDevice(
            pin=int(garage_door_config[garage_door].CLOSED.NUMBER),
            pull_up=garage_door_config[garage_door].CLOSED.PULL_UP,
            bounce_time=garage_door_config[garage_door].CLOSED.BOUNCE_TIME,
        )

    # Create GarageDoor Objects
    for garage_door in garage_door_config.keys():
        garage_doors[garage_door]["DoorObject"] = GarageDoor(
            name=garage_door,
            open_sensor=garage_doors[garage_door]["open_sensor"],
            closed_sensor=garage_doors[garage_door]["closed_sensor"],
            door_cfg=garage_door_config[garage_door],
            debug_logger=logger,
            history_logger=history_logger,
        )

    # Register the exit handler with `SIGINT`(CTRL + C)
    signal.signal(signalnum=signal.SIGINT, handler=exit_handler)
    # Register the exit handler with `SIGTSTP` (Ctrl + Z)
    signal.signal(signalnum=signal.SIGTSTP, handler=exit_handler)

    # Initialize some stuff
    for garage_door in garage_doors.keys():
        garage_doors[garage_door]["open_alarm_last_time"] = dt.datetime(1970, 1, 1, 8)
        garage_doors[garage_door]["open_alarm_time_since_notify"] = 0
        garage_doors[garage_door]["door_time_time_open"] = 0
        garage_doors[garage_door]["next_alarm_time_increment"] = garage_door_config[
            garage_door
        ]["next_alarm_time_increment"]

    while True:
        # Check if garages have been open for more than X minutes (from config)
        for garage_door in garage_door_config.keys():
            if garage_doors[garage_door]["DoorObject"].door_open_longer_than_time_limit:
                send_notification(
                    msg=(
                        f"{garage_doors[garage_door]['DoorObject'].name} open for "
                    ),
                    logger=logger,
                )

            # Other checks TBD?

        sleep(cfg.APP.LOOP_DELAY)
        cfg = load_config()  # reload so that loop delay can be changed for dev.


if __name__ == "__main__":
    main()
