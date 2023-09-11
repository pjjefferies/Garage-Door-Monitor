import signal
from typing import Any, Optional, Protocol


class LoggerProto(Protocol):
    def debug(self, msg: str) -> None:
        ...

    def info(self, msg: str) -> None:
        ...


def exit_handler(
    signum: Optional[signal.Signals] = None,
    frame: Optional[signal.Handlers] = None,
    logger: Optional[LoggerProto] = None,
    history_logger: Optional[LoggerProto] = None,
) -> Any:
    msg = "Stopping Garage Door Monitor"
    if logger:
        logger.info(msg=msg)
    if history_logger:
        history_logger.info(msg=msg)
    exit(0)
