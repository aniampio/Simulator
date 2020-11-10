import simpy
import random

class MixGuard(object):
    __slots__ = ['env', 'conf', 'net', 'logger', 'layer', 'id', 'resource_queue', 'queue', 'resource_queue', 'max_capacity']

    def __init__(self, env, conf, net, id=None, layer=None, logger=None):

        self.env = env
        self.conf = conf
        self.layer = layer
        self.net = net
        self.logger = logger
        self.id = id or random_string(self.conf["misc"]["id_len"])

        self.max_capacity = 100
        # Resource queue to model congestion
        self.resource_queue = simpy.PriorityResource(self.env, capacity=self.max_capacity)
        self.queue = []

    def start(self):
        print("> %s started" % self.id)
        yield self.env.timeout(0)

        self.env.process(self.flush_packets())


    def set_network(self, topology):
        ''' Function sets a given network topology.

            Keyword arguments:
            topology - a topology of the network.
        '''
        self.topology = topology

    def process_packet(self, packet):
        yield self.env.timeout(0)
        self.add_packet_to_queue(packet)


    def add_packet_to_queue(self, packet):
        ''' Adding packet to the internal queue.
            Check whether the queue is not too large.
        '''
        self.queue.append(packet)
        self.manage_queue()

    def flush_packets(self):
        ''' Continusly check whether there are any packets
            to send.
        '''
        while True:
            if len(self.queue) > 1:
                packet = self.queue.pop()
                self.env.process(self.handel_packet(packet))
                # yield self.env.timeout(1)
            else:
                yield self.env.timeout(1)

    def manage_queue(self):
        if len(self.queue) > self.max_capacity:
            self.queue = []

    def handel_packet(self, packet):
        with self.resource_queue.request() as req:
            yield req
            yield self.env.timeout(1)
            self.forward_packet(packet)


    def forward_packet(self, packet):
        self.env.process(self.net.forward_packet(packet))

    def __hash__(self):
        return self.id.__hash__()

    def __repr__(self):
        return self.id
