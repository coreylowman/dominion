import matplotlib.pyplot as plt

games_trained = []

nnet_wins = []
nnet_points = []

bm_wins = []
bm_points = []

avg_length = []

with open('stats.txt') as fp:
    for line in fp:
        if line.startswith('Amount trained'):
            games_trained.append(int(line.split()[-2]))

        if line.startswith('Avg length'):
            avg_length.append(float(line.split()[2]))

        if line.startswith('BM'):
            parts = line.split('\t')
            bm_wins.append(int(parts[1].split(' ')[0]))
            bm_points.append(float(parts[3]))

        if line.startswith('NNet'):
            parts = line.split('\t')
            nnet_wins.append(int(parts[1].split(' ')[0]))
            nnet_points.append(float(parts[3]))

# plt.subplot(211)
plt.title('Average points')
plt.plot(games_trained, nnet_points, label='NNet')
plt.plot(games_trained, bm_points, label='BM')
plt.legend()
plt.ylim(0, 55)
plt.xlabel('Number of games NNet trained')

# plt.subplot(212)
# plt.title('Wins')
# plt.plot(games_trained, nnet_wins, label='NNet')
# plt.plot(games_trained, bm_wins, label='BM')
# plt.legend()

plt.xlabel('Number of games NNet trained')

plt.show()
