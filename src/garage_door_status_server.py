import datetime as dt
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

ALLOWED_POSITIONS: list[str] = ["Opened", "Closed"]


class GarageStatus(BaseModel):
    timestamp: dt.datetime
    door_no: int
    door_position: str


def garage_door_test_history() -> list[GarageStatus]:
    garage_door_history_test1: list[GarageStatus] = [
        GarageStatus(
            timestamp=dt.datetime(2023, 1, 1, 6, 0, 0),
            door_no=1,
            door_position="Closed",
        ),
        GarageStatus(
            timestamp=dt.datetime(2023, 1, 1, 6, 0, 1),
            door_no=2,
            door_position="Closed",
        ),
        GarageStatus(
            timestamp=dt.datetime(2023, 1, 1, 7, 0, 0),
            door_no=1,
            door_position="Opened",
        ),
        GarageStatus(
            timestamp=dt.datetime(2023, 1, 1, 7, 2, 0),
            door_no=1,
            door_position="Closed",
        ),
        GarageStatus(
            timestamp=dt.datetime(2023, 1, 1, 10, 0, 0),
            door_no=2,
            door_position="Opened",
        ),
        GarageStatus(
            timestamp=dt.datetime(2023, 1, 1, 11, 30, 0),
            door_no=2,
            door_position="Closed",
        ),
        GarageStatus(
            timestamp=dt.datetime(2023, 1, 1, 16, 30, 0),
            door_no=2,
            door_position="Opened",
        ),
        GarageStatus(
            timestamp=dt.datetime(2023, 1, 1, 16, 40, 0),
            door_no=2,
            door_position="Closed",
        ),
        GarageStatus(
            timestamp=dt.datetime(2023, 1, 1, 17, 30, 0),
            door_no=2,
            door_position="Opened",
        ),
        GarageStatus(
            timestamp=dt.datetime(2023, 1, 1, 17, 40, 0),
            door_no=2,
            door_position="Closed",
        ),
        GarageStatus(
            timestamp=dt.datetime(2023, 1, 1, 19, 30, 0),
            door_no=1,
            door_position="Opened",
        ),
        GarageStatus(
            timestamp=dt.datetime(2023, 1, 1, 19, 32, 0),
            door_no=1,
            door_position="Closed",
        ),
    ]
    return garage_door_history_test1


garage_door_history: list[GarageStatus] = []
garage_door_status: dict[int, str] = {}  # Garage door number and current status

# Add test data
garage_door_history = garage_door_test_history()
# reset_door_status()

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/status/")
def report_door_status(door_number: Optional[int] = None) -> str:
    if not garage_door_status:
        return "There are no garage doors to report status on"
    if door_number is None:  # return all
        return ", ".join(
            [
                f"Door {num} status: {status}"
                for num, status in garage_door_status.items()
            ]
        )
    if door_number not in garage_door_status:
        return f"There are no status of garage door {door_number} to report"
    return f"Door {door_number} status: {garage_door_status[door_number]}"


@app.get("/reset_door_status/")
def reset_door_status() -> str:
    global garage_door_status
    garage_door_status = {}
    for garage_door_event in garage_door_history:
        garage_door_status[garage_door_event.door_no] = garage_door_event.door_position
    return report_door_status()


reset_door_status()


@app.get("/register_event/")
def save_garage_status(
    door_number: int = 1,
    position: str = "Closed",
    timestamp: dt.datetime = dt.datetime(2023, 7, 31, 6, 45, 00),
) -> str:
    global garage_door_history
    global garage_door_status
    if position not in ALLOWED_POSITIONS:
        return f"Position must be in ({', '.join(ALLOWED_POSITIONS)}). Received: {position}"
    this_status = GarageStatus(
        timestamp=timestamp, door_no=door_number, door_position=position
    )
    garage_door_history.append(this_status)

    garage_door_status[door_number] = position

    return str(this_status)


@app.get("/garage_door_history/")
def return_garage_door_history(no_events: Optional[int] = None) -> str:
    if no_events is None:
        result: str = "\n".join([str(status) for status in garage_door_history])
    else:
        result = "\n".join([str(status) for status in garage_door_history[:-no_events]])
    return result


if __name__ == "__main__":
    uvicorn.run(
        "garage_door_status_server:app",
        host="192.168.1.25",
        port=8000,
        reload=True,
        access_log=True,
    )
