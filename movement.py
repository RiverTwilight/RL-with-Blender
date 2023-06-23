import bpy
from controller.uav import MultiUAVController, MultiDroneGym
from common.blender_kits import render_image_sequence
from stable_baselines3.common.vec_env import DummyVecEnv

# Hyper Paramters
total_timesteps = 4000000
random_seed = 0
num_episodes = 1
uav_name = 'UAV'
num_uavs = 10
uav_size = 1
platform_width = 100
platform_height = 100

def spawn_uav(uav_name, location):
    original_uav = bpy.data.objects[uav_name]
    new_uav = original_uav.copy()
    new_uav.data = original_uav.data.copy()
    new_uav.animation_data_clear()
    bpy.context.collection.objects.link(new_uav)
    
    new_uav.location = location
    return new_uav

controller = MultiUAVController(num_uavs, uav_size, platform_width, platform_height)

initial_positions = controller.get_random_initial_positions()
target_positions = controller.get_target_positions()

for i in range(num_uavs):
    uav = spawn_uav(uav_name, initial_positions[i])
    uav.keyframe_insert(data_path="location", frame=0)

    uav.location = target_positions[i]
    uav.keyframe_insert(data_path="location", frame=100)

    # render_image_sequence(f'Camera{}', '/tmp/image_sequence', 0, 100)


# env = DummyVecEnv([lambda: MultiDroneGym(create_animation=False)])
