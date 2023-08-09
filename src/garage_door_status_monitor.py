from dataclasses import dataclass
import datetime as dt
from enum import Enum
from functools import partial
import signal
from time import sleep
from typing import Any, Callable

from gpiozero import DigitalInputDevice

from src.config.config_main import cfg
from src.config.config_logging import history_logger, logger
from src.garage_door import (
    GarageDoor,
    GarageStatus,
    close_door,
    un_close_door,
    open_door,
    un_open_door,
)


class GarageDoorName(Enum):
    two_car = 1
    one_car = 2


@dataclass
class GarageStatusHistoryDatum:
    name: str
    position: GarageStatus
    timestamp: dt.datetime


def exit_handler(signum: signal.Signals, frame: signal.Handlers) -> Any:
    msg = "Exiting Gracefully"
    logger.info(msg=msg)
    history_logger.info(msg=msg)
    exit(0)


def door_op(
    door: GarageDoor, operation: Callable[[], None], action: GarageStatus
) -> None:
    # Change status of door
    operation()

    # Log status change of door
    print(f"DOOR:{door.name}:{action.name}")
    history_logger.info(msg=f"DOOR:{door.name}:{action.name}")


def main() -> None:
    history_logger.info(msg=f"Starting Garage Door Monitor")

    two_car_garage = GarageDoor(
        name=GarageDoorName.two_car.name,
        status=GarageStatus.unknown,
        logger=history_logger,
    )
    one_car_garage = GarageDoor(
        name=GarageDoorName.one_car.name,
        status=GarageStatus.unknown,
        logger=history_logger,
    )

    door_sensor_2_car_closed = DigitalInputDevice(
        pin=int(cfg.SENSOR_GPIO_PINS.TWO_CAR.CLOSED.NUMBER),
        pull_up=cfg.SENSOR_GPIO_PINS.TWO_CAR.CLOSED.PULL_UP,
        bounce_time=cfg.SENSOR_GPIO_PINS.TWO_CAR.CLOSED.BOUNCE_TIME,
    )
    logger.debug(f"{door_sensor_2_car_closed.value=}")

    door_sensor_2_car_opened = DigitalInputDevice(
        pin=int(cfg.SENSOR_GPIO_PINS.TWO_CAR.OPEN.NUMBER),
        pull_up=cfg.SENSOR_GPIO_PINS.TWO_CAR.OPEN.PULL_UP,
        bounce_time=cfg.SENSOR_GPIO_PINS.TWO_CAR.OPEN.BOUNCE_TIME,
    )
    logger.debug(f"{door_sensor_2_car_opened.value=}")

    door_sensor_1_car_closed = DigitalInputDevice(
        pin=cfg.SENSOR_GPIO_PINS.ONE_CAR.CLOSED.NUMBER,
        pull_up=cfg.SENSOR_GPIO_PINS.ONE_CAR.CLOSED.PULL_UP,
        bounce_time=cfg.SENSOR_GPIO_PINS.ONE_CAR.CLOSED.BOUNCE_TIME,
    )
    logger.debug(f"{door_sensor_1_car_closed.value=}")

    door_sensor_1_car_opened = DigitalInputDevice(
        pin=cfg.SENSOR_GPIO_PINS.ONE_CAR.OPEN.NUMBER,
        pull_up=cfg.SENSOR_GPIO_PINS.ONE_CAR.OPEN.PULL_UP,
        bounce_time=cfg.SENSOR_GPIO_PINS.ONE_CAR.OPEN.BOUNCE_TIME,
    )
    logger.debug(f"{door_sensor_1_car_opened.value=}")

    one_car_garage.update_status(
        open_sensor_state=door_sensor_1_car_opened.value,
        closed_sensor_state=door_sensor_1_car_closed.value,
    )
    two_car_garage.update_status(
        open_sensor_state=door_sensor_2_car_opened.value,
        closed_sensor_state=door_sensor_2_car_closed.value,
    )

    door_sensor_2_car_closed.when_activated = partial(
        door_op, two_car_garage, lambda: close_door(two_car_garage), GarageStatus.closed
    )

    door_sensor_2_car_closed.when_deactivated = partial(
        door_op,
        two_car_garage,
        lambda: un_close_door(two_car_garage),
        GarageStatus.un_closed,
    )
    door_sensor_2_car_opened.when_activated = partial(
        door_op, two_car_garage, lambda: open_door(two_car_garage), GarageStatus.open
    )
    door_sensor_2_car_opened.when_deactivated = partial(
        door_op,
        two_car_garage,
        lambda: un_open_door(two_car_garage),
        GarageStatus.un_open,
    )
    door_sensor_1_car_closed.when_activated = partial(
        door_op, one_car_garage, lambda: close_door(one_car_garage), GarageStatus.closed
    )

    door_sensor_1_car_closed.when_deactivated = partial(
        door_op,
        one_car_garage,
        lambda: un_close_door(one_car_garage),
        GarageStatus.un_closed,
    )

    door_sensor_1_car_opened.when_activated = partial(
        door_op, one_car_garage, lambda: open_door(one_car_garage), GarageStatus.open
    )

    door_sensor_1_car_opened.when_deactivated = partial(
        door_op,
        one_car_garage,
        lambda: un_open_door(one_car_garage),
        GarageStatus.un_open,
    )

    # Register the exit handler with `SIGINT`(CTRL + C)
    signal.signal(signalnum=signal.SIGINT, handler=exit_handler)

    # Register the exit handler with `SIGTSTP` (Ctrl + Z)
    signal.signal(signalnum=signal.SIGTSTP, handler=exit_handler)

    while True:
        logger.debug(msg=f"{str(one_car_garage)}, {str(two_car_garage)}")
        sleep(5)


if __name__ == "__main__":
    main()
