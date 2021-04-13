import numpy as np


def computeThroughput(df):
    throughput = []
    for i, r in df.iterrows():
        transitTime = r['MsgTransitTime']
        messagesTotalSize = r['MsgSize']
        throughput.append(messagesTotalSize/transitTime)
    return np.mean(throughput)


def computePacketE2ELatency(df):
	travelTime = []
	for i, r in df.iterrows():
		timeSent = r['PacketTimeSent']
		timeDelivered = r['PacketTimeDelivered']
		travelTime.append(timeDelivered - timeSent)
	return np.mean(travelTime)


def computeMessageE2ELatency(df):
	''' computes the e2e latency of a message: from the time the message was queued to the time the message was delivered'''
	totalDeliveryTimes = []
	for i, r in df.iterrows():
		timeQ = r['MsgTimeQueued']
		timeD = r['MsgTimeDelivered']
		totalDeliveryTimes.append(timeD - timeQ)
	return np.mean(totalDeliveryTimes)


def computeMessageTransitLatency(df):
	totalTransitTimes = []
	for i, r in df.iterrows():
		totalTransitTimes.append(r['MsgTransitTime'])
	return np.mean(totalTransitTimes)


def computePacketQueuingTime(df):
	queuingTimes = []
	for i, r in df.iterrows():
		timeQ = r['PacketTimeQueued']
		timeS = r['PacketTimeSent']
		queuingTimes.append(timeS-timeQ)
	return np.mean(queuingTimes)

def computeMessageQueuingTime(df):
    queuingTimes = []
    for i, r in df.iterrows():
        timeQ = r['MsgTimeQueued']
        timeS = r['MsgTimeSent']
        queuingTimes.append(timeS-timeQ)
    return np.mean(queuingTimes)
