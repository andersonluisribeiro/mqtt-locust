import numpy as np
from geopy import Point
from geopy import distance

class PayloadGenerator:
    MIN_DISPLACEMENT = 0               # 0 Km
    MAX_DISPLACEMENT = 0.01            # 0.01 Km
    MIN_BEARING = 0                    # 0 degree
    MAX_BEARING = 360                  # 360 degrees

    def __init__(self):
        self._current_position = Point(np.random.random()*180 - 90,
                                       np.random.random()*360 - 180)
        self._mean_temperature = np.random.random_integers(-15,15)
        self._mean_humidity = np.random.random_integers(30,70)

    def _next_position(self):
        # displacement
        displacement = np.random.uniform(self.__class__.MIN_DISPLACEMENT, self.__class__.MAX_DISPLACEMENT)

        # direction
        bearing = np.random.uniform(self.__class__.MIN_BEARING, self.__class__.MAX_BEARING)

        # next point
        next_position = distance.vincenty(kilometers=displacement).destination(self._current_position, bearing)

        return next_position, displacement, bearing

    def next(self):
        # move
        (self._current_position, self._displacement, self._bearing) = self._next_position()

        payload = {
            'temperature': np.random.normal(self._mean_temperature),
            'humidity': np.random.normal(self._mean_humidity),
            'lightness': np.random.binomial(1, 0.0001, 1)[0],
            'gps': "{0}, {1}".format(str(self._current_position.latitude),
                                     str(self._current_position.longitude))
        }
        return payload