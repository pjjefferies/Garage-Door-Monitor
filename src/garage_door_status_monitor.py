from dataclasses import dataclass
import datetime as dt
from enum import Enum
from functools import partial
from typing import Callable

from gpiozero import DigitalInputDevice

from src.config.config_main import cfg
from src.config.config_logging import history_logger  # , logger
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


def door_op(
    door: GarageDoor, door_op: Callable[[GarageDoor], None], action: GarageStatus
) -> None:
    # Change status of door
    door_op(door)

    # Log status change of door
    history_logger.info(msg=f"{door.name}, {action.name}")


def main() -> None:

    two_car_garage = GarageDoor(
        name=GarageDoorName.two_car.name, status=GarageStatus.unknown
    )
    one_car_garage = GarageDoor(
        name=GarageDoorName.one_car.name, status=GarageStatus.unknown
    )

    door_sensor_2_car_closed = DigitalInputDevice(
        cfg.SENSOR_GPIO_PINS.TWO_CAR.CLOSED.NUMBER,
        pull_up=cfg.SENSOR_GPIO_PINS.TWO_CAR.CLOSED.PULL_UP,
        bounce_time=cfg.SENSOR_GPIO_PINS.TWO_CAR.CLOSED.BOUNCE_TIME,
    )
    door_sensor_2_car_opened = DigitalInputDevice(
        cfg.SENSOR_GPIO_PINS.TWO_CAR.OPEN.NUMBER,
        pull_up=cfg.SENSOR_GPIO_PINS.TWO_CAR.OPEN.PULL_UP,
        bounce_time=cfg.SENSOR_GPIO_PINS.TWO_CAR.OPEN.BOUNCE_TIME,
    )
    door_sensor_1_car_closed = DigitalInputDevice(
        cfg.SENSOR_GPIO_PINS.ONE_CAR.CLOSED.NUMBER,
        pull_up=cfg.SENSOR_GPIO_PINS.ONE_CAR.CLOSED.PULL_UP,
        bounce_time=cfg.SENSOR_GPIO_PINS.ONE_CAR.CLOSED.BOUNCE_TIME,
    )
    door_sensor_1_car_opened = DigitalInputDevice(
        cfg.SENSOR_GPIO_PINS.ONE_CAR.OPEN.NUMBER,
        pull_up=cfg.SENSOR_GPIO_PINS.ONE_CAR.OPEN.PULL_UP,
        bounce_time=cfg.SENSOR_GPIO_PINS.ONE_CAR.OPEN.BOUNCE_TIME,
    )

    door_sensor_2_car_closed.when_activated = partial(
        door_op, door=two_car_garage, door_op=close_door, action=GarageStatus.closed
    )
    door_sensor_2_car_closed.when_deactivated = partial(
        door_op,
        door=two_car_garage,
        door_op=un_close_door,
        action=GarageStatus.un_closed,
    )
    door_sensor_2_car_opened.when_activated = partial(
        door_op, door=two_car_garage, door_op=open_door, action=GarageStatus.open
    )
    door_sensor_2_car_opened.when_deactivated = partial(
        door_op, door=two_car_garage, door_op=un_open_door, action=GarageStatus.un_open
    )

    door_sensor_1_car_closed.when_activated = partial(
        door_op, door=one_car_garage, door_op=close_door, action=GarageStatus.closed
    )
    door_sensor_1_car_closed.when_deactivated = partial(
        door_op,
        door=one_car_garage,
        door_op=un_close_door,
        action=GarageStatus.un_closed,
    )
    door_sensor_1_car_opened.when_activated = partial(
        door_op, door=one_car_garage, door_op=open_door, action=GarageStatus.open
    )
    door_sensor_1_car_opened.when_deactivated = partial(
        door_op, door=one_car_garage, door_op=un_open_door, action=GarageStatus.un_open
    )


if __name__ == "__main__":
    main()
