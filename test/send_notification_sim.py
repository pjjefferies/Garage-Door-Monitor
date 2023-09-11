from typing import Protocol


class LoggerProto(Protocol):
    def debug(self, msg: str) -> None:
        ...

    def info(self, msg: str) -> None:
        ...


def send_notification(*, msg: str = "Test notification", logger: LoggerProto):
    logger.debug(msg=f"send_notification TEST MESSAGE: {msg}")
