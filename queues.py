""""""

from abc import ABC, abstractmethod
from itertools import chain, cycle
import math
import random

from passenger import Passenger
from airplane import Airplane


class PassengerQueue(ABC):
    def __init__(self, plane: Airplane):
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
        pass


class GroupedBoarding(ABC):
    def __init__(self,
                 passengers,
                 number_of_boarding_groups=4,
                 shuffle_groups=True):
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
    def __init__(self, plane: Airplane, groups=30):
        PassengerQueue.__init__(self, plane)

        # sort passengers (to be sure)
        self.passengers.sort()

        GroupedBoarding.__init__(self,
                                 self.passengers,
                                 number_of_boarding_groups=groups,
                                 shuffle_groups=True)

    def select_passenger(self):
        return self.passengers.pop(0)


class BackToFront(PassengerQueue, GroupedBoarding):
    def __init__(self, plane: Airplane, groups=30):
        PassengerQueue.__init__(self, plane)

        # invert order of passengers
        self.passengers.sort(reverse=True)

        GroupedBoarding.__init__(self,
                                 self.passengers,
                                 number_of_boarding_groups=groups,
                                 shuffle_groups=True)

    def select_passenger(self):
        return self.passengers.pop(0)


class Random(PassengerQueue):
    def __init__(self, plane: Airplane):
        super().__init__(plane)
        random.shuffle(self.passengers)

    def select_passenger(self):
        return self.passengers.pop(0)


class WindowMiddleAisle(PassengerQueue, GroupedBoarding):
    def __init__(self, plane: Airplane, shuffle_groups=True):
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
    def __init__(self, plane: Airplane, perfect=False):
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
