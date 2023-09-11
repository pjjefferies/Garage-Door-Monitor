import signal
from time import sleep
from typing import Any, Protocol

from box import Box

# from src.send_notification import send_notification
# from src.config.config_main import load_config
# from src.config.config_logging import logger
# from src.garage_door import GarageDoor
import src.garage_door_status_monitor
from src.exit_handler import exit_handler

from test.config.config_test_logging import history_test_logger as history_logger
from src.config.config_logging import logger
from test.config.config_test_main import test_cfg
from test.send_notification_sim import send_notification
from test.digital_input_dev_sim import DoorSensorSim as DoorSensor


class LoggerProto(Protocol):
    def debug(self, msg: str) -> None:
        ...

    def info(self, msg: str) -> None:
        ...


def test_garage_door() -> None:
    global logger, history_logger, send_notification, DoorSensor
    msg: str = f"Starting Garage Door Monitor Test"
    history_logger.info(msg=msg)
    logger.debug(msg=msg)

    src.garage_door_status_monitor.garage_door_status_monitor(
        DoorSensor=DoorSensor,
        send_notification=send_notification,
        logger=logger,
        history_logger=history_logger,
        max_run_time=2200,
    )


if __name__ == "__main__":
    test_garage_door()
