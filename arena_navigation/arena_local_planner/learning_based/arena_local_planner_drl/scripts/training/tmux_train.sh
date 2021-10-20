#!/bin/sh
# send-keys "python3 scripts/training/train_all_in_one_agent.py --agent AGENT_13 --eval_log --tb --n_envs $num_envs --agent_name all_in_one_agents_teb_rlca_rule03_policy13 --all_in_one_config all_in_one_default.json --load" C-m \; \
num_envs=$1

tmux new-session \; \
send-keys "workon rosnav" C-m \; \
send-keys "roslaunch arena_bringup start_training_all_in_one_planner.launch num_envs:=$num_envs" C-m\; \
split-window -h \; \
send-keys 'workon rosnav' C-m \; \
send-keys 'source catkin_ws/devel/setup.zsh' C-m \; \
send-keys 'roscd arena_local_planner_drl/' C-m \; \
send-keys "python3 scripts/training/train_all_in_one_agent.py --agent AGENT_2 --eval_log --tb --n_envs $num_envs --agent_name indoor_teb_drl4_rlca_rule07_policy2_forced0.6-3.5 --all_in_one_config all_in_one_default_with_forced_actions.json" C-m \; \
split-window -h \; \
send-keys 'roslaunch arena_bringup visualization_training.launch use_rviz:=true rviz_file:=allinone_train' \; \
select-layout even-horizontal \; \
split-window -v \; \
select-pane -t 2 \; \