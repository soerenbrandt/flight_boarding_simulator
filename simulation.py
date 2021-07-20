""""""

from queues import PassengerQueue


class Simulation(object):
    def __init__(self, airplane, queue_type: PassengerQueue, max_iter=1000):
        self.plane = airplane
        self.passengers_on_the_plane = []
        self.queue = queue_type(airplane)

        self.max_iter = max_iter

        self.seat_shuffles = 0
        self.passengers_seated_each_step = []
        self.steps = 0

    def next_passenger(self):
        return next(self.queue)

    def step(self):
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

    def run(self):
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
