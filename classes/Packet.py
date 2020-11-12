from classes.Utilities import random_string
import numpy

class Packet():
    ''' This module implements the Packet object, which is the data structure responsible for
        transporting message blocks among clients.
    '''

    __slots__ = ['conf', 'id', 'route', 'payload', 'real_sender', 'dest', 'msg_id', 'message', 'fragments', 'type', 'pool_logs', 'dropped', 'current_node', 'times_transmitted',
                'ACK_Received', 'time_queued', 'time_sent', 'time_delivered', 'sender_estimates', 'probability_mass']

    def __init__(self, conf, route, payload, sender, dest, type, packet_id = None, msg_id="DUMMY", order=1, num=1, message=None):
        self.conf = conf
        self.id = packet_id or random_string(32)

        self.route = route
        self.payload = payload
        self.real_sender = sender
        self.dest = dest

        self.msg_id = msg_id
        self.message = message

        self.fragments = num

        self.type = type
        self.pool_logs = []

        # State
        self.dropped = False
        self.current_node = -1
        self.times_transmitted = 0
        self.ACK_Received = False
        self.time_queued = None
        self.time_sent = None
        self.time_delivered = None

        # Measurements
        self.sender_estimates = numpy.array([0.0, 0.0, 0.0]) #Other, A, B
        self.sender_estimates[self.real_sender.label] = 1.0
        self.probability_mass = numpy.zeros(self.conf["misc"]["num_target_packets"])

        if self.type=="REAL":
            self.message.reconstruct.add(self.id)


    @classmethod
    def new(cls, conf, net, dest, payload, sender, type, num, msg_id):
        '''Method used for constructing a new Packet where
        the content is defined by the client but the route is generated on the constructor.'''

        rand_route = net.select_random_route()
        rand_route = rand_route + [dest]
        return cls(conf=conf, route=rand_route, payload=payload, sender=sender, dest=dest, type=type, num=num, msg_id=msg_id)


    @classmethod
    def ack(cls, conf, net, dest, sender, packet_id, msg_id):
        '''  The class method used for creating an ack Packet. '''

        payload = random_string(conf["packet"]["packet_size"])
        rand_route = net.select_random_route()
        rand_route = rand_route + [dest]
        return cls(conf=conf, route=rand_route, payload=payload, sender=sender, dest=dest, packet_id=packet_id, msg_id=msg_id, type="ACK")

    @classmethod
    def dummy(cls, conf, net, dest, sender):
        '''  The class method used for creating a dummy Packet. '''

        payload = random_string(conf["packet"]["packet_size"])
        rand_route = net.select_random_route()
        rand_route = rand_route + [dest]
        return cls(conf=conf, route=rand_route, payload=payload, sender=sender, dest=dest, type="DUMMY", msg_id="-")

    @classmethod
    def dummy_ack(cls, conf, net, dest, sender):

        payload = random_string(conf["packet"]["ack_packet_size"])
        rand_route = net.select_random_route()
        rand_route = rand_route + [dest]
        return cls(conf=conf, route=rand_route, payload=payload, sender=sender, dest=dest, type="DUMMY_ACK", msg_id="DUMMY_ACK")


    def output(self):
        ''' Function prints the information about the packet'''

        if not self.conf["debug"]["enabled"]:
            return

        print("=====================")
        print("Packet ID              : " + str(self.id))
        print("Packet Type            : " + str(self.type))
        print("Sender                 : " + str(self.real_sender))
        print("Labels                 : " + str(self.sender_estimates))
        print("Time Added to Queue    : " + str(self.time_queued))
        print("Time Sent              : " + str(self.time_sent))
        print("Time Delivered         : " + str(self.time_delivered))
        print("ACK Received           : " + str(self.ACK_Received))
        print("Route                  : " + str(self.route))
        print("Current Hop            : " + str(self.current_node))
        print("Times Transmitted      : " + str(self.times_transmitted))
        print("=====================")
