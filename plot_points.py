import matplotlib.pyplot as plt

num_games_trained = 0
games_trained = []

nnet_wins = []
nnet_points = []

bm_wins = []
bm_points = []

with open('curr.log') as fp:
    for line in fp:
        if line.startswith('BM'):
            num_games_trained += 1000
            games_trained.append(num_games_trained)
            parts = line.split('\t')
            bm_wins.append(int(parts[1].split(' ')[0]))
            bm_points.append(float(parts[3]))

        if line.startswith('NNet'):
            parts = line.split('\t')
            nnet_wins.append(int(parts[1].split(' ')[0]))
            nnet_points.append(float(parts[3]))

plt.subplot(211)
plt.title('Average points')
plt.plot(games_trained, nnet_points, label='NNet')
plt.plot(games_trained, bm_points, label='BM')

plt.legend()

plt.subplot(212)
plt.title('Wins')
plt.plot(games_trained, nnet_wins, label='NNet')
plt.plot(games_trained, bm_wins, label='BM')
plt.xlabel('Number of games NNet trained')

plt.legend()

plt.show()
