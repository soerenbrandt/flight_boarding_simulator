""""""


class Passenger(object):
    def __init__(self, row: int, seat: int):
        self.target_row = row
        self.seat = seat

        self.current_row = None

    @property
    def arrived_at_row(self) -> bool:
        return self.current_row == self.target_row

    @property
    def row(self):
        return self.target_row

    def board(self) -> None:
        """Sets the row counter to -1 so that the next row is row 0."""
        self.current_row = -1

    def move(self) -> None:
        """Moves forward 1 row."""
        try:
            self.current_row += 1
        except TypeError:
            # The passenger has not yet boarded. Skip.
            pass
