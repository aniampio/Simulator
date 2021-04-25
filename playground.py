from simulation_modes import test_mode
import os
# from experiments import plotting
from metrics import anonymity_metrics, performance_metrics
from classes.Utilities import get_total_num_of_target_packets
import pandas as pd
import shutil
import json
import pickle
from datetime import datetime
import argparse

def runSimulation(edir=None, rseed=None):
    if edir:
        experiment_dir = edir
    else:
        experiment_dir = './playground_experiment/'

    print("Mix-network Simulator\n")
    # print("Insert the following network parameters to test: ")

    with open('test_config.json') as json_file:
        config = json.load(json_file)

    if not os.path.exists(os.path.join(experiment_dir, 'logs')):
        os.makedirs(os.path.join(experiment_dir, 'logs'))
    else:
        try:
            os.remove(os.path.join(experiment_dir, 'logs/packet_log.csv'))
            os.remove(os.path.join(experiment_dir, 'logs/message_log.csv'))
            os.remove(os.path.join(experiment_dir, 'logs/last_mix_entropy.csv'))
        except:
            pass

    test_mode.run(exp_dir=experiment_dir, conf_file=None, conf_dic=config, rseed=rseed)
    pps = test_mode.throughput

    packetLogsDir = os.path.join(experiment_dir, 'logs/packet_log.csv')
    messageLogsDir = os.path.join(experiment_dir, 'logs/message_log.csv')
    entropyLogsDir = os.path.join(experiment_dir, 'logs/last_mix_entropy.csv')
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

    # exp_timestamp = datetime.now()
    # total_results = [{'Experiment Time':exp_timestamp.strftime("%d/%m/%Y %H:%M:%S") ,
    #     'Experimental Setup':config,
    #     'Experiment results': {
    #         'unlinkability' : unlinkability,
    #         'entropy' : entropy,
    #         'throughput':throughput,
    #         'latency_per_packet':latency_per_packet,
    #         'packet_queuing_time':packet_queuing_time,
    #         'transit_latency_per_message':transit_latency_per_message,
    #         'sending_latency_per_message':sending_latency_per_message,
    #         'message_queuing_time':message_queuing_time}
    #     }]
    #
    # if os.path.exists("./total_results.pkl"):
    #     l = pickle.load(open("total_results.pkl", "rb"))
    #     l.append(total_results)
    #     pickle.dump(l, open('total_results.pkl', 'wb'))
    # else:
    #     pickle.dump(total_results, open('total_results.pkl', 'wb'))
    return


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-edir", help="The directory of the experiment output")
    args = parser.parse_args()
    runSimulation(args.edir)

# except Exception as e:
# print(e)
# print("Something went wrong! Check whether your input parameters are correct.")
