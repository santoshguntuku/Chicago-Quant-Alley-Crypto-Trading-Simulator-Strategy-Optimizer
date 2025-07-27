import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

def run_experiment(algorithm, env, T, is_contextual=False):
    cumulative_rewards = np.zeros(T)
    best_arm_counts = np.zeros(T)
    best_arm = env.best_arm if hasattr(env, 'best_arm') else None
    contexts_cache = []

    for t in tqdm(range(T), desc="Running experiment"):
        if is_contextual:
            contexts = env.get_contexts()
            arm = algorithm.select_arm(contexts)
            reward = env.get_reward(arm, contexts)
            algorithm.update(arm, reward, contexts[arm])
            contexts_cache.append(contexts)
        else:
            arm = algorithm.select_arm()
            reward = env.get_reward(arm)
            algorithm.update(arm, reward)
            contexts_cache.append(None)

        cumulative_rewards[t] = reward if t == 0 else cumulative_rewards[t-1] + reward
        if arm == best_arm:
            best_arm_counts[t] = 1 if t == 0 else best_arm_counts[t-1] + 1
        else:
            best_arm_counts[t] = best_arm_counts[t-1] if t > 0 else 0

    return cumulative_rewards, best_arm_counts, contexts_cache

def plot_results(algorithms, algorithm_names, env_name, cumulative_regrets, best_arm_freqs):
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 1, 1)
    for i, regrets in enumerate(cumulative_regrets):
        plt.plot(regrets, label=algorithm_names[i])
    plt.title(f'Cumulative Regret - {env_name}')
    plt.xlabel('Steps')
    plt.ylabel('Cumulative Regret')
    plt.legend()
    
    plt.subplot(2, 1, 2)
    for i, freqs in enumerate(best_arm_freqs):
        plt.plot(freqs, label=algorithm_names[i])
    plt.title(f'Best Arm Frequency - {env_name}')
    plt.xlabel('Steps')
    plt.ylabel('Frequency')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(f'{env_name}_results.png')
    plt.close()