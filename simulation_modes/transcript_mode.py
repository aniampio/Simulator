import simpy
import csv
from collections import namedtuple
import datetime
import time
import csv
import os
import random

import experiments.Settings
import classes.Utilities as ut
import classes.Net as nt
import classes.Client as ct


class Trace(object):
    __slots__ = ['sender', 'recipient', 'time', 'message', 'target']
    def __init__(self, sender, recipient, time, message, target=0):
        self.sender = sender
        self.recipient = recipient
        self.time = time
        self.message = message
        self.target = 0

    def __repr__(self):
        return "Sender: %s, Recipient: %s, Time: %s, Size: %s, Target: %s" % (self.sender.id, self.recipient.id, self.time, len(self.message.payload), self.target)


def get_loggers(log_dir):
	packet_logger = ut.setup_logger('simulation.packet', os.path.join(log_dir, 'packet_log.csv'))
	packet_logger.info(ut.StructuredMessage(metadata=("Type", "CurrentTime", "ClientID", "PacketID", "PacketType", "MessageID", "PacketTimeQueued", "PacketTimeSent", "PacketTimeDelivered", "TotalFragments", "PrOthers", "PrSenderA", "PrSenderB", "RealSenderLabel", "Route", "PoolSizes")))

	message_logger = ut.setup_logger('simulation.messages', os.path.join(log_dir, 'message_log.csv'))
	message_logger.info(ut.StructuredMessage(metadata=("Type", "CurrentTime", "ClientID", "MessageID", "NumPackets", "MsgTimeQueued", "MsgTimeSent", "MsgTimeDelivered", "MsgTransitTime", "MsgSize", "MsgRealSender")))

	loggers = (packet_logger, message_logger)
	return loggers


def create_network(env, confx):
    # Build a stratfied network
    net = nt.Network(env, confx)
    # print the whole network
    for m in net.MixNodes:
        m.set_network(net.topology)
    return net


def load_csv(dataFile):
    allData = []
    # read in the Riseup email data from the csv file.
    with open(dataFile, 'r') as inFile:
        reader = csv.reader(inFile)
        Row = namedtuple("Row", next(reader))
        for row in map(Row._make, reader):
            allData.append(row)
    print("All imported records: ", len(allData))
    return allData


def filter_data(allData):

    dataNT = allData[:]
    # pick only the records for which status == sent, is_outgoing == true and is_list == false
    # for d in dataNT:
    #     if '' not in d._asdict().values():
    #         print("Hello")
    dataFiltered = [d for d in dataNT if d.status == "sent" and d.is_outgoing == "t" and d.is_list == "f"]

    dataFinal = []
    # parse str time to float time
    FilteredRow = namedtuple('FilteredRow', ['sender', 'recipient', 'first_seen_at', 'size', 'is_outgoing', 'is_list', 'status'])
    for d in dataFiltered:
        tmp = FilteredRow(d.sender, d.recipient, time.mktime(datetime.datetime.strptime(d.first_seen_at, '%Y-%m-%d %H:%M:%S').timetuple()), d.size, d.is_outgoing, d.is_list, d.status)
        dataFinal.append(tmp)

    # sort the data based on the time when a message was sent
    dataFinal.sort(key=lambda x: x.first_seen_at)
    print("Number of records valid for analysis: ", len(dataFinal))
    return dataFinal


def schedule_transcript_messages(env, transcript):
    '''
		schedule_transcript_run schedules all transcript traces to be triggered.
		The transcript is ordered from the earlies event. A trace = (message, sender,
		recipient, t) is popped from the transcript and scheduled as an event
		by requesting the client sender to send the message to the recipient
		at time t.
    '''
    # sorting the transcript by time from the oldest to the newest
    print("> Started scheduling messages from the transcript")
    transcript.sort(key=lambda x: -x.time)
    start_time = env.now

    # take top message (i.e., the earliest one) and schedule it for sending
    # when done, schedule the next call
    while True:
        trace = transcript.pop()
        print("> Selected trace")
        sender = trace.sender
        recipient = trace.recipient
        time = trace.time
        message = trace.message
        if len(transcript) == 0:
            env.finished = True
            break
        delay = (start_time + time) - env.now
        print("Generated delay: ", delay)
        yield env.timeout(delay)
        print("> Delayed")

        # schedule the message to be sent by adding to the clients outgoing buffer
        sender.schedule_message(message)
    print("> Finished scheduling messages from the transcript")


