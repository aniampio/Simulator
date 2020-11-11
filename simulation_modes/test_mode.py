import simpy
import os
import datetime
import numpy as np


import experiments.Settings

from classes.Net import *
from classes.Client import *
from classes.Net import *
from classes.Utilities import *


throughput = 0.0

def progress_update(env, interval=5):
    while True:
        yield env.timeout(interval)
        print("Current time tick is: " + str(env.now))


def build_network(env, layers, mixnodes_per_layer, num_in, num_out):
    return Network(env, layers, mixnodes_per_layer, num_in, num_out)

def get_loggers(log_dir):
    packet_logger = setup_logger('simulation.packet', os.path.join(log_dir, 'packet_log.csv'))
    packet_logger.info(StructuredMessage(metadata=("Type", "CurrentTime", "ClientID", "PacketID", "PacketType", "MessageID", "PacketTimeQueued", "PacketTimeSent", "PacketTimeDelivered", "TotalFragments", "PrOthers", "PrSenderA", "PrSenderB", "RealSenderLabel", "Route", "PoolSizes")))

    message_logger = setup_logger('simulation.messages', os.path.join(log_dir, 'message_log.csv'))
    message_logger.info(StructuredMessage(metadata=("Type", "CurrentTime", "ClientID", "MessageID", "NumPackets", "MsgTimeQueued", "MsgTimeSent", "MsgTimeDelivered", "MsgTransitTime", "MsgSize", "MsgRealSender")))

    entropy_logger = setup_logger('simulation.mix', os.path.join(log_dir, 'last_mix_entropy.csv'))
    entropy_logger.info(StructuredMessage(metadata=tuple(['Entropy'+str(x) for x in range(100)])))

    return (packet_logger, message_logger, entropy_logger)



def run(exp_dir, conf_file=None, conf_dic=None):
    ''' Creates an experimental run of the simulator with the settings in the signature above or reading from a configuration file'''
    print("The experiment log directory is: %s" %exp_dir)

    if conf_file:
        print("The config file is at:%s" %conf_file)
        conf = experiments.Settings.load(conf_file)
    elif conf_dic:
        conf = conf_dic
    else:
        print("A configuration dictionary or file required")

    log_dir = os.path.join(exp_dir,conf["logging"]["dir"])

    # ------ config, loggers and env ----------
    verbose=conf["debug"]["mixnodes_verbose"]

    loggers = get_loggers(log_dir)
    mix_logger = setup_logger('simulation.mix', os.path.join(log_dir, 'mix_logger.csv'))


    env = simpy.Environment()
    env.stop_sim_event = env.event()
    env.message_ctr = 0
    env.total_messages_sent = 0
    env.total_messages_received = 0
    env.finished = False
    env.entropy = numpy.zeros(100)

    # ------- creating mix network -------------
    type = "stratified"
    net = Network(env, type, conf, loggers)

    # -------- timing for how long to run the simulation ----------
    limittime = conf["phases"]["burnin"] + conf["phases"]["execution"] # time after which we should terminate the target senders from sending
    simtime = conf["phases"]["burnin"] +  conf["phases"]["execution"] + conf["phases"]["cooldown"] # time after which the whole simulator stops

    # Creating so called "other" users, who will only send dummy traffic
    otherClients = net.clients
    print("> Number of clients started: ", len(net.clients))
    # for s in range(conf["clients"]["number"] - 3):
    #     sender = Client(env, conf, net, loggers = loggers, label=0)
    #     otherClients.append(sender)

    sender = otherClients[0]
    for c in otherClients:
        env.process(sender.start(random.choice(otherClients)))
        # env.process(Sender.start_ack_sending())
        # env.process(sender.terminate(limittime))

    # Creating a target recipient recipient
    recipient = Client(env, conf, net, loggers = loggers, label=0)
    # print("> Recipient: %s" % recipient.id)
    recipient.verbose = True

    env.process(recipient.set_start_logs())
    print("> Logging turned on")
    env.process(recipient.start(random.choice(otherClients)))

    SenderT1 = Client(env, conf, net, loggers = loggers, label = 1)
    SenderT1.verbose = True
    # print("> Sender A: ", SenderT1.id)
    # env.process(SenderT1.terminate(limittime))
    env.process(SenderT1.start(random.choice(otherClients)))

    SenderT2 = Client(env, conf, net, loggers = loggers, label = 2)
    SenderT2.verbose = True
    # print("> Sender B: ", SenderT2.id)
    # env.process(SenderT2.terminate(limittime))
    env.process(SenderT2.start(random.choice(otherClients)))

    # env.process(recipient.start_ack_sending())
    # env.process(recipient.terminate(limittime))

    print("---------" + str(datetime.datetime.now()) + "---------")
    print("> Running the system for %s ticks to prepare it for measurment." % (conf["phases"]["burnin"]))

    # env.process(progress_update(env, 5))
    time_started = env.now
    time_started_unix = datetime.datetime.now()
    # ------ RUNNING THE STARTUP PHASE ----------
    if conf["phases"]["burnin"] > 0.0:
        env.run(until=conf["phases"]["burnin"])
    print("> Finished the preparation")

    # Start logging since system in steady state
    for m in net.mixnodes:
        m.mixlogging = True
    # print("---------" + str(time_started) + "---------")
    # print("> Now: " + str(env.now) + ", Simulation Duration: " + str(conf["phases"]["execution"]) + ", Running until: " + str(limittime) + ", Cooling-down until: " + str(simtime))

    # ------ RUNNING THE MAIN SIMULATION PHASE ----------
    # --------- Only SenderT1 is sending REAL packets to the target recipient --------------
    env.process(SenderT1.simulate_real_traffic(recipient))
    # print("> Turned on generating traffic")

    # env.process(SenderT1.start_ack_sending())
    # if conf["clients"]["retransmit"]:
    #     env.process(SenderT1.schedule_retransmits())

    # env.process(SenderT2.start_ack_sending())
    # if conf["clients"]["retransmit"]:
    #     env.process(SenderT2.schedule_retransmits())

    # env.run(until=simtime)
    env.run(until=env.stop_sim_event)  # Run until the stop_sim_event is triggered.
    print("> Main part of simulation finished. Starting cooldown phase.")

    # Log entropy
    net.loggers[2].info(StructuredMessage(metadata=tuple(env.entropy)))

    # ------ RUNNING THE COOLDOWN PHASE ----------
    if conf["phases"]["burnin"] > 0.0:
        env.run(until=env.now + conf["phases"]["cooldown"])

    print("> Cooldown phase finished.")
    time_finished = env.now
    time_finished_unix = datetime.datetime.now()
    # print("Reciever received: ", recipient.num_received_packets)
    print("> Total Simulation Time [in ticks]: " + str(time_finished-time_started) + "---------")
    print("> Total Simulation Time [in unix time]: " + str(time_finished_unix-time_started_unix) + "---------")

    for l in loggers:
        for h in l.handlers:
            h.flush()
    for h in mix_logger.handlers:
        h.flush()


    global throughput
    throughput = float(env.total_messages_received) / float(time_finished-time_started)

    mixthroughputs = []
    for m in net.mixnodes:
        mixthroughputs.append(float(m.pkts_sent) / float(time_finished-time_started))

    print("Network throughput %f / second: " % throughput)
    print("Average mix throughput %f / second, with std: %f" % (np.mean(mixthroughputs), np.std(mixthroughputs)))
