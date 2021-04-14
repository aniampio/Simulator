from simulation_modes import test_mode
import os
# from experiments import plotting
from metrics import anonymity_metrics, performance_metrics
from classes.Utilities import get_total_num_of_target_packets
import pandas as pd
import shutil
import json

if __name__ == "__main__":

    # try:

    print("Mix-network Simulator\n")
    print("Insert the following network parameters to test: ")

    with open('test_config.json') as json_file:
        config = json.load(json_file)

    if not os.path.exists('./playground_experiment/logs'):
        os.makedirs('./playground_experiment/logs')
    else:
        try:
            os.remove('./playground_experiment/logs/packet_log.csv')
            os.remove('./playground_experiment/logs/message_log.csv')
            os.remove('./playground_experiment/logs/last_mix_entropy.csv')
        except:
            pass

    test_mode.run(exp_dir='playground_experiment', conf_file=None, conf_dic=config)
    pps = test_mode.throughput

    packetLogsDir = './playground_experiment/logs/packet_log.csv'
    messageLogsDir = './playground_experiment/logs/message_log.csv'
    entropyLogsDir = './playground_experiment/logs/last_mix_entropy.csv'
    packetLogs = pd.read_csv(packetLogsDir, delimiter=';')
    messageLogs = pd.read_csv(messageLogsDir, delimiter=';')
    entropyLogs = pd.read_csv(entropyLogsDir, delimiter=';')

    unlinkability = anonymity_metrics.getUnlinkability(packetLogs)
    entropy = anonymity_metrics.getEntropy(entropyLogs, get_total_num_of_target_packets(config))

    throughput = performance_metrics.computeThroughput(messageLogs)
    #
    latency_per_packet = performance_metrics.computePacketE2ELatency(packetLogs)
    packet_queuing_time = performance_metrics.computePacketQueuingTime(packetLogs)
    #
    transit_latency_per_message = performance_metrics.computeMessageTransitLatency(messageLogs)
    sending_latency_per_message = performance_metrics.computeMessageE2ELatency(messageLogs)
    #
    message_queuing_time = performance_metrics.computeMessageQueuingTime(messageLogs)



    print("\n\n")
    print("-------------------------------------------------------")
    print("Simulation finished. Below, you can check your results.")
    print("-------------------------------------------------------")
    print("-------- Anonymity metrics --------")
    print(">>> Entropy: ", entropy)
    if unlinkability[0] == None:
        print(">>> E2E Unlinkability: epsilon= -, stdEps= -, delta=%f)" % unlinkability[1])
    else:
        print(">>> E2E Unlinkability: (epsilon=%f, stdEps=%f, delta=%f)" % unlinkability)

    print("\n\n")
    print("-------- Setup --------")
    print(">> Topology: ", config["network"]["topology"])
    print(">> Number of clients: ", config["clients"]["number"])
    print(">> Packet stream average delay: ", config["clients"]["packet_stream_average_delay"])
    print(">> Avg packet delay per hop: ", config["mixnodes"]["avg_delay"])
    cover_traffic = config["clients"]["cover_stream_average_delay"] if config["clients"]["cover_traffic"] == True else 'false'
    print(">> Cover traffic: ", cover_traffic)
    print(">> Packet size: ", config["packet"]["packet_size"])
    print(">> Message size: ", config["message"]["exact_msg_size"])

    print("\n\n")
    print("-------- Performance metrics --------")
    print(">> Average packet latency: {:.3f} [s]".format(latency_per_packet))
    print(">> Average packet queuing time: {:.3f} [s]".format(packet_queuing_time))
    print("----------------")
    print(">> Average message transit latency (from sending to delivery): {:.3f} [s]".format(transit_latency_per_message))
    print(">> Average message sending latency (from queuing to delivery): {:.3f} [s]".format(sending_latency_per_message))
    print(">> Average message queing time (from queue to send): {:.3f} [s]".format(message_queuing_time))
    print("----------------")
    print(">> Throughput [packets/time] of the network: {:.3f} [packets/s]".format(pps))
    print(">> Throughput [bytes/time] of the network: {:.3f} [kB/s]".format(throughput / 1000))
    print("-------------------------------------------------------")

# except Exception as e:
# print(e)
# print("Something went wrong! Check whether your input parameters are correct.")
