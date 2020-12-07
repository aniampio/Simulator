import math
import random
import scipy.special
import numpy as np
from operator import attrgetter
from collections import namedtuple
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.style as style
import seaborn as sns
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
style.use('ggplot')
plt.rcParams['legend.title_fontsize'] = 12


def probability_fully_malicious_stratified(malicious_mixes, cascade_length, nodes_per_layer):
    top = math.factorial(malicious_mixes)
    bottom = (nodes_per_layer**cascade_length) * (cascade_length**cascade_length) * (math.factorial(malicious_mixes - cascade_length))
    return top / bottom

def simulate(allNodes, mm, cl):
    nodes_per_layer = int(allNodes / cl)
    layers = {}
    for i in range(cl):
        layers[i] = list(np.zeros(nodes_per_layer))

    for x in range(mm):
        j = random.randint(0, cl-1)
        while True:
            idx = random.randint(0, nodes_per_layer-1)
            if layers[j][idx] == 0:
                layers[j][idx] = 1
                break

    path = []
    for k in layers.keys():
        path.append(random.choice(layers[k]))

    if all(v == 1 for v in path):
        return True
    else:
        return False


def p2p_fully_malicious(mal, all):
    # calculation for a peer to peer network, with possible path lengths 1-2-3:
    forL1 = scipy.special.binom(mal, 1) /  scipy.special.binom(all, 1)
    forL2 = scipy.special.binom(mal, 2) /  scipy.special.binom(all, 2)
    forL3 = scipy.special.binom(mal, 3) /  scipy.special.binom(all, 3)
    #
    total = 1.00/3.00 * (forL1 + forL2 + forL3)
    return total

def p2p_fully_malicious_length_3_all(mal, all):
    return scipy.special.binom(mal, 3) /  scipy.special.binom(all, 3)


def plot1():
        lengths = [3,4,5,6]
        percentage = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

        StatStrat = namedtuple('StatNym', ['m', 'cl', 'pm', 'mm', 'per_layer', 'probability'])
        allStatsStrat = []

        cl = 3
        allNodes = cl*450
        for p in percentage:
            nodes_per_layer = int(allNodes / cl)
            mm = round(p * allNodes)
            probability = probability_fully_malicious_stratified(mm, cl, nodes_per_layer)
            stats = StatStrat(m=allNodes, cl=cl, pm=p, mm=mm, per_layer=nodes_per_layer, probability=probability)
            allStatsStrat.append(stats)

        cl = 4
        allNodes = cl*450
        for p in percentage:
            nodes_per_layer = int(allNodes / cl)
            mm = round(p * allNodes)
            probability = probability_fully_malicious_stratified(mm, cl, nodes_per_layer)
            stats = StatStrat(m=allNodes, cl=cl, pm=p, mm=mm, per_layer=nodes_per_layer, probability=probability)
            allStatsStrat.append(stats)

        cl = 5
        allNodes = cl*450
        for p in percentage:
            nodes_per_layer = int(allNodes / cl)
            mm = round(p * allNodes)
            probability = probability_fully_malicious_stratified(mm, cl, nodes_per_layer)
            stats = StatStrat(m=allNodes, cl=cl, pm=p, mm=mm, per_layer=nodes_per_layer, probability=probability)
            allStatsStrat.append(stats)

        cl = 6
        allNodes = cl*450
        for p in percentage:
            nodes_per_layer = int(allNodes / cl)
            mm = round(p * allNodes)
            probability = probability_fully_malicious_stratified(mm, cl, nodes_per_layer)
            stats = StatStrat(m=allNodes, cl=cl, pm=p, mm=mm, per_layer=nodes_per_layer, probability=probability)
            allStatsStrat.append(stats)

        print("Computed from formula")
        sortedAllStatsStrat = sorted(allStatsStrat, key=attrgetter('cl'))
        for x in sortedAllStatsStrat:
            print(x)

        dataCl3 = [(x.pm, x.probability) for x in sortedAllStatsStrat[0:7]]
        dataCl4 = [(x.pm, x.probability) for x in sortedAllStatsStrat[7:14]]
        dataCl5 = [(x.pm, x.probability) for x in sortedAllStatsStrat[14:21]]
        dataCl6 = [(x.pm, x.probability) for x in sortedAllStatsStrat[21:28]]

        palette = plt.get_cmap('inferno', 5)
        fig = plt.figure()
        ax = plt.axes()
        ax.plot(*zip(*dataCl3), 'o-', label = 3, color=palette(1), linewidth=2, markersize=8, alpha=0.7)
        ax.plot(*zip(*dataCl4), 'v-', label = 4, color=palette(2), linewidth=2, markersize=8, alpha=0.7)
        ax.plot(*zip(*dataCl5), 's-', label = 5, color=palette(3), linewidth=2, markersize=8, alpha=0.7)
        ax.plot(*zip(*dataCl6), 'd-', label = 6, color=palette(4), linewidth=2, markersize=8, alpha=0.7)
        ax.set_ylim(bottom=0, top=0.6)
        ax.grid(True, linestyle="dashed")
        ax.xaxis.set_tick_params(labelsize=10)
        ax.yaxis.set_tick_params(labelsize=10)
        ax.legend(title="Route length", prop={'size': 12})
        plt.xlabel('Percentage of malicious mix nodes in the network', fontsize=14, labelpad=10)
        plt.ylabel('Probability of picking a fully-malicious route', fontsize=14, labelpad=10)
        plt.show()

