""""""

import math


class Airplane(object):
    def __init__(self, number_of_rows: int, seats_per_row: int):
        self.number_of_rows = number_of_rows
        self.seats_per_row = seats_per_row

        self.seating_chart = self._generate_seating_chart()

    @property
    def seats(self):
        """Returns a generator for seats on the plane

        Returns:
            tuple: (row, seat) for each seat on the plane
        """
        seats = list(range(self.seats_per_row))
        seats_window_to_aisle = seats[:self._aisle] + seats[self._aisle:][::-1]
        return ((row, seat) for row in range(self.number_of_rows)
                for seat in seats_window_to_aisle)

    @property
    def window_seats(self):
        return ((row, seat) for row in range(self.number_of_rows)
                for seat in [0, self.seats_per_row - 1])

    @property
    def middle_seats(self):
        seats = set(range(self.seats_per_row))
        # remove window and aisle seats
        seats.remove(set([seat for _, seat in self.window_seats]))
        seats.remove(set([seat for _, seat in self.aisle_seats]))

        return ((row, seat) for row in range(self.number_of_rows)
                for seat in seats)

    @property
    def aisle_seats(self):
        return ((row, seat) for row in range(self.number_of_rows)
                for seat in [self._aisle, self._aisle])

    @property
    def fully_boarded(self) -> bool:
        """True if the plane is full

        Returns:
            bool
        """
        return all([all(row) for row in self.seating_chart])

    @property
    def _aisle(self) -> int:
        return self.seats_per_row // 2

    def _required_shuffles(self, passenger) -> int:
        """Determines if seating requires people to get up (seat shuffle).

        Args:
            passenger (Passenger)

        Returns:
            int: Number of people that need to get up.
        """
        aisle = self._aisle
        if passenger.seat < aisle:
            # passenger sits on the left side of the plane
            seats = self.seating_chart[passenger.row][:aisle]
            return sum(seats[passenger.seat:])
        else:
            # passenger sits on the right side of the plane
            seats = self.seating_chart[passenger.row][aisle:]
            return sum(seats[:passenger.seat - aisle])

    def seat_passenger(self, passenger) -> int:
        """Change seating for passenger seat to 1 (occupied).

        Args:
            passenger (Passenger)

        Returns:
            int: number of seat suffles
        """
        required_shuffles = self._required_shuffles(passenger)
        self.seating_chart[passenger.row][passenger.seat] = 1
        return required_shuffles

    def _generate_seating_chart(self) -> list:
        """Generate a simple seating chart.

            Airplane layout:
            row#   0  1  2  3  4  5  6  7  8  9 10 11 ...
                  ------------------------------------
            seat#  0  0  0  0  0  0  0  0  0  0  0  0 ...
            seat#  1  1  1  1  1  1  1  1  1  1  1  1 ...
            seat#  2  2  2  2  2  2  2  2  2  2  2  2 ...
                               middle aisle
            seat#  3  3  3  3  3  3  3  3  3  3  3  3 ...
            seat#  4  4  4  4  4  4  4  4  4  4  4  4 ...
            seat#  5  5  5  5  5  5  5  5  5  5  5  5 ...
                  ------------------------------------

        Returns:
            list: List of rows containing lists of seats.
        """
        seating_chart = []
        for _ in range(self.number_of_rows):
            seating_chart.append([0 for _ in range(self.seats_per_row)])

        return seating_chart