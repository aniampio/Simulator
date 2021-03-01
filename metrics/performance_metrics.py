import numpy as np


def computeThroughput(df):
    throughput = []
    for i, r in df.iterrows():
        transitTime = r['MsgTransitTime']
        messagesTotalSize = r['MsgSize']
        throughput.append(messagesTotalSize/transitTime)
    return np.mean(throughput)
