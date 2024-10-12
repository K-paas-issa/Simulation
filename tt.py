import gym
import numpy as np
import pandas as pd
from balloon_learning_environment.env import balloon_env
from balloon_learning_environment.env import generative_wind_field
from balloon_learning_environment.utils import run_helpers
import jax
import datetime as dt
from balloon_learning_environment.env import grid_based_wind_field

# @title Generate a wind field
def main(simulation_input_data):
    wind_field = generative_wind_field.GenerativeWindField
    rng = jax.random.PRNGKey(10)
    df1 = pd.read_csv(simulation_input_data)

    data = [list(df1.columns)]
    df = pd.DataFrame(data, columns=["1", "2", "3", "4", "5"])
    df1.columns=["1","2","3","4","5"]
    df1=pd.concat([df,df1])

    wind_field.field = np.zeros((780,602,1,1,2))
    wind_field.field[:,:,0,0,0] = np.reshape( np.array(df1['4']),newshape=(780,602))
    wind_field.field[:,:,0,0,1] = np.reshape( np.array(df1['5']),newshape=(780,602))

    agents = []
    envs = []
    for agent in ['perciatelli44']:
        envs.append(gym.make('BalloonLearningEnvironment-v0',
                       wind_field_factory=wind_field))
        agents.append(run_helpers.create_agent(agent,envs[-1].action_space.n,
          observation_shape=envs[-1].observation_space.shape))

#@title Run simulation
    seed = random.randint(1, 120000)
    num_steps = 1200  # @param {type: 'number'}
    frame_skip = 5 # @param {type: 'number'}

    times = []
    flight_paths = {}
    data=[]
    for i, agent in enumerate(agents):
        agent_name = agent.get_name()
        print(f'Running simulation for {agent_name}')
        total_reward = 0.0
        steps_within_radius = 0
        flight_paths[agent_name] = list()

        envs[i].seed(seed)
        observation = envs[i].reset()
        envs[i].seed(seed)
        observation = envs[i].reset()
        action = agent.begin_episode(observation)
        observation = envs[i].reset()
        action = agent.begin_episode(observation)

        step_count = 0
        while step_count < num_steps:
            observation, reward, is_done, info = envs[i].step(action)
            action = agent.step(reward, observation)

            total_reward += reward
            sim_state = envs[i].get_simulator_state()
            balloon_state = sim_state.balloon_state
            if step_count % frame_skip == 0:
                altitude = sim_state.atmosphere.at_pressure(balloon_state.pressure).height
                data.append([balloon_state.x.km+ 631.8,balloon_state.y.km+416.8,altitude.km])
                if step_count==1:
                    balloon_state.x.km=balloon_state.x.km-10
                    balloon_state.y.km=balloon_state.y.km-130
                if i == 0:
                    times.append(balloon_state.date_time)

            step_count += 1

            if is_done:
                break
        agent.end_episode(reward, is_done)


        df=pd.DataFrame(data)
        re='./simulation_output.npy'
        np.save(re, np.array(df))
        return re
