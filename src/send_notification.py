import requests
from typing import Protocol

from security.keys import IFTTT_EVENT, IFTTT_KEY, IFTTT_MSG_VAR


class LoggerProto(Protocol):
    def debug(self, msg: str) -> None:
        ...

    def info(self, msg: str) -> None:
        ...


address: str = f"https://maker.ifttt.com/trigger/{IFTTT_EVENT}/with/key/{IFTTT_KEY}"


def send_notification(*, msg: str = "Test notification", logger: LoggerProto):
    requests.post(address, data={f"{IFTTT_MSG_VAR}": f"{msg}"})
    logger.debug(msg=f"{IFTTT_MSG_VAR}: {msg}")
