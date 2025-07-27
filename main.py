import numpy as np
from environments import BernoulliEnvironment, GaussianEnvironment, ContextualLinearEnvironment
from bandit_algorithms import EpsilonGreedy, UCB1, ThompsonSampling, Exp3, LinUCB
from experiment import run_experiment, plot_results

# Experiment parameters
n_arms = 10
T = 10000
n_simulations = 10

# Create environments
bernoulli_env = BernoulliEnvironment(
    n_arms, 
    probabilities=np.random.uniform(0.1, 0.9, n_arms)
)

gaussian_env = GaussianEnvironment(
    n_arms,
    means=np.random.normal(0, 1, n_arms)
)

contextual_env = ContextualLinearEnvironment(
    n_arms,
    dim=5,
    theta_star=np.random.normal(size=5)
)

# Algorithms to test
algorithms = {
    "Bernoulli": [
        EpsilonGreedy(n_arms, epsilon=0.1),
        UCB1(n_arms),
        ThompsonSampling(n_arms),
        Exp3(n_arms, eta=0.1, gamma=0.1)
    ],
    "Gaussian": [
        EpsilonGreedy(n_arms, epsilon=0.1),
        UCB1(n_arms),
        ThompsonSampling(n_arms),
        Exp3(n_arms, eta=0.1, gamma=0.1)
    ],
    "Contextual": [
        LinUCB(n_arms, dim=5, alpha=1.0)
    ]
}

# Run experiments and plot results
for env_name, env in [("Bernoulli", bernoulli_env), ("Gaussian", gaussian_env)]:
    cumulative_regrets = []
    best_arm_freqs = []
    algorithm_names = [
        "EpsilonGreedy", "UCB1", "ThompsonSampling", "Exp3"
    ]
    
    for alg in algorithms[env_name]:
        avg_cumulative_regret = np.zeros(T)
        avg_best_arm_freq = np.zeros(T)
        
        for _ in range(n_simulations):
            cumulative_rewards, best_arm_counts, _ = run_experiment(
                alg, env, T
            )
            optimal_rewards = env.best_prob if env_name == "Bernoulli" else env.best_mean
            cumulative_regret = np.arange(1, T+1) * optimal_rewards - cumulative_rewards
            best_arm_freq = best_arm_counts / np.arange(1, T+1)
            
            avg_cumulative_regret += cumulative_regret
            avg_best_arm_freq += best_arm_freq
        
        avg_cumulative_regret /= n_simulations
        avg_best_arm_freq /= n_simulations
        
        cumulative_regrets.append(avg_cumulative_regret)
        best_arm_freqs.append(avg_best_arm_freq)
    
    plot_results(algorithms[env_name], algorithm_names, env_name, cumulative_regrets, best_arm_freqs)

# Contextual experiment
cumulative_regrets = []
best_arm_freqs = []
algorithm_names = ["LinUCB"]

for _ in range(n_simulations):
    alg = LinUCB(n_arms, dim=5, alpha=1.0)
    cumulative_rewards, best_arm_counts, contexts = run_experiment(
        alg, contextual_env, T, is_contextual=True
    )
    # Calculate optimal rewards for contextual setting
    optimal_rewards = np.zeros(T)
    for t in range(T):
        optimal_arm = np.argmax([np.dot(contextual_env.theta_star, ctx) for ctx in contexts[t]])
        optimal_rewards[t] = np.dot(contextual_env.theta_star, contexts[t][optimal_arm])
    cumulative_rewards_optimal = np.cumsum(optimal_rewards)
    cumulative_regret = cumulative_rewards_optimal - cumulative_rewards
    best_arm_freq = best_arm_counts / np.arange(1, T+1)
    
    cumulative_regrets.append(cumulative_regret)
    best_arm_freqs.append(best_arm_freq)

avg_cumulative_regret = np.mean(cumulative_regrets, axis=0)
avg_best_arm_freq = np.mean(best_arm_freqs, axis=0)
plot_results([alg], algorithm_names, "Contextual", [avg_cumulative_regret], [avg_best_arm_freq])