def plot2():

    percentage = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

    StatStrat = namedtuple('StatNym', ['m', 'cl', 'pm', 'mm', 'per_layer', 'probability'])
    allStatsStrat = []


    allNodes = 3*100
    cl = 3
    for p in percentage:
        nodes_per_layer = int(allNodes / cl)
        mm = round(p * allNodes)
        probability = probability_fully_malicious_stratified(mm, cl, nodes_per_layer)
        stats = StatStrat(m=allNodes, cl=cl, pm=p, mm=mm, per_layer=nodes_per_layer, probability=probability)
        allStatsStrat.append(stats)



    allNodes = 3*100
    cl = 3
    for p in percentage:
        nodes_per_layer = int(allNodes / cl)
        mm = round(p * allNodes)
        probability = probability_fully_malicious_stratified(mm, cl, nodes_per_layer)
        stats = StatStrat(m=allNodes, cl=cl, pm=p, mm=mm, per_layer=nodes_per_layer, probability=probability)
        allStatsStrat.append(stats)


    allNodes = 3*1000
    cl = 3
    for p in percentage:
        nodes_per_layer = int(allNodes / cl)
        mm = round(p * allNodes)
        probability = probability_fully_malicious_stratified(mm, cl, nodes_per_layer)
        stats = StatStrat(m=allNodes, cl=cl, pm=p, mm=mm, per_layer=nodes_per_layer, probability=probability)
        allStatsStrat.append(stats)


    allNodes = 3*10000
    cl = 3
    for p in percentage:
        nodes_per_layer = int(allNodes / cl)
        mm = round(p * allNodes)
        probability = probability_fully_malicious_stratified(mm, cl, nodes_per_layer)
        stats = StatStrat(m=allNodes, cl=cl, pm=p, mm=mm, per_layer=nodes_per_layer, probability=probability)
        allStatsStrat.append(stats)


    print("Computed from formula")
    sortedAllStatsStrat = sorted(allStatsStrat, key=attrgetter('cl'))
    for x in sortedAllStatsStrat:
        print(x)


    dataCl3 = [(x.pm, x.probability) for x in sortedAllStatsStrat[0:7]]
    # dataCl4 = [(x.pm, x.probability) for x in sortedAllStatsStrat[7:14]]
    # dataCl5 = [(x.pm, x.probability) for x in sortedAllStatsStrat[14:21]]
    # dataCl6 = [(x.pm, x.probability) for x in sortedAllStatsStrat[21:28]]


    palette = plt.get_cmap('inferno', 5)
    fig = plt.figure()
    ax = plt.axes()
    ax.plot(*zip(*dataCl3), 'o-', label = '100', color=palette(1), linewidth=2, markersize=8, alpha=0.7)
    # ax.plot(*zip(*dataCl4), 'v-', label = '100', color=palette(2), linewidth=2, markersize=8, alpha=0.7)
    # ax.plot(*zip(*dataCl5), 's-', label = '1000', color=palette(3), linewidth=2, markersize=8, alpha=0.7)
    # ax.plot(*zip(*dataCl6), 'd-', label = 6, color=palette(4), linewidth=2, markersize=8, alpha=0.7)

    ax.legend(title="Number of nodes", prop={'size': 12})
    plt.xlabel('Percentage of malicious mix nodes in the network', fontsize=14, labelpad=10)
    plt.ylabel('Probability of picking a fully-malicious route', fontsize=14, labelpad=10)
    plt.title("Probability of picking fully malicious path in a 3x100 mixnet")
    plt.show()


if __name__ == "__main__":

    plot1()
