import numpy as np
import random
import gym
from gym import spaces
from controller.missile import Missile
import bpy
import time
from mathutils import Vector

class MultiUAVController:
    def __init__(self, num_uavs, uav_size, platform_width, platform_height):
        self.num_uavs = num_uavs
        self.uav_size = uav_size
        self.platform_width = platform_width
        self.platform_height = platform_height

        self.total_uav_perimeter = self.num_uavs * self.uav_size
        self.total_platform_perimeter = (self.platform_width + self.platform_height) * 2
        self.spacing = (self.total_platform_perimeter - self.total_uav_perimeter) / (self.num_uavs - 1)

    def get_random_initial_positions(self):
        positions = []
        for _ in range(self.num_uavs):
            x = random.uniform(-self.platform_width/2, self.platform_width/2)
            y = random.uniform(-self.platform_height/2, self.platform_height/2)
            z = 0  # initial z-position
            positions.append((x, y, z))
        return positions

    def get_target_positions(self):
        positions = []
        for i in range(self.num_uavs):
            distance_along_perimeter = i * self.spacing

            # Determine position on perimeter
            if distance_along_perimeter < self.platform_width:  # Top side
                x = -self.platform_width / 2 + distance_along_perimeter
                y = self.platform_height / 2
            elif distance_along_perimeter < self.platform_width + self.platform_height:  # Right side
                x = self.platform_width / 2
                y = self.platform_height / 2 - (distance_along_perimeter - self.platform_width)
            elif distance_along_perimeter < 2 * self.platform_width + self.platform_height:  # Bottom side
                x = self.platform_width / 2 - (distance_along_perimeter - self.platform_width - self.platform_height)
                y = -self.platform_height / 2
            else:  # Left side
                x = -self.platform_width / 2
                y = -self.platform_height / 2 + (distance_along_perimeter - 2 * self.platform_width - self.platform_height)

            # Adjust for UAV size
            x += np.sign(x) * self.uav_size / 2
            y += np.sign(y) * self.uav_size / 2
            z = 100

            positions.append((x, y, z))
        return positions

obstacle_names=[
    # "Obstacle"
]

class MultiDroneGym(gym.Env):
    def __init__(self, create_animation=False):
        super(MultiDroneGym, self).__init__()

        self.missile_object = bpy.data.objects['UAV0']
        self.target_object = bpy.data.objects['Target0']
        self.base_object = bpy.data.objects['Base']

        self.missile_object.animation_data_clear()

        self.randomize_target()
        self.reset_missile()
        
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(2,), dtype=np.int32)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(4,))

        self.action_mapping = [
            np.array([-1, 0, 0]),  # Left
            np.array([1, 0, 0]),   # Right
            np.array([0, 1, 0]),   # Forward
            np.array([0, -1, 0]),  # Backward
        ]

        self.obstacles = []
        for name in obstacle_names:
            obstacle = bpy.data.objects[name]
            # Get the position and size of each obstacle
            position = list(obstacle.location)
            size = list(obstacle.dimensions)
            self.obstacles.append((position, size))
        
        self.safe_distance = 4  # Default safe distance from obstacles

        self.frame = 0
        self.create_animation = create_animation
    
    def randomize_target(self):
        np.random.seed(int(time.time()))
        self.target = np.concatenate((np.random.uniform(low=-100, high=100, size=2), [0]))
        self.target_object.location = self.target
        print("Shuffle Target", self.target)

    def update_orientation(self):
        direction = Vector(self.missile.velocity)
        rot_quat = direction.to_track_quat('Y', 'Z')
        self.missile_object.rotation_euler = rot_quat.to_euler()

        if self.create_animation:
            self.missile_object.keyframe_insert(data_path="rotation_euler", frame=self.frame)

    def reset_missile(self):
        self.missile = Missile(list(self.base_object.location), [1, 0, 0], 1, 0.1, 1)
        self.missile_object.location = self.missile.position
        
    def step(self, action):
        control_force = np.concatenate((action, [0]))

        self.missile.update(control_force, [0, 0, 0], 0.1)

        self.update_orientation()

        self.missile_object.location = self.missile.position

        new_distance = np.linalg.norm(self.missile.position - self.target)
        reward = -new_distance
        reward -= 1 

        if new_distance > 150:
            reward -= new_distance * 0.5

        for pos, size in self.obstacles:
            obstacle_distance = np.linalg.norm(np.array(pos) - np.array(self.missile.position))
            if obstacle_distance - np.linalg.norm(np.array(size)) / 2 < self.safe_distance:
                reward -= 20  # Penalize if the missile is too close to any obstacle

        if new_distance < 4:  # If close enough to the target
            reward += 200  # Extra reward for reaching target

        done = new_distance > 300 or new_distance < 3  # If close enough to the target

        obs = np.concatenate((self.missile.position[:2], self.target[:2]))

        if self.create_animation:
            print(reward)
            self.missile_object.keyframe_insert(data_path="location", frame=self.frame)
            self.frame += 1  # Increment frame counter

        return obs, reward, done, {}

    def reset(self):
        self.randomize_target()
        self.reset_missile()

        obs = np.concatenate((self.missile.position[:2], self.target[:2]))

        self.frame = 0
        if self.create_animation:
            self.missile_object.keyframe_insert(data_path="location", frame=self.frame)

        return obs

