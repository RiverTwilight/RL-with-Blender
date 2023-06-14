import numpy as np
import gymnasium as gym
from gymnasium import spaces
from missile import Missile
import bpy
import random

obstacle_names=[
    "Obstacle",
    "Obstacle.001",
    "Obstacle.002",
]

class MissileGym(gym.Env):
    def __init__(self):
        super(MissileGym, self).__init__()

        self.missile_object = bpy.data.objects['UAV0']
        self.target_object = bpy.data.objects['Target0']

        self.init_position = list(self.missile_object.location)
        self.init_target_position = list(self.target_object.location)
        
        self.missile = Missile(self.init_position, [1, 0, 0], 1, 0.1, 1)
        self.target = np.array(self.init_target_position)
        
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(3,))
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(9,))
        
        # Store obstacle information
        self.obstacles = []
        for name in obstacle_names:
            obstacle = bpy.data.objects[name]
            # Get the position and size of each obstacle
            position = list(obstacle.location)
            size = list(obstacle.dimensions)
            self.obstacles.append((position, size))
        
        print(self.obstacles)
        
        self.safe_distance = 0.5.  # Default safe distance from obstacles

        self.frame = 0  # Initialize frame counter

    def step(self, action, animate=False):
        control_force = action
        self.missile.update(control_force, [0, 0, 0], 0.1)
        
        self.missile_object.location = self.missile.position

        if animate:
            self.missile_object.keyframe_insert(data_path="location", frame=self.frame)
            self.frame += 1  # Increment frame counter

        distance = np.linalg.norm(self.missile.position - self.target)

        # Modify reward based on distance from target and obstacles
        reward = -distance
        for pos, size in self.obstacles:
            obstacle_distance = np.linalg.norm(np.array(pos) - np.array(self.missile.position))
            if obstacle_distance - np.linalg.norm(np.array(size)) / 2 < self.safe_distance:
                reward -= 100  # Penalize if the missile is too close to any obstacle
        if distance < 1:  # If close enough to the target
            reward += 100  # Extra reward for reaching target

        # Compute done
        done = distance > 200 or distance < 1  # If close enough to the target

        # Pack observation for the next step
        obs = np.concatenate((self.missile.position, self.missile.velocity, self.target))


        return obs, reward, done, {}

    def reset(self):
        self.missile = Missile(self.init_position, [1, 0, 0], 1, 0.1, 1)
        self.target = np.array(self.init_target_position)
        self.missile_object.location = self.init_position
        obs = np.concatenate((self.missile.position, self.missile.velocity, self.target))

        self.frame = 0
        self.missile_object.keyframe_insert(data_path="location", frame=self.frame)

        return obs
