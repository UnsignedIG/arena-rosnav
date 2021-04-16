import argparse
import time
from datetime import datetime
import os
import sys
from stable_baselines3 import A2C
from rl_agent.envs.flatland_gym_env import FlatlandEnv
from task_generator.tasks import get_predefined_task
import rospy
import rospkg
import numpy as np
from collections import OrderedDict
import h5py

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-o', '--outputformat', type=str, help='choose output format: "h5" or "npz"', default='h5')
parser.add_argument('-s', '--scenario', type=str, metavar="[scenario name]", default='/home/michael/catkin_ws/src/arena-rosnav/simulator_setup/scenerios/obstacle_map1_obs20.json', help='path of scenario json file for deployment')
args = parser.parse_args()

rospy.init_node("record_rollouts")

task = get_predefined_task(mode="ScenerioTask", PATHS={"scenerios_json_path": args.scenario})
models_folder_path = rospkg.RosPack().get_path('simulator_setup')
arena_local_planner_drl_folder_path = rospkg.RosPack().get_path(
    'arena_local_planner_drl')

env = FlatlandEnv(task, os.path.join(models_folder_path, 'robot', 'myrobot.model.yaml'),
                  os.path.join(arena_local_planner_drl_folder_path,
                               'configs', 'default_settings.yaml'), "rule_00", False,
                  )

obs = env.reset()
observations = []
actions = []
while(True):
    merged_obs, obs_dict, action = env.observation_collector.get_observations_and_action()

    reward, reward_info = env.reward_calculator.get_reward(
            obs_dict['laser_scan'], obs_dict['goal_in_robot_frame'])
    env.observation_collector.register_reward(reward)

    observations.append(merged_obs)
    actions.append(action)
    #TODO improvement: get info from check_if_done; if the robot collided, don't save (obs, action) to the arrays
    if env.check_if_done(merged_obs, obs_dict):
        try:
            env.reset()
        except:
            print('All scenarios have been evaluated!')
            break

# save rollouts
if args.outputformat == 'h5':
    date_str = datetime.now().strftime('%Y%m%d_%H-%M')
        
    file_action = h5py.File(f'./output/{date_str}_action.hdf5', "w")
    file_state = h5py.File(f'./output/{date_str}_state.hdf5', "w")
    
    file_action.create_dataset("actions", data=np.array(actions))
    file_state.create_dataset("states", data=np.array(observations))

    file_state.close()
    file_action.close()
    rospy.loginfo("h5py writer have been shut down.")

if args.outputformat == 'npz':
    # save observations and actions in an npz file:
    date_str = datetime.now().strftime('%Y%m%d_%H-%M')
    path = str(f'./output/rollout_{date_str}')
    print(f'Saving rollouts to {path}')
    np.savez_compressed(
        path,
        observations = np.array(observations),
        actions = np.array(actions)
    )
    print('Done saving rollouts')