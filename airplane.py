"""Airplanes are defined by two classes: Airplane and Seat.

Each spot on the plane has a corresponding seat that can be assigned to the
passengers. Each seats is identified by the row and seat number which is set by
the Airplane seat map while Seats also have a window-middle-aisle property which
allows them to be sorted in order.

The Airplane class generates the seat map and tracks which seats are occupied.

Usage:
    from airplane import Airplane, Seat

    plane = Airplane(number_of_rows=30, seats_per_row=6)
    seat = Seat(row=10, seat=1, window_middle_aisle='middle')
"""

SEAT_TYPES = ['window', 'middle', 'aisle']


class Seat(object):
    def __init__(self, row: int, seat: int, window_middle_aisle: str) -> None:
        """Airplane seats sortable in order.

        Args:
            row (int)
            seat (int)
            window_middle_aisle (str): String identifying the seat_type, e.g.
                'window', 'middle', or 'aisle'.

        Raises:
            ValueError: if the seat_type is illdefined
        """
        self.row = row
        self.seat = seat
        if window_middle_aisle in SEAT_TYPES:
            self.type = window_middle_aisle
        else:
            raise ValueError(f'Invalid seat type. Must be in {SEAT_TYPES}')

    def __lt__(self, other):
        # window < middle < aisle (reverse alphabetical)
        if self.row < other.row:
            return True
        elif self.row == other.row and self.type > other.type:
            return True
        elif self.row == other.row and self.seat < other.seat:
            return True

    def __gt__(self, other):
        # window < middle < aisle (reverse alphabetical)
        if self.row > other.row:
            return True
        elif self.row == other.row and self.type < other.type:
            return True
        elif self.row == other.row and self.seat > other.seat:
            return True


class Airplane(object):
    def __init__(self, number_of_rows: int, seats_per_row: int) -> None:
        """Airplane class that defines the seating arangement

        Args:
            number_of_rows (int)
            seats_per_row (int): Each row is split in half by a central aisle.
        """
        self.number_of_rows = number_of_rows
        self.seats_per_row = seats_per_row

        self.seating_chart = self._generate_seating_chart()

    @property
    def seats(self):
        """Returns a generator for seats on the plane

        Returns:
            tuple: (row, seat) for each seat on the plane
        """
        for row in range(self.number_of_rows):
            for seat in list(range(self.seats_per_row)):
                if seat in self.window_seats:
                    yield Seat(row, seat, 'window')
                elif seat in self.aisle_seats:
                    yield Seat(row, seat, 'aisle')
                else:
                    yield Seat(row, seat, 'middle')

    @property
    def window_seats(self) -> set:
        """
        Returns:
            set: window seat numbers
        """
        return {0, self.seats_per_row - 1}

    @property
    def middle_seats(self) -> set:
        """
        Returns:
            set: all seat numbers that are not window or aisle seats
        """
        seats = set(range(self.seats_per_row))
        # remove window and aisle seats
        seats -= self.window_seats
        seats -= self.aisle_seats
        return seats

    @property
    def aisle_seats(self) -> set:
        """
        Returns:
            set: aisle seat numbers
        """
        return {self._aisle - 1, self._aisle}

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
            side = self.seating_chart[passenger.row][:aisle]
            return sum(side[:passenger.seat:-1])
        else:
            # passenger sits on the right side of the plane
            side = self.seating_chart[passenger.row][aisle:]
            return sum(side[:passenger.seat - aisle + 1])

    def seat_passenger(self, passenger) -> int:
        """Change seating for passenger seat to 1 (occupied).

        Args:
            passenger (Passenger)

        Returns:
            int: number of seat suffles
        """
        required_shuffles = self._required_shuffles(passenger)
        if passenger.seat < self._aisle:
            self.seating_chart[passenger.row][passenger.seat] = 1
        else:
            # start seating passengers from the window
            self.seating_chart[passenger.row][passenger.seat] = 1
        return required_shuffles

    def _generate_seating_chart(self) -> list:
        """Generate a simple seating chart.

        Passengers are seated according to the chart below. Also see
        self.seat_passenger above.

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
