import numpy
import simpy
import random
from classes.Utilities import random_string, StructuredMessage
import experiments.Settings
import math


def get_exponential_delay(avg_delay, cache=[]):
    if cache == []:
        cache.extend(list(numpy.random.exponential(avg_delay, 10000)))

    return cache.pop()


class MixNode(object):
    def __init__(self, env, conf, net=None, layer=None, logger=None, corrupt=False, id=None):
        # global conf
        # conf = experiments.Settings.conf  # Any better way?

        self.conf = conf
        self.env = env
        # self.cpu = simpy.Resource(env, capacity=1)
        self.id = id or random_string(self.conf["misc"]["id_len"])
        self.net = net
        self.verbose = self.conf["debug"]["mixnodes_verbose"]
        self.position = layer

        #Operation
        self.corrupt = corrupt
        self.pool_limit = self.conf["mixnodes"]["max_queue_size"]
        self.AQM = self.conf["mixnodes"]["AQM"]
        if self.conf["mixnodes"]["avg_delay"] == 0.0:
            self.avg_delay = 0.0
        else:
            self.avg_delay = float(self.conf["mixnodes"]["avg_delay"])

        # State
        self.pool = {}
        # the internal vector of probabilities calculated by the mix node (i.e., colour of the mix)
        self.sender_estimates = None
        self.probability_mass = None
        self.max_pool_size = 0

        self.logger = logger if logger else None
        self.mixlogging = False
        self.pkts_received = 0
        self.pkts_sent = 0

        self.l = 0
        self.k = 0 #ctr which count how many new packets arrived since the last time a packet left

    def set_network(self, topology):
        ''' Function sets a given network topology.

            Keyword arguments:
            topology - a topology of the network.
        '''
        self.topology = topology

    def process_packet(self, packet):
        ''' Function performs processing of the given packet and logs information
            about it and forwards it to the next destionation.
            While processing the packet, the function also calculates the probability
            that the given packet has a specific sender label.

            Keyword arguments:
            packet - the packet which should be processed.
        '''

        self.pkts_received += 1
        self.add_pkt_in_pool(packet)


        if self.AQM and (len(self.pool) >= self.pool_limit):
            drpd_pkt = self.drop_random()
        else:
            pass

        if self.avg_delay != 0.0:
            delay = get_exponential_delay(self.avg_delay) # Include a per-packet delay
        else:
            delay = 0.0

        wait = delay + 0.00036 # add the time of processing the Sphinx packet
        yield self.env.timeout(wait)

        if not packet.dropped: # It may get dropped if pool gets full, while waiting
            self.forward_packet(packet)
        else:
            pass


    def drop_random(self):
        '''Drops a packet from the pool at random, and returns it.'''

        pkt_id = random.choice(list(self.pool.keys()))
        self.pool[pkt_id].dropped = True
        pkt=self.pool.pop(pkt_id)
        return pkt


    def add_pkt_in_pool(self, packet):
        ''' Method adds incoming packet in mixnode pool and updates the vector
            of estimated probabilities, taking into account the new state of the pool.

            Keyword arguments:
            packet - the packet for which we update the probabilities vector
        '''

        self.k += 1
        if self.probability_mass is None and self.sender_estimates is None:
            self.pool[packet.id] = packet  # Add Packet in Pool
            self.probability_mass = packet.probability_mass.copy()
            self.sender_estimates = packet.sender_estimates.copy()
        else:
            dist_pm = self.probability_mass * len(self.pool) + packet.probability_mass
            dist_se = self.sender_estimates * len(self.pool) + packet.sender_estimates

            self.pool[packet.id] = packet  # Add Packet in Pool

            dist_pm = dist_pm / float(len(self.pool))
            dist_se = dist_se / float(len(self.pool))

            self.probability_mass = dist_pm.copy()
            self.sender_estimates = dist_se.copy()
        self.max_pool_size += 1


    def update_entropy(self, packet):
        for i, pr in enumerate(packet.probability_mass):
            if pr != 0.0:
                self.env.entropy[i] += -(float(pr) * math.log(float(pr), 2))


    def forward_packet(self, packet):
        if not self.probability_mass is None:
            packet.probability_mass = self.probability_mass.copy()
        if not self.sender_estimates is None:
            packet.sender_estimates = self.sender_estimates.copy()

        #If it has been dropped in the meantime, we just skip sending it.
        # This is a sync problem. I'll avoid using semaphores, it seems we
        #can live without perfect queue handling.
        try:
            self.pool.pop(packet.id)
        except Exception as e:
            pass


        packet.pool_logs.append((len(self.pool), self.max_pool_size))
        # If the pool dries out, then we start from scratch
        if len(self.pool) == 0:
            self.sender_estimates = None
            self.probability_mass = None
            self.max_pool_size = 0
            # if self.verbose:
            #     print("Warning: Pool empty at " + str(self.id) + "!")
        self.pkts_sent += 1

        # If this is the last mixnode, update the entropy taking into account probabilities
        # of packets leaving the network
        if self.position == self.conf["network"]["layers"] - 1 and self.mixlogging:
            self.update_entropy(packet)


        self.env.process(self.net.forward_packet(packet))


    def __hash__(self):
        return self.id.__hash__()

    def __repr__(self):
        return self.id
