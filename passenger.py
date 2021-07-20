""""""

from airplane import Seat


class Passenger(object):
    def __init__(self, seat: Seat):
        self._seat = seat

        self.current_row = None

    def __lt__(self, other):
        return self._seat < other._seat

    def __gt__(self, other):
        return self._seat > other._seat

    @property
    def row(self):
        return self._seat.row

    @property
    def seat(self):
        return self._seat.seat

    @property
    def arrived_at_row(self) -> bool:
        return self.current_row == self.row

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
