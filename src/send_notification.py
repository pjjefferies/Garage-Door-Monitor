import requests

from security.keys import IFTTT_EVENT, IFTTT_KEY, IFTTT_MSG_VAR

address: str = f"https://maker.ifttt.com/trigger/{IFTTT_EVENT}/with/key/{IFTTT_KEY}"


def send_notification(msg: str = "Test notification"):
    requests.post(address, data={f"{IFTTT_MSG_VAR}": f"{msg}"})
