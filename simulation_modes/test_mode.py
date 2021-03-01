import simpy
import os
import datetime
import time
import numpy as np
from collections import namedtuple


import experiments.Settings

from classes.Net import *
from classes.Client import *
from classes.Net import *
from classes.Utilities import *


throughput = 0.0

def get_loggers(log_dir, conf):

    packet_logger = setup_logger('simulation.packet', os.path.join(log_dir, 'packet_log.csv'))
    packet_logger.info(StructuredMessage(metadata=("Type", "CurrentTime", "ClientID", "PacketID", "PacketType", "MessageID", "PacketTimeQueued", "PacketTimeSent", "PacketTimeDelivered", "TotalFragments", "PrOthers", "PrSenderA", "PrSenderB", "RealSenderLabel", "Route", "PoolSizes")))

    message_logger = setup_logger('simulation.messages', os.path.join(log_dir, 'message_log.csv'))
    message_logger.info(StructuredMessage(metadata=("Type", "CurrentTime", "ClientID", "MessageID", "NumPackets", "MsgTimeQueued", "MsgTimeSent", "MsgTimeDelivered", "MsgTransitTime", "MsgSize", "MsgRealSender")))

    entropy_logger = setup_logger('simulation.mix', os.path.join(log_dir, 'last_mix_entropy.csv'))
    entropy_logger.info(StructuredMessage(metadata=tuple(['Entropy'+str(x) for x in range(get_total_num_of_target_packets(conf))])))

    return (packet_logger, message_logger, entropy_logger)


def setup_env(conf):
    env = simpy.Environment()
    env.stop_sim_event = env.event()
    env.stop_cool_down_event = env.event()
    env.message_ctr = 0
    env.total_messages_sent = 0
    env.total_messages_received = 0
    env.finished = False
    #env.entropy = numpy.zeros(int(conf["misc"]["num_target_messages"]))
    env.entropy = numpy.zeros(get_total_num_of_target_packets(conf))

    return env



def run_p2p(env, conf, net, loggers):
    print("Running P2P topology")
    peers = net.peers
    print("Number of active peers: ", len(peers))

    SenderT1 = peers.pop()
    SenderT1.label = 1
    SenderT1.verbose = True

    SenderT2 = peers.pop()
    SenderT2.label = 2
    SenderT2.verbose = True

    recipient = peers.pop()

    for c in peers:
        env.process(c.start(random.choice(peers)))
        env.process(c.start_loop_cover_traffic())

    env.process(SenderT1.start(dest=random.choice(peers)))
    env.process(SenderT1.start_loop_cover_traffic())
    env.process(SenderT2.start(dest=random.choice(peers)))
    env.process(SenderT2.start_loop_cover_traffic())
    env.process(recipient.set_start_logs())
    env.process(recipient.start(dest=random.choice(peers)))
    env.process(recipient.start_loop_cover_traffic())

    print("---------" + str(datetime.datetime.now()) + "---------")
    print("> Running the system for %s ticks to prepare it for measurement." % (conf["phases"]["burnin"]))

    # env.process(progress_update(env, 5))
    time_started = env.now
    time_started_unix = datetime.datetime.now()
    # ------ RUNNING THE STARTUP PHASE ----------
    if conf["phases"]["burnin"] > 0.0:
        env.run(until=conf["phases"]["burnin"])
    print("> Finished the preparation")

    # Start logging since system in steady state
    for p in net.peers:
        p.mixlogging = True

    env.process(SenderT1.simulate_real_traffic(recipient))
    print("> Started sending traffic for measurements")

    env.run(until=env.stop_sim_event)  # Run until the stop_sim_event is triggered.
    print("> Main part of simulation finished. Starting cooldown phase.")


    # ------ RUNNING THE COOLDOWN PHASE ----------
    env.run(until=env.now + conf["phases"]["cooldown"])


    # Log entropy
    loggers[2].info(StructuredMessage(metadata=tuple(env.entropy)))
    print("> Cooldown phase finished.")

    time_finished = env.now
    time_finished_unix = datetime.datetime.now()

    print("> Total Simulation Time [in ticks]: " + str(time_finished-time_started) + "---------")
    print("> Total Simulation Time [in unix time]: " + str(time_finished_unix-time_started_unix) + "---------")

    flush_logs(loggers)

    global throughput
    throughput = float(env.total_messages_received) / float(time_finished-time_started)

    mixthroughputs = []
    for p in net.peers:
        mixthroughputs.append(float(p.pkts_sent) / float(time_finished-time_started))

    print("Network throughput: %f [packets/s]" % throughput)
    print("Average mix throughput: %f [packets/s], with std: %f" % (np.mean(mixthroughputs), np.std(mixthroughputs)))



