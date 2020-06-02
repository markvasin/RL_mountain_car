import gym
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class RBFFeatureTransformer:
    def __init__(self, env, n_basis=100):
        observation_examples = np.array([env.observation_space.sample() for x in range(10000)])
        scaler = StandardScaler()
        scaler.fit(observation_examples)
        scaled_examples = scaler.transform(observation_examples)
        kmeans = KMeans(n_clusters=n_basis, random_state=0).fit(scaled_examples)

        self.sigma = np.std(scaled_examples)
        self.basis_center = kmeans.cluster_centers_
        self.dimension = n_basis
        self.scaler = scaler

    def featurize_state(self, state):
        X = self.scaler.transform([state])
        N = X.shape[0]
        U = np.zeros((N, self.dimension))
        for i in range(N):
            for j in range(self.dimension):
                U[i][j] = self.gaussian(X[i], self.basis_center[j], self.sigma)

        return U

    def gaussian(self, x, u, sigma):
        return np.exp(-0.5 * np.linalg.norm(x - u) / sigma)


class RLModel:

    def __init__(self, env, feature_transformer):
        self.feature_transformer = feature_transformer
        self.w = np.zeros((env.action_space.n, feature_transformer.dimension))

    def q(self, states, action):
        features = self.feature_transformer.featurize_state(states)
        return np.dot(features, self.w[action])

    def epsilon_greedy(self, state):
        features = self.feature_transformer.featurize_state(state)
        yh = features @ self.w.T
        if np.random.uniform(low=0, high=1) < epsilon:
            chosen_action = np.random.choice(env.action_space.n)
        else:
            chosen_action = np.argmax(yh)
        return chosen_action

    def sarsa_update(self, lr, reward, gamma, state, action, next_state, next_action):
        feature = feature_transformer.featurize_state(state).flatten()
        self.w[action] += lr * (reward + gamma * self.q(next_state, next_action) - self.q(state, action)) * feature


if __name__ == '__main__':
    env = gym.make("MountainCar-v0")
    obs = env.reset()
    env.render()

    # initializations
    episodes = 500
    alpha = 0.01  # learning rate
    gamma = 0.99  # discount factor
    epsilon = 0.05  # epsilon greedy policy
    env = env.unwrapped
    env.seed()
    np.random.seed(0)
    n_basis = 200  # number of basis functions for RBF
    feature_transformer = RBFFeatureTransformer(env, n_basis)
    model = RLModel(env, feature_transformer)

    for episode in range(episodes):
        print("Episode:", episode)
        state = env.reset()
        step = 0
        total_reward = 0
        while True:
            # if episode >= (episodes - 1):
            #     env.render()
            env.render()
            action = model.epsilon_greedy(state)
            next_state, reward, terminate, _ = env.step(action)
            next_action = model.epsilon_greedy(next_state)
            model.sarsa_update(alpha, reward, gamma, state, action, next_state, next_action)

            if terminate:
                break

            step += 1
            total_reward += reward
            state = next_state

        print('Total steps:', step)
        print('Return:', total_reward)
        print()
    env.close()