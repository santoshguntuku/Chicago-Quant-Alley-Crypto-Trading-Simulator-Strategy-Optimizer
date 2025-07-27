import numpy as np

class BernoulliEnvironment:
    def __init__(self, n_arms, probabilities):
        self.n_arms = n_arms
        self.probabilities = probabilities
        self.best_arm = np.argmax(probabilities)
        self.best_prob = probabilities[self.best_arm]

    def get_reward(self, arm):
        return 1 if np.random.random() < self.probabilities[arm] else 0

class GaussianEnvironment:
    def __init__(self, n_arms, means, std_dev=1.0):
        self.n_arms = n_arms
        self.means = means
        self.std_dev = std_dev
        self.best_arm = np.argmax(means)
        self.best_mean = means[self.best_arm]

    def get_reward(self, arm):
        return np.random.normal(self.means[arm], self.std_dev)

class ContextualLinearEnvironment:
    def __init__(self, n_arms, dim, theta_star, std_dev=0.1):
        self.n_arms = n_arms
        self.dim = dim
        self.theta_star = theta_star
        self.std_dev = std_dev

    def get_contexts(self):
        return np.random.normal(size=(self.n_arms, self.dim))

    def get_reward(self, arm, context):
        mean = np.dot(self.theta_star, context[arm])
        return np.random.normal(mean, self.std_dev)