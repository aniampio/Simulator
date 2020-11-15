from classes.Utilities import random_string
import random
from classes.Packet import Packet
import math

class Message():
    ''' This class defines an object of a Message, which is a message send between
    the sender and recipient. '''

    __slots__ = ['conf', 'id', 'payload', 'real_sender', 'time_queued', 'time_sent', 'time_delivered', 'transit_time', 'reconstruct', 'complete_receiving', 'pkts']
    def __init__(self, conf, net, payload, dest, real_sender, id=None):

        self.conf = conf

        self.id = id or random_string(self.conf["misc"]["id_len"])
        self.payload = payload
        self.real_sender = real_sender

        self.time_queued = None  # The first packet to be added in the queue (sender updates this)
        self.time_sent = None  # The first packet to leave the client (sender updates this)
        self.time_delivered = None  # The last packet to arrive (The recipient of msg will fill this in)
        self.transit_time = None
        self.reconstruct = set()  # The IDs we need to reconstruct.

        # State on reception
        self.complete_receiving = False
        # Packets
        self.pkts = self.split_into_packets(net, dest)


    @classmethod
    def random(cls, conf, net, sender, dest):
        ''' This class method creates a random message, with random payload. '''

        size = random.randint(conf["message"]["min_msg_size"], conf["message"]["max_msg_size"])
        payload = random_string(size)

        m = cls(conf=conf, net=net, payload=payload, real_sender=sender, dest=dest)
        return m


    def split_into_packets(self, net, dest):
        ''' Function splits the payload of the message into the fixed size blocks
            and encodes them into the objects of class Packet.

            Keyword arguments:
            topology - the network topology,
            dest - the destination of the message.
        '''

        pkts = []

        pkt_size = float(self.conf["packet"]["packet_size"])

        # to be able to have atomic messages, we keep this if condition
        if pkt_size == 0:
            fragments = [self.payload]
            num_fragments = 1
        else:
            num_fragments = int(math.ceil(float(len(self.payload))/pkt_size))
            fragments = [self.payload[i:i + int(self.conf["packet"]["packet_size"])] for i in range(0, len(self.payload), int(self.conf["packet"]["packet_size"]))]

        for i, f in enumerate(fragments):
            rand_route = net.select_random_route()
            rand_route = rand_route + [dest]
            tmp_pkt = Packet(conf=self.conf, route=rand_route, payload=f, sender=self.real_sender, dest=dest, msg_id=self.id, type="REAL", order=i+1, num=num_fragments, message=self)
            pkts.append(tmp_pkt)
            self.reconstruct.add(tmp_pkt.id)

        return pkts

    def register_received_pkt(self, new_pkt):
        ''' Function registers the information about the received packets
            by removing the packet id from the set of expected packets. Additionaly,
            the function triggers updates the completeness of the message,
            i.e., the flag pointing whether all the expected packets were received
            and the times, i.e., the information when the last packet was received.

            Keyword arguments:
            new_pkt - the new packet to be registered.
        '''
        if self.complete_receiving: #Same packet may have been retransmitted.
            return
        elif new_pkt.msg_id == self.id and new_pkt.id in self.reconstruct:
            self.reconstruct.remove(new_pkt.id)
            self.update_times(new_pkt)
            self.update_completeness()

    def update_times(self, pkt):
        ''' Function updates the time_delivered of the message with the time of the
            recently received packet.

            Keyword arguments:
            pkt - the received packet.
        '''
        if self.time_delivered is None or pkt.time_delivered > self.time_delivered:
            self.time_delivered = pkt.time_delivered

    def update_completeness(self):
        ''' Function checks whether all the expected packets of the message
            were received and if the message can be reconstructed. If yes,
            the status of the message completeness is set to True.
        '''
        self.complete_receiving = (len(self.reconstruct) == 0)


    def output(self):
        ''' Prints all the information about the message ans its packets'''

        if not self.conf["debug"]["enabled"]:
            return

        self.transit_time = self.time_delivered - self.time_sent

        print("=====================")
        print("Message ID              : " + str(self.id))
        print("Real Sender             : " + str(self.pkts[0].real_sender))
        print("All fragments collected?: " + str(self.complete_receiving))
        print("Original Fragments      : " + str(len(self.pkts)))
        print("Fragments sent          : " + str(self.pkts[0].fragments))
        print("Fragments missing       : " + str(len(self.reconstruct)))
        print("Time queued             : " + str(self.time_queued))
        print("Time sent               : " + str(self.time_sent))
        print("Time delivered          : " + str(self.time_delivered))
        print("Transit duration        : " + str(self.transit_time))

        # Reconstruct Payload
        tmp_payload = ""
        for i in range(self.pkts[0].fragments):
            for tmp_pkt in self.pkts:
                if tmp_pkt.order == (i-1):
                    tmp_payload += tmp_pkt.payload

        print("Payload : " + str(tmp_payload))

        for packet in self.pkts:
           packet.output()
        print("=====================")
