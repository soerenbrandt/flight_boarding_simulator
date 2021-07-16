""""""

from abc import ABC, abstractmethod
from itertools import chain, cycle
import math
import random


class PassengerQueue(ABC):
    def __init__(self, passengers):
        self.passengers = passengers

    def __iter__(self):
        return self

    def __next__(self):
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
    def __init__(self, passengers, groups=30):
        PassengerQueue.__init__(self, passengers)
        GroupedBoarding.__init__(self,
                                 passengers,
                                 number_of_boarding_groups=groups,
                                 shuffle_groups=True)

    def select_passenger(self):
        return self.passengers.pop(0)


class BackToFront(PassengerQueue, GroupedBoarding):
    def __init__(self, passengers, groups=30):
        # invert order of passengers in each row
        row_size = len(set([p.row for p in passengers]))
        reordered_passenger_rows = [
            passengers[i * row_size:(i + 1) * row_size][::-1]
            for i in range(len(passengers) // row_size + 1)
        ]

        passengers = list(chain(*reordered_passenger_rows))
        PassengerQueue.__init__(self, passengers)
        GroupedBoarding.__init__(self,
                                 passengers,
                                 number_of_boarding_groups=groups,
                                 shuffle_groups=True)

    def select_passenger(self):
        return self.passengers.pop(-1)


class Random(PassengerQueue):
    def __init__(self, passengers):
        random.shuffle(passengers)
        super().__init__(passengers)

    def select_passenger(self):
        return self.passengers.pop(0)


class WindowMiddleAisle(PassengerQueue, GroupedBoarding):
    def __init__(self, passengers, shuffle_groups=True):
        # sort passengers by window, middle, aisle
        PassengerQueue.__init__(self, passengers)
        GroupedBoarding.__init__(self,
                                 passengers,
                                 number_of_boarding_groups=6,
                                 shuffle_groups=shuffle_groups)

    def select_passenger(self):
        return self.passengers.pop(0)

    def group_passengers(self):
        seats = sorted(set([passenger.seat for passenger in self.passengers]))
        groups = []
        side = cycle([0, -1])
        while len(seats) > 0:
            seat = seats.pop(next(side))
            passengers_in_group = []
            for passenger in self.passengers:
                if passenger.seat == seat:
                    passengers_in_group.append(passenger)
            groups.append(passengers_in_group)

        if self.shuffle_groups:
            for group in groups:
                random.shuffle(group)

        self.passengers = list(chain(*groups))


class Steffen(PassengerQueue, GroupedBoarding):
    def __init__(self, passengers, shuffle_groups=True):
        # sort passengers by window, middle, aisle
        PassengerQueue.__init__(self, passengers)
        GroupedBoarding.__init__(self,
                                 passengers,
                                 number_of_boarding_groups=4,
                                 shuffle_groups=shuffle_groups)

    def select_passenger(self):
        return self.passengers.pop(0)

    def group_passengers(self):
        seats = sorted(set([passenger.seat for passenger in self.passengers]))
        groups = []
        side = cycle([seats[:len(seats) // 2], seats[len(seats) // 2:]])
        for group in [1, 1, 0, 0]:
            seats_on_side = next(side)
            passengers_in_group = []
            for passenger in self.passengers:
                if passenger.seat in seats_on_side and passenger.row % 2 == group:
                    passengers_in_group.append(passenger)
            groups.append(passengers_in_group)

        if self.shuffle_groups:
            for group in groups:
                random.shuffle(group)

        self.passengers = list(chain(*groups))
