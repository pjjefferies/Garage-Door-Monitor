import datetime as dt
from functools import partial
import signal
from time import sleep
from typing import Callable, Optional, Protocol

from box import Box

from src.config.config_main import load_config
from src.exit_handler import exit_handler
from src.garage_door import GarageDoor


class DoorSensorProto(Protocol):
    value: bool


class LoggerProto(Protocol):
    def debug(self, msg: str) -> None:
        ...

    def info(self, msg: str) -> None:
        ...


def garage_door_status_monitor(
    DoorSensor: DoorSensorProto,
    send_notification: Callable[[str], None],
    logger: LoggerProto,
    history_logger: LoggerProto,
    max_run_time: Optional[int] = None,
) -> None:
    msg: str = f"Starting Garage Door Monitor"
    history_logger.info(msg=msg)
    logger.debug(msg=msg)
    cfg: Box = load_config()
    garage_door_config: Box = cfg.DOORS
    garage_doors: Box = Box({})
    start_time: dt.datetime = dt.datetime.now()

    # Create DigitalInputDevice Door Open/Closed Sensors
    for garage_door in garage_door_config.keys():
        garage_doors[garage_door] = Box({})
        for sensor in garage_door_config[garage_door].keys():
            garage_doors[garage_door][
                garage_door_config[garage_door][sensor].NAME
            ] = DoorSensor(
                pin=int(garage_door_config[garage_door][sensor].NUMBER),
                pull_up=garage_door_config[garage_door][sensor].PULL_UP,
                bounce_time=garage_door_config[garage_door][sensor].BOUNCE_TIME,
            )

    # Create GarageDoor Objects
    for garage_door in garage_door_config.keys():
        garage_doors[garage_door]["DoorObject"] = GarageDoor(
            name=garage_door,
            open_sensor=garage_doors[garage_door]["open_sensor"],
            closed_sensor=garage_doors[garage_door]["closed_sensor"],
            load_config=load_config,
            debug_logger=logger,
            history_logger=history_logger,
        )

    # Register the exit handler with `SIGINT`(CTRL + C)
    signal.signal(
        signalnum=signal.SIGINT,
        handler=partial(exit_handler, logger=logger, history_logger=history_logger),
    )

    try:
        # Register the exit handler with `SIGTSTP` (Ctrl + Z)
        signal.signal(
            signalnum=signal.SIGTSTP,
            handler=partial(exit_handler, logger=logger, history_logger=history_logger),
        )
    except AttributeError:  # doesn't work in windows for testing
        pass

    # Main Loop
    while True:
        if max_run_time and (
            (dt.datetime.now() - start_time).total_seconds() > max_run_time
        ):
            msg = f"Max. run time of {max_run_time} exceeded. Closing Monitor"
            logger.debug(msg=msg)
            history_logger.info(msg=msg)
            exit_handler(logger=logger, history_logger=history_logger)

        # Check if garages have been open for more than X minutes (from config)
        for garage_door in garage_door_config.keys():
            if garage_doors[garage_door]["DoorObject"].door_open_longer_than_time_limit:
                send_notification(
                    msg=(
                        f"{garage_doors[garage_door]['DoorObject'].name} open for "
                        f"{garage_doors[garage_door]['DoorObject'].seconds_at_state // 60} minutes"
                    ),
                    logger=logger,
                )

            # Other checks TBD?

        sleep(cfg.APP.LOOP_DELAY)
        cfg = load_config()  # reload so that loop delay can be changed for dev.


if __name__ == "__main__":
    from gpiozero import DigitalInputDevice as DoorSensor

    from src.config.config_logging import history_logger
    from src.config.config_logging import logger
    from src.send_notification import send_notification

    garage_door_status_monitor(
        DoorSensor=DoorSensor,
        send_notification=send_notification,
        logger=logger,
        history_logger=history_logger,
    )
