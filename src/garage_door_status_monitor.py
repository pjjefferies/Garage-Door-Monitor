from dataclasses import dataclass
import datetime as dt

# from typing import Optional

from src.garage_door import GarageDoor, GarageStatus


@dataclass
class GarageStatusHistoryDatum:
    name: str
    position: GarageStatus
    timestamp: dt.datetime


garage_door_history: list[GarageStatus] = []
garage_doors: list[GarageDoor] = []


if __name__ == "__main__":
    pass
