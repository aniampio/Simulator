import numpy
import simpy
import random
from classes.Utilities import random_string, StructuredMessage
from classes.Node import Node
import experiments.Settings
import math



class MixNode(Node):
    def __init__(self, env, conf, net=None, layer=None, logger=None, corrupt=False, id=None):

        super().__init__(env=env, net=net, loggers=logger, conf=conf, id=id)
        self.position = layer

        #Operation
        self.AQM = self.conf["mixnodes"]["AQM"]
        if self.conf["mixnodes"]["avg_delay"] == 0.0:
            self.avg_delay = 0.0
        else:
            self.avg_delay = float(self.conf["mixnodes"]["avg_delay"])


    def set_network(self, topology):
        ''' Function sets a given network topology.

            Keyword arguments:
            topology - a topology of the network.
        '''
        self.topology = topology


    def drop_random(self):
        '''Drops a packet from the pool at random, and returns it.'''

        pkt_id = random.choice(list(self.pool.keys()))
        self.pool[pkt_id].dropped = True
        pkt=self.pool.pop(pkt_id)
        return pkt


    def __hash__(self):
        return self.id.__hash__()

    def __repr__(self):
        return self.id
