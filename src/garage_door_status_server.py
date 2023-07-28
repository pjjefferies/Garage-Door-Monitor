from datetime import datetime
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel


class GarageStatus(BaseModel):
    timestamp: datetime
    door_no: int
    door_position: str


def garage_door_status_server():
    garage_door_history: list[GarageStatus] = []
    garage_doors: dict[int, str] = {}  # Garage door number and current status

    app = FastAPI()

    @app.get("/")
    def read_root():
        return {"Hello": "World"}

    @app.get("/status/{door_number}")
    def read_item(door_number: Optional[int] = None):
        if not garage_doors:
            return "There are no garage doors to report statuses on."
        if door_number is None:  # return all
            return "\n".join(
                [
                    f"Door {num} status: {status}"
                    for num, status in enumerate(garage_door_numbers)
                ]
            )
        if door_number not in garage_doors:
            return f"There are no statuses of garage door {door_number} to report."
        return f"Door {door_number} status: {garage_doors[door_number]}"


if __name__ == "__main__":
    garage_door_status_server()