def setup_transcript(dataFiltered, exp_dir, confx):

    # CREATE SIMPY ENVIRONMENT
    env = simpy.Environment()
    env.stop_sim_event = env.event()
    env.finished = False
    env.message_ctr = 0

    print("> Created simpy env")

    # Create the network
    net = create_network(env, confx)
    print("> Created network")

    # take all ids of the senders in the transcript
    senderIds = set()
    total = set([s.sender for s in dataFiltered])
    if len(total) > 10:
        senderIds = random.sample(total, 10)

    # take records of data for only the selected senders
    senderIds = set(senderIds)
    newDataFiltered = [d for d in dataFiltered if d.sender in senderIds]
    print("> Selected sample senders")

    # pick target senders
    ctr = 0
    while ctr < 50:
        pick1 = random.choice(newDataFiltered)
        pick2 = random.choice(newDataFiltered)
        if pick1.sender != pick2.sender and pick1.recipient != pick2.recipient and pick1.sender != pick2.recipient and pick1.recipient != pick2.sender:
            break
        elif ctr == 50:
            print('Data is shit')
        ctr += 1
    print("> Picked target senders and recipient")

    pick1Sender = pick1.sender
    pick1Recipient = pick1.recipient
    pick2Sender = pick2.sender
    pick2Recipient = pick2.recipient

    # remove all records where target senders and sending elsewhere that target recipients
    newNewDataFiltered = []
    for n in newDataFiltered:
        if n.sender == pick1Sender and n.recipient != pick1Recipient:
            continue
        elif n.sender == pick2Sender and n.recipient != pick2Recipient:
            continue
        else:
            newNewDataFiltered.append(n)
    print("> Removed all records where target senders are sending elsewhere than the target recipients")

    # take ids of all clients from the final filtered data to create objects
    clientsIds = set()
    for d in newNewDataFiltered:
        clientsIds.add(d.sender)
        clientsIds.add(d.recipient)


    # Create loggers
    log_dir= os.path.join(exp_dir, confx["logging"]["dir"])
    loggers = get_loggers(log_dir)

    # create objects of clients
    clientsObj = {}
    for idx in clientsIds:
        if idx == pick1Sender:
            clientsObj[idx] = ct.Client(env, confx, net, loggers=loggers, label=1, id=idx)
        elif idx == pick2Sender:
            clientsObj[idx] = ct.Client(env, confx, net, loggers=loggers, label=2, id=idx)
        else:
            clientsObj[idx] = ct.Client(env, confx, net, loggers=loggers, label=0, id=idx)
    print("> Created all clients objects")

    # create traces
    traces = []
    for row in newNewDataFiltered:
        tmpSender = clientsObj[row.sender]
        tmpRecipient = clientsObj[row.recipient]

        fake_payload = '0' * int(row.size)
        msg = nt.Message(conf=confx, payload=fake_payload, dest=tmpRecipient, topology=net.topology, real_sender=tmpSender)
        traces.append(Trace(sender=tmpSender, recipient=tmpRecipient, time=row.first_seen_at, message=msg))
    print("> Created all traces")

    min_time = min(traces, key = lambda t: t.time).time
    for t in traces:
        t.time = t.time - min_time
        print("Actual time: ", t.time)

    # for c in clientsObj.values():
    #     env.process(c.start(c))
    #
    # env.process(schedule_transcript_messages(env, traces))
    #
    # print(" ---------Simulation started---------")
    # time_start = datetime.datetime.now()
    # env.run(until=env.stop_sim_event)
    # time_finished = datetime.datetime.now()
    # print(" ---------Finished " + str(time_finished) + "---------")
    # print(" ---------Simulation total time (in seconds): %f ----------" % (time_finished - time_start).total_seconds())


def run(data_file, conf_dir, exp_dir):

    # IMPORT WHOLE DATA
    data = load_csv(data_file)
    dataFiltered = filter_data(data)
    print("> Email data uploaded")

    # Read in configuration file
    confx = experiments.Settings.load(conf_dir)
    print("> Config file uploaded")

    setup_transcript(dataFiltered, exp_dir, confx)


# handlers = logging._handlers.copy()
# for h in handlers:
# 	h.flush()
# 	h.close()
# 	for l in loggers:
# 		l.removeHandler(h)

if __name__ == "__main__":
    run()
