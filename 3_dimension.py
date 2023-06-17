import numpy as np
import gym
from gym import spaces
from controller.missile import Missile
import bpy
import random
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.utils import set_random_seed

obstacle_names=[

]

animate = False

class MissileGym(gym.Env):
    def __init__(self):
        super(MissileGym, self).__init__()

        self.missile_object = bpy.data.objects['UAV0']
        self.target_object = bpy.data.objects['Target0']

        self.init_position = list(self.missile_object.location)
        self.init_target_position = list(self.target_object.location)

        self.missile = Missile(self.init_position, [1, 0, 0], 1, 0.1, 1)
        self.target = np.array(self.init_target_position)
        
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(3,), dtype=np.int32)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(9,))

        # Store obstacle information
        self.obstacles = []
        for name in obstacle_names:
            obstacle = bpy.data.objects[name]
            # Get the position and size of each obstacle
            position = list(obstacle.location)
            size = list(obstacle.dimensions)
            self.obstacles.append((position, size))
        
        self.safe_distance = 0.5  # Default safe distance from obstacles

        self.frame = 0  # Initialize frame counter

    def step(self, action):
        control_force = action

        self.missile.update(control_force, [0, 0, 0], 0.1)
        
        self.missile_object.location = self.missile.position

        new_distance = np.linalg.norm(self.missile.position - self.target)
        reward = -new_distance

        for pos, size in self.obstacles:
            obstacle_distance = np.linalg.norm(np.array(pos) - np.array(self.missile.position))
            if obstacle_distance - np.linalg.norm(np.array(size)) / 2 < self.safe_distance:
                reward -= 20  # Penalize if the missile is too close to any obstacle
        if new_distance < 1:  # If close enough to the target
            reward += 120  # Extra reward for reaching target

        done = new_distance < 1  # If close enough to the target

        obs = np.concatenate((self.missile.position, self.missile.velocity, self.target))

        if animate:
            print(reward)
            self.missile_object.keyframe_insert(data_path="location", frame=self.frame)
            self.frame += 1  # Increment frame counter

        return obs, reward, done, {}

    def reset(self):
        self.missile = Missile(self.init_position, [1, 0, 0], 1, 0.1, 1)
        self.target = np.array(self.init_target_position)
        self.missile_object.location = self.init_position
        obs = np.concatenate((self.missile.position, self.missile.velocity, self.target))

        self.frame = 0

        return obs

env = DummyVecEnv([lambda: MissileGym()])  # Wrap the environment

set_random_seed(0)

model = PPO('MlpPolicy', env, verbose=1)

model.learn(total_timesteps=2000000)

model.save("missile_ppo")

model = PPO.load("missile_ppo")
obs = env.reset()
animate = True
for i in range(1000):
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    if dones:
        obs = env.reset()

# num_episodes = 100

# for i_episode in range(num_episodes):
#     observation = env.reset()
#     total_reward = 0
#     for t in range(300):
#         # Compute the direction to the target
#         missile_position = observation[:3]
#         target_position = observation[6:]
#         direction = target_position - missile_position
#         direction /= np.linalg.norm(direction)

#         action = direction
#         observation, reward, done, info = env.step(action)

#         total_reward += reward
#         if done:
#             print("Episode finished after {} timesteps with reward {}".format(t+1, total_reward))
#             break

