import numpy as np
import os
import bpy
from stable_baselines3 import DQN, PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.utils import set_random_seed
from stable_baselines3.common.callbacks import BaseCallback
from blender_env import MissileGym

# Hyper Paramters
total_timesteps = 1500000
random_seed = 0

class TensorboardCallback(BaseCallback):
    def __init__(self, verbose=0):
        self.verbose = verbose
        super(TensorboardCallback, self).__init__(verbose)

    def _on_step(self) -> bool:
        # Log scalar value (here a random variable)
        x, y = self.model.env.get_attr('missile')[0].position[:2]
        self.logger.record('reward/x', x)
        self.logger.record('reward/y', y)

        return True

def test_model(model_path, num_episodes=10, max_steps_per_episode=3000):
    model = PPO.load(model_path)

    env = DummyVecEnv([lambda: MissileGym(create_animation=False)])  # Wrap the environment
    obs = env.reset()
    
    total_rewards = []

    for episode in range(num_episodes):
        obs = env.reset()
        if episode == num_episodes - 1:
            env.set_attr("create_animation", True)
        for step in range(max_steps_per_episode):
            action, _states = model.predict(obs)
            obs, rewards, dones, info = env.step(action)
            if dones:
                print(f"Episode {episode + 1} finished after {step + 1} steps with reward {rewards}")
                total_rewards.append(rewards)
                break

    print(f"Average reward: {np.mean(total_rewards)}")

    return total_rewards

if __name__ == "__main__":

    env = DummyVecEnv([lambda: MissileGym()])

    set_random_seed(random_seed)

    dir_path = os.path.dirname(bpy.data.filepath)
    tensorboard_log=os.path.join(dir_path, "tensorboard_logs/")

    model = PPO('MlpPolicy', env, verbose=1, device="cuda", tensorboard_log=tensorboard_log)

    model.learn(total_timesteps=total_timesteps)

    model.save("missile_ppo_randomized")

    test_model("missile_ppo_randomized")
