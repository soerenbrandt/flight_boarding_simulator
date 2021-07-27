"""Queues define how passengers will enter the plane. There are two superclasses:
PassengerQueue and GroupedBoarding. Most queues are divided into boarding groups
but not all have to be (e.g. Random boarding).

Usage:
    Boarding groups are generated from the seating chart of the airplane.

    from airplane import Airplane
    from queues import *

    plane = Airplane(number_of_rows=30, seats_per_row=6)

    <PassengerQueue>(plane, **kwargs)

The passenger queues currently implemented are:
- FrontToBack
- BackToFront
- Random
- WindowMiddleAisle
- Steffen

The kwargs for some of these groups include:
- number_of_boarding_groups (for GroupedBoarding: FrontToBack, BackToFront)
- shuffle_groups (for GroupedBoarding: FrontToBack, BackToFront, WindowMiddleAisle)
- perfect (for Steffen only, opposite of shuffle_groups)
"""

from abc import ABC, abstractmethod
from itertools import chain, cycle
import math
import random

from passenger import Passenger
from airplane import Airplane


class PassengerQueue(ABC):
    def __init__(self, plane: Airplane) -> None:
        """Defines the PassengerQueue.

        Args:
            plane (Airplane): Airplane that generates Seats for passengers
        """
        self.passengers = [Passenger(seat) for seat in plane.seats]

    def __iter__(self):
        return self

    def __next__(self) -> Passenger:
        if len(self.passengers) > 0:
            return self.select_passenger()
        else:
            raise StopIteration

    @abstractmethod
    def select_passenger(self):
        """Generates the order in which passengers board the plane. Must define
        a method that also remove the passenger from the list when boarding.
        """
        pass


class GroupedBoarding(ABC):
    def __init__(self,
                 passengers: Passenger,
                 number_of_boarding_groups: int = 4,
                 shuffle_groups: bool = True) -> None:
        """Adds boarding groups to a passenger queue.

        Args:
            passengers (Passenger)
            number_of_boarding_groups (int, optional): Defaults to 4.
            shuffle_groups (bool, optional): If True, passengers within a group
                board in random order. Defaults to True.
        """
        self.passengers = passengers
        self.number_of_boarding_groups = number_of_boarding_groups
        self.shuffle_groups = shuffle_groups

        if number_of_boarding_groups is not None:
            self.group_passengers()

    def group_passengers(self):
        number_per_group = math.ceil(
            len(self.passengers) / self.number_of_boarding_groups)
        groups = [
            self.passengers[i * number_per_group:(i + 1) * number_per_group]
            for i in range(self.number_of_boarding_groups)
        ]
        if self.shuffle_groups:
            for group in groups:
                random.shuffle(group)
        self.passengers = list(chain(*groups))


class FrontToBack(PassengerQueue, GroupedBoarding):
    def __init__(self,
                 plane: Airplane,
                 groups: int = None,
                 shuffle_groups: bool = True) -> None:
        """Rows board in increasing order but passengers within each row board
        in random order.

        Args:
            plane (Airplane)
            groups (int, optional): The number of groups. By default, uses group
                per row in the plane. Defaults to None.
            shuffle_groups (bool, optional): If True, passengers within a group
                board in random order. Defaults to True.
        """
        PassengerQueue.__init__(self, plane)

        # sort passengers (to be sure)
        self.passengers.sort()

        if groups is None:
            groups = plane.number_of_rows
        GroupedBoarding.__init__(self,
                                 self.passengers,
                                 number_of_boarding_groups=groups,
                                 shuffle_groups=shuffle_groups)

    def select_passenger(self):
        return self.passengers.pop(0)


class BackToFront(PassengerQueue, GroupedBoarding):
    def __init__(self,
                 plane: Airplane,
                 groups: int = None,
                 shuffle_groups: bool = True) -> None:
        """Rows board in increasing order but passengers within each row board
        in random order.

        Args:
            plane (Airplane)
            groups (int, optional): The number of groups. By default, uses group
                per row in the plane. Defaults to None.
            shuffle_groups (bool, optional): If True, passengers within a group
                board in random order. Defaults to True.
        """
        PassengerQueue.__init__(self, plane)

        # invert order of passengers
        self.passengers.sort(reverse=True)

        if groups is None:
            groups = plane.number_of_rows
        GroupedBoarding.__init__(self,
                                 self.passengers,
                                 number_of_boarding_groups=groups,
                                 shuffle_groups=shuffle_groups)

    def select_passenger(self):
        return self.passengers.pop(0)


