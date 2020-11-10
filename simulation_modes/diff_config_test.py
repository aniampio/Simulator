import simpy
import os
import datetime


import experiments.Settings

from classes.Net import *
from classes.Client import *
from classes.Net import *
from classes.Utilities import *



def progress_update(env, interval=100):
    while True:
        yield env.timeout(interval)
        print("Current tick is: " + str(env.now))


def build_network(env, layers, mixnodes_per_layer, num_in, num_out):
	return Network(env, layers, mixnodes_per_layer, num_in, num_out)

def get_loggers(log_dir):
	packet_logger = setup_logger('simulation.packet', os.path.join(log_dir, 'packet_log.csv'))
	packet_logger.info(StructuredMessage(metadata=("Type", "CurrentTime", "ClientID", "PacketID", "PacketType", "MessageID", "PacketTimeSent", "PacketTimeDelivered", "TotalFragments", "PrOthers", "PrSenderA", "PrSenderB", "RealSenderLabel")))

	message_logger = setup_logger('simulation.messages', os.path.join(log_dir, 'message_log.csv'))
	message_logger.info(StructuredMessage(metadata=("Type", "CurrentTime", "ClientID", "MessageID", "NumPackets", "MsgTimeSent", "MsgTimeDelivered", "MsgTransitTime", "MsgSize", "MsgRealSender", "MsgLikelihoodRation")))

	loggers = (packet_logger, message_logger)
	return loggers



def run(log_dir, number_of_clients, ticks, layers, MixNodes_per_layer, num_in, num_out, num_runs, startup, cooldown, perc_corrupt, verbose):
    ''' Creates an experimental run of the simulator with the settings in the signature above or reading from a configuration file'''

    # ------ config, loggers and env ----------
    confx = experiments.Settings.conf
    loggers = get_loggers(log_dir)
    env = simpy.Environment()


    # ------- creating mix network -------------
    net = Network(env, layers, MixNodes_per_layer, num_in, num_out)
    for m in net.MixNodes:
        m.set_network(net.topology)
    # net.MixNodes[0].verbose = True

    # -------- timing for how long to run the simulation ----------
    limittime = startup + ticks # time after which we should terminate the target senders from sending
    simtime = startup +  ticks + cooldown # time after which the whole simulator stops

    # Creating so called "other" users, who will only send dummy traffic
    otherClients = []
    print("Number of clients started: ", number_of_clients)
    for s in range(number_of_clients - 3):
        sender = Client(env, net, net.topology, loggers = loggers, label=0)
        otherClients.append(sender)

    for o in otherClients:
        env.process(sender.start(random.choice(otherClients)))
        # env.process(Sender.start_ack_sending())
        # env.process(Sender.terminate(limittime))

    # Creating a target recipient recipient
    recipient = Client(env, net, net.topology, loggers = loggers, label=0)
    print("> Recipient: %s" % recipient.id)
    recipient.verbose = True

    env.process(recipient.set_start_logs())
    env.process(recipient.start(random.choice(otherClients)))

    SenderT1 = Client(env, net, net.topology, loggers = loggers, label = 1)
    SenderT1.rate_sending = 1.0
    print("Sender1 rate of sending: ", SenderT1.rate_sending)
    SenderT1.verbose = True
    print("Sender A: ", SenderT1.id)
    env.process(SenderT1.terminate(limittime))
    env.process(SenderT1.start(random.choice(otherClients)))

    SenderT2 = Client(env, net, net.topology, loggers = loggers, label = 2)
    SenderT2.rate_sending = 1.0
    print("Sender2 rate of sending: ", SenderT2.rate_sending)
    SenderT2.verbose = True
    print("Sender B: ", SenderT2.id)
    env.process(SenderT2.terminate(limittime))
    env.process(SenderT2.start(random.choice(otherClients)))

    # env.process(recipient.start_ack_sending())
    # env.process(recipient.terminate(limittime))

    print("Other clients rate of sending: ")
    for c in otherClients:
        print(c.rate_sending)

    print("---------" + str(datetime.datetime.now()) + "---------")
    print("Running the system for %s ticks to prepare it." % (startup))

    # ------ RUNNING THE STARTUP PHASE ----------
    if startup > 0.0:
        env.run(until=startup)

    time_started = datetime.datetime.now()
    print("---------" + str(time_started) + "---------")
    print("Now: " + str(env.now) + ", Simulation Duration: " + str(confx["phases"]["execution"]) + ", Running until: " + str(limittime) + ", Cooling-down until: " + str(simtime))
    # env.process(progress_update(env, 100))

    # ------ RUNNING THE MAIN SIMULATION PHASE ----------
    # --------- Only SenderT1 is sending REAL packets to the target recipient --------------
    env.process(SenderT1.gen_fake_traffic(recipient))
    print("Turned on generating real (synthetic) traffic")

    # env.process(SenderT1.start_ack_sending())
    # if confx["clients"]["retransmit"]:
    #     env.process(SenderT1.schedule_retransmits())

    # env.process(SenderT2.start_ack_sending())
    # if confx["clients"]["retransmit"]:
    #     env.process(SenderT2.schedule_retransmits())

    env.run(until=simtime)  
    print("Time for simulation ellapsed. Current time: ", env.now)
    time_finished = datetime.datetime.now()
    print("---------" + str(time_finished) + "---------")
    print("Total Simulation Time: " + str(time_finished-time_started) + "---------")
    print("Current time (to know when the simulation was used) ", datetime.datetime.now())
