"""This is a simplified simulation method that performs the boarding sequence
according to a PassengerQueue.

The simulation performs a single step in which each passenger on the plane moves
one row. If passengers reach their target row, all of them get seated at the
same time which is recorded as a stop.

Usage:
    from airplane import Airplane
    from passenger import Passenger
    from simulation import Simulation
    from queues import FrontToBack

    ROWS = 30
    SEATS_PER_ROW = 6

    airplane = Airplane(number_of_rows=ROWS, seats_per_row=SEATS_PER_ROW)
    sim = Simulation(airplane, FrontToBack, max_iter=1000)
    sim.run()

Note: In order to change kwargs passed to the PassengerQueue, I use partial, e.g.:

    from functools import partial

    NewFrontToBack = partial(FrontToBack, groups=10)
"""

from airplane import Airplane
from passenger import Passenger
from queues import PassengerQueue


class Simulation(object):
    def __init__(self,
                 airplane: Airplane,
                 queue_type: PassengerQueue,
                 max_iter: int = 1000) -> None:
        """Simulation object that oversees the boarding process.

        Args:
            airplane (Airplane)
            queue_type (PassengerQueue)
            max_iter (int, optional): Maximume number of steps. Defaults to 1000.
        """
        self.plane = airplane
        self.passengers_on_the_plane = []
        self.queue = queue_type(airplane)

        self.max_iter = max_iter

        self.seat_shuffles = 0
        self.passengers_seated_each_step = []
        self.steps = 0

    def next_passenger(self) -> Passenger:
        return next(self.queue)

    def step(self) -> None:
        """Performs a simulation step.

        Each step has two parts:
            1) All passengers move one row and sit if they have reached their
               target row. If any passenger sits down, a stop is recorded and
               all steps passengers that reached their target row sit down
               during the same stop.
            2) One new passenger enters the plane.
        """
        self.passengers_seated_each_step.append(0)
        # all passengers move, if they arrive at their seat, they sit down
        for passenger in self.passengers_on_the_plane:
            passenger.move()

            if passenger.arrived_at_row:
                self.seat_shuffles += min(
                    [1, self.plane.seat_passenger(passenger)])
                self.passengers_seated_each_step[-1] += 1

        # board a new passenger until all are on the plane
        try:
            passenger = self.next_passenger()
            passenger.board()
            self.passengers_on_the_plane.append(passenger)
        except StopIteration:
            pass

        self.steps += 1

    def run(self) -> dict:
        """Run the simulation until the plane is full or max_iter is reached.

        Returns:
            dict: {
                    'number of steps': number of simulation steps,
                    'number of stops': number of stops when passengers sit down,
                    'number of seat shuffles': seat shuffles that require
                        passengers to get up,
                    'number of passengers seated': number of passengers that got
                        seated (also the number of seats)
                   }
        """
        while not self.plane.fully_boarded and self.steps < self.max_iter:
            self.step()

        number_of_stops = sum([
            1 if seated > 0 else 0
            for seated in self.passengers_seated_each_step
        ])
        return {
            'number of steps': self.steps,
            'number of stops': number_of_stops,
            'number of seat shuffles': self.seat_shuffles,
            'number of passengers seated': sum(self.passengers_seated_each_step)
        }