class Random(PassengerQueue):
    def __init__(self, plane: Airplane) -> None:
        """Passengers board in entirely random order

        Args:
            plane (Airplane)
        """
        super().__init__(plane)
        random.shuffle(self.passengers)

    def select_passenger(self):
        return self.passengers.pop(0)


class WindowMiddleAisle(PassengerQueue, GroupedBoarding):
    def __init__(self, plane: Airplane, shuffle_groups: bool = True) -> None:
        """Passengers are divided into 6 groups: both side for each for window,
        middle, and aisle.

        Args:
            plane (Airplane)
            shuffle_groups (bool, optional): If True, passengers within a group
                board in random order. Defaults to True.
        """
        # sort passengers by window, middle, aisle
        PassengerQueue.__init__(self, plane)

        self.passengers.sort()

        self._window_seats = plane.window_seats
        self._middle_seats = plane.middle_seats
        self._aisle_seats = plane.aisle_seats

        GroupedBoarding.__init__(self,
                                 self.passengers,
                                 number_of_boarding_groups=6,
                                 shuffle_groups=shuffle_groups)

    def select_passenger(self):
        return self.passengers.pop(0)

    def group_passengers(self):
        groups = []
        # assign window seats
        for seat in chain(self._window_seats, self._middle_seats,
                          self._aisle_seats):
            group = []
            for passenger in self.passengers:
                if passenger.seat == seat:
                    group.append(passenger)
            groups.append(group)

        if self.shuffle_groups:
            for group in groups:
                random.shuffle(group)

        self.passengers = list(chain(*groups))


class Steffen(PassengerQueue, GroupedBoarding):
    def __init__(self, plane: Airplane, perfect: bool = False) -> None:
        """Steffen is a highly efficient boarding approach combining different
        boarding approaches.

        There are two types of Steffen boarding: modified and perfect. In perfect
        Steffen boarding, passengers are perfectly ordered both back-to-front
        and window-middle-aisle.
        In modified Steffen, passengers are sorted into 4 boarding groups:
        Alternating rows on alternating sides. Within each group, passengers
        are again randomized.

        Args:
            plane (Airplane)
            perfect (bool, optional): If True, perfect Steffen is used, else
                modified Steffen. Defaults to False.
        """
        # sort passengers by window, middle, aisle
        PassengerQueue.__init__(self, plane)

        self.perfect = perfect

        self._window_seats = plane.window_seats
        self._middle_seats = plane.middle_seats
        self._aisle_seats = plane.aisle_seats

        GroupedBoarding.__init__(self,
                                 self.passengers,
                                 number_of_boarding_groups=4,
                                 shuffle_groups=not perfect)

    def select_passenger(self):
        return self.passengers.pop(0)

    def group_passengers(self):
        if self.perfect:
            groups = []
            # assign window seats
            #for odd_even in [1, 0]:
            for seat in chain(self._window_seats, self._middle_seats,
                              self._aisle_seats):
                group = []
                for passenger in self.passengers:
                    if passenger.seat == seat:
                        group.append(passenger)
                groups.append(group)
            for group in groups:
                group.sort(reverse=True)

        else:
            seats = sorted(
                set.union(self._window_seats, self._middle_seats,
                          self._aisle_seats))
            groups = []
            side = cycle([seats[:len(seats) // 2], seats[len(seats) // 2:]])
            for odd_even in [1, 1, 0, 0]:
                seats_on_side = next(side)
                group = []
                for passenger in self.passengers:
                    if passenger.seat in seats_on_side and passenger.row % 2 == odd_even:
                        group.append(passenger)
                groups.append(group)

            if self.shuffle_groups:
                for group in groups:
                    random.shuffle(group)

        self.number_of_boarding_groups = len(groups)
        self.passengers = list(chain(*groups))