def run_client_server(env, conf, net, loggers):
    clients = net.clients
    print("Number of active clients: ", len(clients))

    SenderT1 = clients.pop()
    SenderT1.label = 1
    SenderT1.verbose = True
    print("Target Sender1: ", SenderT1.id)

    SenderT2 = clients.pop()
    SenderT2.label = 2
    SenderT2.verbose = True
    print("Target Sender2: ", SenderT2.id)

    recipient = clients.pop()
    recipient.verbose = True
    print("Target Recipient: ", recipient.id)

    net.mixnodes[0].verbose = True

    for c in clients:
        c.verbose = True
        env.process(c.start(random.choice(clients)))
        env.process(c.start_loop_cover_traffic())

    env.process(SenderT1.start(dest=recipient))
    env.process(SenderT1.start_loop_cover_traffic())
    env.process(SenderT2.start(dest=random.choice(clients)))
    env.process(SenderT2.start_loop_cover_traffic())
    env.process(recipient.set_start_logs())
    env.process(recipient.start(dest=random.choice(clients)))
    env.process(recipient.start_loop_cover_traffic())

    print("---------" + str(datetime.datetime.now()) + "---------")
    print("> Running the system for %s ticks to prepare it for measurement." % (conf["phases"]["burnin"]))

    env.process(check_progress(env, conf["phases"]["burnin"]))

    # env.process(progress_update(env, 5))
    time_started = env.now
    time_started_unix = datetime.datetime.now()
    # ------ RUNNING THE STARTUP PHASE ----------
    if conf["phases"]["burnin"] > 0.0:
        env.run(until=conf["phases"]["burnin"])
    print("> Finished the preparation")

    # Start logging since system in steady state
    for p in net.mixnodes:
        p.mixlogging = True

    env.process(SenderT1.simulate_real_traffic(recipient))
    real_time_started_measurements = round(time.time())
    tick_time_started_measurements = env.now
    print("> Started sending traffic for measurements (sim tick {})".format(tick_time_started_measurements))

    env.run(until=env.stop_sim_event)  # Run until the stop_sim_event is triggered.
    real_time_ended_measurements = round(time.time())
    total_real_time_measurements = real_time_ended_measurements - real_time_started_measurements
    tick_time_ended_measurements = env.now
    total_tick_time_measurements = tick_time_ended_measurements - tick_time_started_measurements
    print("> Total measurements time: {} minutes.".format(total_real_time_measurements/60))
    print("> Total measurements in ticks: {}.".format(total_tick_time_measurements))
    print("> Main part of simulation finished at tick {}. Starting cooldown phase.".format(tick_time_ended_measurements))
    end_cooldown_time = (conf["phases"]["cooldown"]/total_tick_time_measurements)*total_real_time_measurements

    # Log entropy
    loggers[2].info(StructuredMessage(metadata=tuple(env.entropy)))
    # ------ RUNNING THE COOLDOWN PHASE ----------
    env.process(check_progress(env, env.now + conf["phases"]["cooldown"]))
    env.run(until=env.now + conf["phases"]["cooldown"])

    # Log entropy
    loggers[2].info(StructuredMessage(metadata=tuple(env.entropy)))

    print("> Cooldown phase finished.")
    time_finished = env.now
    time_finished_unix = datetime.datetime.now()
    # print("Reciever received: ", recipient.num_received_packets)
    print("> End of Simulation at {}".format(datetime.datetime.now().strftime("%H:%M:%S")))
    print("> Total Simulation Time [in ticks]: " + str(time_finished-time_started) + "---------")
    print("> Total Simulation Time [in unix time]: " + str(time_finished_unix-time_started_unix) + "---------")

    flush_logs(loggers)


    global throughput
    throughput = float(env.total_messages_received) / float(time_finished-time_started)

    mixthroughputs = []
    for m in net.mixnodes:
        mixthroughputs.append(float(m.pkts_sent) / float(time_finished-time_started))

    print("Total number of packets which went through the network: ", float(env.total_messages_received))
    print("Network throughput %f / second: " % throughput)
    print("Average mix throughput %f / second, with std: %f" % (np.mean(mixthroughputs), np.std(mixthroughputs)))


def check_progress(env, max_tick):
    last_value = -1
    while env.now <= max_tick:
        if env.now != last_value:
            print("tick: {}/{} at {}".format(int(env.now), int(max_tick), datetime.datetime.now().strftime("%H:%M:%S")))
            last_value = env.now
            yield env.timeout(1)



def flush_logs(loggers):
    for l in loggers:
        for h in l.handlers:
            h.flush()


def run(exp_dir, conf_file=None, conf_dic=None):
    print("The experiment log directory is: %s" %exp_dir)

    # Upload config file
    if conf_file:
        print("The config file is at:%s" %conf_file)
        conf = experiments.Settings.load(conf_file)
    elif conf_dic:
        conf = conf_dic
    else:
        print("A configuration dictionary or file required")

    # -------- timing for how long to run the simulation ----------
    limittime = conf["phases"]["burnin"] + conf["phases"]["execution"] # time after which we should terminate the target senders from sending
    simtime = conf["phases"]["burnin"] +  conf["phases"]["execution"] + conf["phases"]["cooldown"] # time after which the whole simulator stops

    # Logging directory
    log_dir = os.path.join(exp_dir,conf["logging"]["dir"])
    # Setup environment
    env = setup_env(conf)

    # Create the network
    type = conf["network"]["topology"]
    loggers = get_loggers(log_dir, conf)
    net = Network(env, type, conf, loggers)

    if type == "p2p":
        run_p2p(env, conf, net, loggers)
    else:
        run_client_server(env, conf, net, loggers)
