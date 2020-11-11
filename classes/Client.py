import numpy as np
import copy
import sys
import random

from classes.Packet import Packet
from classes.Message import Message
from classes.Node import Node
from classes.Utilities import StructuredMessage, setup_logger, random_string
import experiments.Settings

class Client(Node):
    def __init__(self, env, conf, net, loggers=None, label=0, id=None, p2p=False):
        self.conf = conf
        super().__init__(env=env, conf=conf, net=net, loggers=loggers, id=id)


        self.rate_ack = 1.0/float(self.conf["clients"]["rate_ack"])
        # This field is used to notify whether we can start logging. It should be set
        # to true when the system in a stady state
        self.start_logs = False
        #Monitoring
        self.RTTs = np.array([])
        self.verbose = False
        self.num_received_packets = 0


    def start_ack_sending(self):
        ''' start_ack_sending manages the buffer of ACKs scheduled for sending.
            If an ack is waiting in a buffer, it is popped and sent. Otherwise,
            a DUMMY_ACK is sent. DUMMY_ACK is sent to a random destination.
        '''

        delays = []

        while True:
            if delays == []:
                delays = list(np.random.exponential(self.rate_ack, 10000))

            delay_ack = delays.pop()
            yield self.env.timeout(delay_ack)

            if len(self.ack_buffer_out) > 0:
                ack_pkt = self.ack_buffer_out.pop(0)
                self.send_packet(ack_pkt)
            else:
                fake_recipient = Client(self.env, self.net, loggers = (self.packet_logger, self.message_logger) ,label=0)
                dummy_ack = Packet.dummy_ack(conf=self.conf, topology=self.net.topology, dest=fake_recipient, sender=self)
                self.send_packet(dummy_ack)



    def schedule_retransmits(self):
        pass


    def schedule_message(self, message):
        #  This function is used in the transcript mode
        ''' schedule_message adds given message into the outgoing client's buffer. Before adding the message
            to the buffer the function records the time at which the message was queued.'''

        print("> Scheduled message")
        current_time = self.env.now
        message.time_queued = current_time
        for pkt in message.pkts:
            pkt.time_queued = current_time
        self.add_to_buffer(message.pkts)


    def simulate_real_traffic(self, dest):
        #  This function is used in the test mode
        ''' This method generates messages simulating those of normal communication (email).
            It first, generates a random message, splits it into packets and then adds all
            the packets of the message to the outgoing buffer.
​
            Keyword arguments:
            dest - the destination of the message.
        '''
        i = 0

        # this while True should be changed to a some while i < X if we want to use the event as the condition to stop simulation
        while i < self.conf["misc"]["num_target_packets"]:
            yield self.env.timeout(float(self.rate_generating))

            msg = Message.random(conf=self.conf, net=self.net, sender=self, dest=dest)  # New Message
            current_time = self.env.now
            msg.time_queued = current_time  # The time when the message was created and placed into the queue
            for pkt in msg.pkts:
                pkt.time_queued = current_time
                pkt.probability_mass[i] = 1.0
            self.add_to_buffer(msg.pkts)
            i += 1
            self.env.message_ctr += 1
        self.env.finished = True


    def terminate(self, delay=0.0):
        ''' Function changes user's alive status to False after a particular delay
            Keyword argument:
            delayd (float) - time after the alice status should be switched to False.
        '''
        yield self.env.timeout(delay)
        self.alive = False
        print("Client %s terminated at time %s ." % (self.id, self.env.now))


    def add_to_buffer(self, packets):
        for pkt in packets:
            tmp_now = self.env.now
            pkt.time_queued = tmp_now
            self.pkt_buffer_out.append(pkt)

    def add_to_ack_buffer(self, ack_packet):
        self.ack_buffer_out.append(ack_packet)

    def print_msgs(self):
        ''' Method prints all the messages gathered in the buffer of incoming messages.'''
        for msg in self.msg_buffer_in:
            msg.output()

    def __repr__(self):
        return self.id
