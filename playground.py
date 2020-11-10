from simulation_modes import test_mode
import os
# from experiments import plotting
from metrics import anonymity_metrics
import pandas as pd
import shutil


if __name__ == "__main__":

	# try:

	print("Mix-network Simulator\n")
	print("Insert the following network parameters to test: ")
	number_clients = int(input("Number of clients (at least 4): "))
	rate_sending = float(input("Average number of packets sent per second per single user (as float value > 0): "))
	number_layers = int(input("Number of mix network layers (at least 1): "))
	number_mixnodes = int(input("Number of mixes per layer (at least 1)	: "))
	avg_delay = float(input("Average delay in seconds per single mix (expressed as float > 0): "))

	config = {}
	config["experiment_id"] = 'Playground'
	config["runs"] = 1
	config["debug"] = {"enabled": True, "mixnodes_verbose": False, "net_verbose": True}
	config["logging"] = {"enabled": True, "dir": "logs", "client_log": "client_log.json", "mix_log": "mix_log.json"}
	config["phases"] = {"burnin": 100, "execution": 100, "cooldown": 100}
	config["network"] = {"packet_size": 0, "layers": int(number_layers), "layer_size": int(number_mixnodes), "prov_in": 0, "prov_out": 0, "ack_packet_size": 5}
	config["mixnodes"] = {"avg_delay": float(avg_delay), "perc_corrupt": 0.0, "AQM":False, "max_queue_size":5000}
	config["clients"] = {"number": int(number_clients), "min_msg_size": 2, "max_msg_size": 2, "rate_sending": float(rate_sending), "sim_add_buffer": 0.5, "rate_ack": 0.5, "rolling_mean_depth":10, "cover_traffic":True, "ACK":False, "retransmit":False, "dummies_acks":False, "max_retransmissions":5}
	config["misc"] = {"id_len": 32, "num_target_packets": 100}

	if not os.path.exists('./playground_experiment/logs'):
		os.makedirs('./playground_experiment/logs')
	else:
		os.remove('./playground_experiment/logs/packet_log.csv')
		os.remove('./playground_experiment/logs/last_mix_entropy.csv')

	test_mode.run(exp_dir='playground_experiment', conf_file=None, conf_dic=config)
	throughput = test_mode.throughput

	packetLogsDir = './playground_experiment/logs/packet_log.csv'
	entropyLogsDir = './playground_experiment/logs/last_mix_entropy.csv'
	packetLogs = pd.read_csv(packetLogsDir, delimiter=';')
	entropyLogs = pd.read_csv(entropyLogsDir, delimiter=';')

	unlinkability = anonymity_metrics.getUnlinkability(packetLogs)
	entropy = anonymity_metrics.getEntropy(entropyLogs)
	latency = anonymity_metrics.computeE2ELatency(packetLogs)

	print("\n\n")
	print("Simulation finished. Below, you can check your results.")
	print("-------------------------------------------------------")
	print("-------- Anonymity metrics --------")
	print(">>> Entropy: ", entropy)
	if unlinkability[0] == None:
		print(">>> E2E Unlinkability: epsilon= -, delta=%f)" % unlinkability[1])
	else:
		print(">>> E2E Unlinkability: (epsilon=%f, delta=%f)" % unlinkability)
	print("\n\n")
	print("-------- Performance metrics --------")
	print(">> Overall latency: %f seconds, of which sphinx cryptographic operations took on average: %f seconds" % (latency + number_layers * 0.00036, number_layers * 0.00036))
	print(">> Throuhput of the network: %f [packets / second]" % throughput)
	print("-------------------------------------------------------")

	# except Exception as e:
		# print(e)
		# print("Something went wrong! Check whether your input parameters are correct.")
