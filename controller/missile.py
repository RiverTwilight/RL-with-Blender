import numpy as np

class Missile:
    def __init__(self, position, velocity, mass, drag_coefficient, characteristic_area):
        # print("Missile Controller Initialized")
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.mass = mass
        self.drag_coefficient = drag_coefficient
        self.characteristic_area = characteristic_area

    def update(self, control_force, disturbance, dt):
        self.position += self.velocity * dt
        self.velocity += (control_force / self.mass - disturbance) * dt
