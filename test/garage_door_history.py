import datetime as dt

# from typing import Protocol

from src.garage_door import GarageStatus
from src.garage_door_status_monitor import GarageStatusHistoryDatum


def garage_door_test_history() -> list[GarageStatusHistoryDatum]:
    garage_door_history_test1: list[GarageStatusHistoryDatum] = [
        GarageStatusHistoryDatum(
            name="2-Car",
            position=GarageStatus.closed,
            timestamp=dt.datetime(2023, 1, 1, 6, 0, 0),
        ),
        GarageStatusHistoryDatum(
            name="1-Car",
            position=GarageStatus.closed,
            timestamp=dt.datetime(2023, 1, 1, 6, 0, 1),
        ),
        GarageStatusHistoryDatum(
            name="2-Car",
            position=GarageStatus.unknown,
            timestamp=dt.datetime(2023, 1, 1, 6, 59, 50),
        ),
        GarageStatusHistoryDatum(
            name="2-Car",
            position=GarageStatus.open,
            timestamp=dt.datetime(2023, 1, 1, 7, 0, 0),
        ),
        GarageStatusHistoryDatum(
            name="2-Car",
            position=GarageStatus.unknown,
            timestamp=dt.datetime(2023, 1, 1, 7, 1, 50),
        ),
        GarageStatusHistoryDatum(
            name="2-Car",
            position=GarageStatus.closed,
            timestamp=dt.datetime(2023, 1, 1, 7, 2, 0),
        ),
        GarageStatusHistoryDatum(
            name="1-Car",
            position=GarageStatus.unknown,
            timestamp=dt.datetime(2023, 1, 1, 10, 59, 50),
        ),
        GarageStatusHistoryDatum(
            name="1-Car",
            position=GarageStatus.open,
            timestamp=dt.datetime(2023, 1, 1, 10, 0, 0),
        ),
        GarageStatusHistoryDatum(
            name="1-Car",
            position=GarageStatus.unknown,
            timestamp=dt.datetime(2023, 1, 1, 11, 29, 50),
        ),
        GarageStatusHistoryDatum(
            name="1-Car",
            position=GarageStatus.closed,
            timestamp=dt.datetime(2023, 1, 1, 11, 30, 0),
        ),
        GarageStatusHistoryDatum(
            name="1-Car",
            position=GarageStatus.unknown,
            timestamp=dt.datetime(2023, 1, 1, 16, 29, 50),
        ),
        GarageStatusHistoryDatum(
            name="1-Car",
            position=GarageStatus.open,
            timestamp=dt.datetime(2023, 1, 1, 16, 30, 0),
        ),
        GarageStatusHistoryDatum(
            name="1-Car",
            position=GarageStatus.unknown,
            timestamp=dt.datetime(2023, 1, 1, 16, 39, 50),
        ),
        GarageStatusHistoryDatum(
            name="1-Car",
            position=GarageStatus.closed,
            timestamp=dt.datetime(2023, 1, 1, 16, 40, 0),
        ),
        GarageStatusHistoryDatum(
            name="1-Car",
            position=GarageStatus.unknown,
            timestamp=dt.datetime(2023, 1, 1, 17, 29, 50),
        ),
        GarageStatusHistoryDatum(
            name="1-Car",
            position=GarageStatus.open,
            timestamp=dt.datetime(2023, 1, 1, 17, 30, 0),
        ),
        GarageStatusHistoryDatum(
            name="1-Car",
            position=GarageStatus.unknown,
            timestamp=dt.datetime(2023, 1, 1, 17, 39, 50),
        ),
        GarageStatusHistoryDatum(
            name="1-Car",
            position=GarageStatus.closed,
            timestamp=dt.datetime(2023, 1, 1, 17, 40, 0),
        ),
        GarageStatusHistoryDatum(
            name="2-Car",
            position=GarageStatus.unknown,
            timestamp=dt.datetime(2023, 1, 1, 19, 29, 50),
        ),
        GarageStatusHistoryDatum(
            name="2-Car",
            position=GarageStatus.open,
            timestamp=dt.datetime(2023, 1, 1, 19, 30, 0),
        ),
        GarageStatusHistoryDatum(
            name="2-Car",
            position=GarageStatus.unknown,
            timestamp=dt.datetime(2023, 1, 1, 19, 31, 50),
        ),
        GarageStatusHistoryDatum(
            name="2-Car",
            position=GarageStatus.closed,
            timestamp=dt.datetime(2023, 1, 1, 19, 32, 0),
        ),
    ]
    return garage_door_history_test1


garage_door_history_test1 = garage_door_test_history()
