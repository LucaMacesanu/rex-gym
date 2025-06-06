r"""Running a pre-trained ppo agent on rex environments"""
import logging
import os
import site
import time

import tensorflow.compat.v1 as tf
from rex_gym.agents.scripts import utility
from rex_gym.agents.ppo import simple_ppo_agent
from rex_gym.util import flag_mapper


class PolicyPlayer:
    def __init__(self, env, args, signal_type, policy_dir=None):
        self.env = env
        self.args = args
        self.signal_type = signal_type
        self.env_id = env
        self.gym_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        if policy_dir is None:
            # Fallback to default behavior
            self.policy_dir = os.path.join(os.path.dirname(__file__), '..', 'policies', env, signal_type)
        else:
            self.policy_dir = policy_dir


    def play(self):
        if self.signal_type:
            self.args['signal_type'] = self.signal_type
        else:
            self.signal_type = flag_mapper.DEFAULT_SIGNAL[self.env_id]
        policy_id = f"{self.env_id}_{self.signal_type}"
        policy_path = flag_mapper.ENV_ID_TO_POLICY[policy_id][0]
        policy_dir = os.path.join(self.gym_dir_path, policy_path)
        config = utility.load_config(self.policy_dir)
        # config = utility.load_config(policy_dir)
        policy_layers = config.policy_layers
        value_layers = config.value_layers
        # env = config.env(render=True, **self.args)
        # Pull tag from config.env.state[0]
        env_tag = config.env.state[0].tag
        env_class = utility.load_class_from_tag(env_tag)
        env = env_class(render=True, **self.args)
        network = config.network
        # checkpoint = os.path.join(policy_dir, flag_mapper.ENV_ID_TO_POLICY[policy_id][1])
        checkpoint = os.path.join(self.policy_dir, "model.ckpt-2000000")
        with tf.Session() as sess:
            agent = simple_ppo_agent.SimplePPOPolicy(sess,
                                                     env,
                                                     network,
                                                     policy_layers=policy_layers,
                                                     value_layers=value_layers,
                                                     checkpoint=checkpoint)
            sum_reward = 0
            observation = env.reset()
            while True:
                action = agent.get_action([observation])
                observation, reward, done, _ = env.step(action[0])
                time.sleep(0.002)
                sum_reward += reward
                logging.info(f"Reward={sum_reward}")
                if done:
                    break
