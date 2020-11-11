import math
import random
import numpy
from classes.Node import Node
from classes.Client import Client
import experiments.Settings
import networkx as nx
import os


class Network(object):

    def __init__(self, env, type, conf, loggers):
        self.env = env
        self.conf = conf
        self.topology = {}
        self.type = type
        self.loggers = loggers

        self.clients = [Client(env, conf, self, loggers = loggers, label=0) for i in range(int(conf["clients"]["number"]))]

        if type == "p2p":
            self.peers = [Node(env, conf, self, id="Peer%s" % i, loggers = loggers) for i in range(int(conf["clients"]["number"]))]
            self.topology["Type"] = "p2p"
            self.init_p2p()
        else:
            if type == "cascade":
                self.topology["Type"] = "cascade"
                self.mixnodes = [Node(env, conf, self, id="M%s" % i, loggers = loggers) for i in range(self.conf["network"]["num_nodes"])]
                self.init_cascade()
            elif type == "stratified":
                self.topology["Type"] = "stratified"
                num_mixnodes = int(self.conf["network"]["layers"]) * int(self.conf["network"]["layer_size"])
                self.mixnodes = [Node(env, conf, self, id="M%s" % i, loggers = loggers) for i in range(num_mixnodes)]
                self.init_stratified()
            elif type == "multi_cascade":
                pass
            else:
                raise Exception("Didn't recognize the network type")

    def init_p2p(self):
        self.topology["peers"] = self.peers.copy()

    def init_cascade(self):
        self.topology["cascade"] = self.mixnodes.copy()

    def init_multi_cascade(self):
        pass

    def init_stratified(self):
        num_layers = int(self.conf["network"]["layers"])
        mixes_per_layer = int(self.conf["network"]["layer_size"])

        layers = [self.mixnodes[i * mixes_per_layer:(i + 1) * mixes_per_layer] for i in range(0, num_layers)]
        self.topology["Layers"] =  layers

        for i in range(0, num_layers - 1):
            for j in range(0, mixes_per_layer):
                self.topology[self.mixnodes[i * mixes_per_layer + j]] = layers[i + 1]

    def select_random_route(self, length=None):
        tmp_route = []

        if self.topology["Type"] == "stratified":
            tmp_route = [random.choice(L) for L in self.topology["Layers"]]
        elif self.topology["Type"] == "cascade":
            tmp_route = self.topology["cascade"].copy()
        elif self.topology["Type"] == "p2p":
            tmp_route = random.sample(self.peers, 3)

        for i, m in enumerate(tmp_route):
            m.position = i
        return tmp_route


    def forward_packet(self, packet):
        ''' Function responsible for forwarding the packet, i.e.,
            checking what is the next hop of the packet and triggering the
            process_packet function by a particular node.

            Keyword arguments:
            packet - the packet to be forwarded.
        '''
        # TODO: If needed, some network delay can be added.
        yield self.env.timeout(0)

        next_node = packet.route[packet.current_node + 1]
        packet.current_node += 1
        self.env.process(next_node.process_packet(packet))


    def __repr__(self):
        return "topology: " + str(self.topology)
