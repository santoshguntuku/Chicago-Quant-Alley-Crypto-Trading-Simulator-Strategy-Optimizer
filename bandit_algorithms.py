import numpy as np
import math
from scipy.stats import beta, norm

class EpsilonGreedy:
    def __init__(self, n_arms, epsilon=0.1):
        self.n_arms = n_arms
        self.epsilon = epsilon
        self.counts = [0] * n_arms
        self.values = [0.0] * n_arms

    def select_arm(self):
        if np.random.random() < self.epsilon:
            return np.random.randint(self.n_arms)
        else:
            return np.argmax(self.values)

    def update(self, chosen_arm, reward):
        self.counts[chosen_arm] += 1
        n = self.counts[chosen_arm]
        self.values[chosen_arm] = ((n - 1) * self.values[chosen_arm] + reward) / n

class UCB1:
    def __init__(self, n_arms):
        self.n_arms = n_arms
        self.counts = [0] * n_arms
        self.values = [0.0] * n_arms
        self.total_counts = 0

    def select_arm(self):
        for arm in range(self.n_arms):
            if self.counts[arm] == 0:
                return arm
        ucb_values = [
            self.values[arm] + math.sqrt(2 * math.log(self.total_counts) / self.counts[arm])
            for arm in range(self.n_arms)
        ]
        return np.argmax(ucb_values)

    def update(self, chosen_arm, reward):
        self.total_counts += 1
        self.counts[chosen_arm] += 1
        n = self.counts[chosen_arm]
        self.values[chosen_arm] = ((n - 1) * self.values[chosen_arm] + reward) / n

class ThompsonSampling:
    def __init__(self, n_arms):
        self.n_arms = n_arms
        self.alpha = [1] * n_arms
        self.beta = [1] * n_arms

    def select_arm(self):
        samples = [beta.rvs(a, b) for a, b in zip(self.alpha, self.beta)]
        return np.argmax(samples)

    def update(self, chosen_arm, reward):
        self.alpha[chosen_arm] += reward
        self.beta[chosen_arm] += 1 - reward

class Exp3:
    def __init__(self, n_arms, eta=0.1, gamma=0.1):
        self.n_arms = n_arms
        self.eta = eta
        self.gamma = gamma
        self.weights = [1.0] * n_arms
        self.last_probs = None

    def select_arm(self):
        total = sum(self.weights)
        probs = [(1 - self.gamma) * (w / total) + self.gamma / self.n_arms for w in self.weights]
        arm = np.random.choice(self.n_arms, p=probs)
        self.last_probs = probs
        return arm

    def update(self, chosen_arm, reward):
        prob = self.last_probs[chosen_arm]
        loss_hat = (1 - reward) / prob
        self.weights[chosen_arm] *= math.exp(-self.eta * loss_hat)

class LinUCB:
    def __init__(self, n_arms, dim, alpha=1.0):
        self.n_arms = n_arms
        self.dim = dim
        self.alpha = alpha
        self.A = [np.eye(dim) for _ in range(n_arms)]
        self.b = [np.zeros(dim) for _ in range(n_arms)]
        self.A_inv = [np.eye(dim) for _ in range(n_arms)]
        self.theta = [np.zeros(dim) for _ in range(n_arms)]

    def select_arm(self, contexts):
        scores = []
        for arm in range(self.n_arms):
            x = contexts[arm]
            score = np.dot(self.theta[arm], x) + self.alpha * math.sqrt(np.dot(x.T, np.dot(self.A_inv[arm], x)))
            scores.append(score)
        return np.argmax(scores)

    def update(self, chosen_arm, reward, context):
        x = context
        A_inv = self.A_inv[chosen_arm]
        u = np.dot(A_inv, x)
        v = np.dot(x, u)
        self.A_inv[chosen_arm] = A_inv - np.outer(u, u) / (1 + v)
        self.b[chosen_arm] += reward * x
        self.theta[chosen_arm] = np.dot(self.A_inv[chosen_arm], self.b[chosen_arm])

class ExploreThenCommit:
    def __init__(self, n_arms, explore_rounds_per_arm):
        self.n_arms = n_arms
        self.explore_rounds_per_arm = explore_rounds_per_arm
        self.counts = [0] * n_arms
        self.values = [0.0] * n_arms # Store sum of rewards for simple average calculation
        self.t = 0
        self.exploration_complete = False
        self.best_arm_explored = -1 # Will store the index of the best arm found during exploration

    def select_arm(self):
        if not self.exploration_complete:
            # Exploration phase: pull arms sequentially or randomly until explore_rounds_per_arm is met for all.
            # A common way is to cycle through arms.
            arm_to_pull = self.t % self.n_arms
            if self.counts[arm_to_pull] < self.explore_rounds_per_arm:
                return arm_to_pull
            else:
                # Check if all arms have been explored enough
                if all(c >= self.explore_rounds_per_arm for c in self.counts):
                    self.exploration_complete = True
                    # Calculate empirical means and find the best arm
                    empirical_means = [v / c if c > 0 else -np.inf for v, c in zip(self.values, self.counts)]
                    self.best_arm_explored = np.argmax(empirical_means)
                    return self.best_arm_explored # Pull the best arm for the first time in commit phase
                else:
                    # Continue cycling through arms until all are explored
                    return arm_to_pull # This branch might need refinement based on exact exploration strategy
        
        # Commitment phase: always pull the best arm found during exploration
        return self.best_arm_explored

    def update(self, chosen_arm, reward):
        self.counts[chosen_arm] += 1
        self.values[chosen_arm] += reward # Sum of rewards
        self.t += 1 # Increment total time step

# Placeholder classes for other algorithms (ETC, KL-UCB, etc.)
# Implement similarly with select_arm and update methods