from classes.Utilities import random_string, StructuredMessage, get_exponential_delay
import math
import numpy as np
from classes.Packet import Packet
from classes.Message import Message

class Node(object):

    def __init__(self, env, conf, net=None, label=0, loggers=None, id=None):

        self.env = env
        self.conf = conf
        self.id = id or random_string(self.conf["misc"]["id_len"])
        self.net = net

        self.pkts_received = 0
        self.pkts_sent = 0


        self.avg_delay = 0.0 if self.conf["mixnodes"]["avg_delay"] == 0.0 else float(self.conf["mixnodes"]["avg_delay"])

        # State
        self.pool = {}
        self.inter_pkts = 0 #ctr which count how many new packets arrived since the last time a packet left
        self.probability_mass = None
        self.sender_estimates = None
        self.pool = {}
        self.max_pool_size = 0
        self.mixlogging = False

        self.loggers = loggers if loggers else None
        (self.packet_logger, self.message_logger, self.entropy_logger) = self.loggers
        #State
        self.alive = True

        self.rate_sending = 1.0/float(self.conf["clients"]["rate_sending"])
        self.rate_generating = float(self.conf["clients"]["sim_add_buffer"]) # this specifies how often we put a real message into a buffer

        self.verbose = False
        self.pkt_buffer_out = []
        self.pkt_buffer_out_not_ack = {}
        self.label = label
        self.send_dummy_ACK = self.conf["clients"]["dummies_acks"]
        self.send_ACK = self.conf["clients"]["ACK"]
        self.num_received_packets = 0
        self.msg_buffer_in = {}

    def start(self, dest):
        ''' Main client method; It sends packets out.
        It checks if there are any new packets in the outgoing queue.
        If it finds any, it sends the first of them.
        If none are found, the client may sent out a dummy
        packet (i.e., cover traffic) depending on the mixnet settings.
        '''

        delays = []

        while True:
            if self.alive:
                if delays == []:
                    delays = list(np.random.exponential(self.rate_sending, 10000))

                delay = delays.pop()
                yield self.env.timeout(float(delay))

                pkt_sent = False
                while len(self.pkt_buffer_out) > 0: #If there is a packet to be send
                    tmp_pkt = self.pkt_buffer_out.pop(0)
                    if not tmp_pkt.ACK_Received: #Check if it got ACK_Received in the meanwhile
                        self.send_packet(tmp_pkt)
                        self.env.total_messages_sent += 1
                        pkt_sent = True
                        break
                    else:
                        print("ACK_Received while waiting in the queue.")

                # Send dummy packet when the packet buffer is empty,(currently we don't send dummies during the cooldown phase)
                if pkt_sent == False and self.conf["clients"]["cover_traffic"]:
                    tmp_pkt = Packet.dummy(conf=self.conf, net=self.net, dest=dest, sender=self)  # sender_estimates[sender.label] = 1.0
                    tmp_pkt.time_queued = self.env.now
                    self.send_packet(tmp_pkt)
                    self.env.total_messages_sent += 1
            else:
                break


    def send_packet(self, packet):
        ''' Methods sends a packet into the network,
         adds it to the ack waiting-list,
         and logs information about the sending.
​
            Keyword arguments:
            packet - an object of class Packet which is sent into the network.
        '''

        packet.time_sent = self.env.now
        packet.current_node = -1  # If it's a retransmission this needs to be reset
        packet.times_transmitted += 1

        if packet.type == "REAL" or packet.type == "DUMMY":
            self.pkt_buffer_out_not_ack[packet.id] = packet #Add to ack waiting list
            if packet.type == "REAL" and packet.message.time_sent is None:
                packet.message.time_sent = packet.time_sent

        self.env.process(self.net.forward_packet(packet))


    def process_packet(self, packet):
        ''' Function performs processing of the given packet and logs information
            about it and forwards it to the next destionation.
            While processing the packet, the function also calculates the probability
            that the given packet has a specific sender label.

            Keyword arguments:
            packet - the packet which should be processed.
        '''

        if self.id == packet.dest.id:
            self.env.process(self.process_received_packet(packet))
        else:
            self.pkts_received += 1
            self.add_pkt_in_pool(packet)

            delay = get_exponential_delay(self.avg_delay) if self.avg_delay != 0.0 else 0.0
            wait = delay + 0.00036 # add the time of processing the Sphinx packet.
            yield self.env.timeout(wait)

            if not packet.dropped: # It may get dropped if pool gets full, while waiting
                self.forward_packet(packet)
            else:
                pass


    def process_received_packet(self, packet):
        ''' 1. Processes the received packets and logs informatiomn about them.
            2. If enabled, it sends an ACK packet to the sender.
            3. Checks whether all the packets of particular message were received and logs the information about the reconstructed message.
            Keyword arguments:
            packet - the received packet.
        '''

        packet.time_delivered = self.env.now
        self.env.total_messages_received += 1

        if packet.type == "REAL":
            # print("> Real message")
            if self.send_ACK:
                ack_pkt = Packet.ack(conf=self.conf, net=self.net, dest=packet.real_sender, sender=self, packet_id=packet.id, msg_id=packet.msg_id)
                self.add_to_ack_buffer(ack_pkt)

            self.num_received_packets += 1
            msg = packet.message
            if not msg.complete_receiving:
                # print("> Message not complete, but packet added")
                msg.register_received_pkt(packet)
                self.msg_buffer_in[msg.id] = msg
                if self.conf["logging"]["enabled"] and self.packet_logger is not None and self.start_logs:
                    self.packet_logger.info(StructuredMessage(metadata=("RCV_PKT_REAL", self.env.now, self.id, packet.id, packet.type, packet.msg_id, packet.time_queued, packet.time_sent, packet.time_delivered, packet.fragments, packet.sender_estimates[0], packet.sender_estimates[1], packet.sender_estimates[2], packet.real_sender.label, packet.route, packet.pool_logs)))
            if msg.complete_receiving:
                # print("> Message completed")
                msg_transit_time = (msg.time_delivered - msg.time_sent)
                if self.conf["logging"]["enabled"] and self.message_logger is not None and self.start_logs:
                    self.message_logger.info(StructuredMessage(metadata=("RCV_MSG", self.env.now, self.id, msg.id, len(msg.pkts), msg.time_queued, msg.time_sent, msg.time_delivered, msg_transit_time, len(msg.payload), msg.real_sender.label)))
                self.env.message_ctr -= 1

                # this part is used to stop the simulator at a time when all sent packets got delivered!
                if self.env.finished == True and self.env.message_ctr <= 0:
                  print('> The stop simulation condition happend')
                  self.env.stop_sim_event.succeed()

        elif packet.type == "ACK": #remove packet from ack waiting list
            try:
                if self.conf["logging"]["enabled"] and self.packet_logger is not None and self.start_logs:
                    self.packet_logger.info(StructuredMessage(metadata=("RCV_PKT_ACK", self.env.now, self.id, packet.id, packet.type, packet.msg_id, packet.time_sent, packet.time_delivered, packet.fragments, packet.sender_estimates[0], packet.sender_estimates[1], packet.sender_estimates[2], packet.real_sender.label, packet.route, packet.pool_logs)))
                self.update_RTT(packet)
                self.pkt_buffer_out_not_ack[packet.id].ACK_Received = True
                del self.pkt_buffer_out_not_ack[packet.id]
            except Exception as e:
                pass
        elif packet.type == "DUMMY":
            if self.send_dummy_ACK:
                ack_pkt = Packet.ack(conf=self.conf, net=self.net, dest=packet.real_sender, sender=self, packet_id=packet.id, msg_id=packet.msg_id)
                self.add_to_ack_buffer(ack_pkt)
        elif packet.type == "DUMMY_ACK":
            pass

        return
        yield  # self.env.timeout(0.0)

    def forward_packet(self, packet):
        if not self.probability_mass is None:
            packet.probability_mass = self.probability_mass.copy()
        if not self.sender_estimates is None:
            packet.sender_estimates = self.sender_estimates.copy()

        #If it has been dropped in the meantime, we just skip sending it.
        try:
            self.pool.pop(packet.id)
        except Exception as e:
            pass

        # If the pool dries out, then we start measurments from scratch
        if len(self.pool) == 0:
            self.sender_estimates = None
            self.probability_mass = None
            self.max_pool_size = 0
        self.pkts_sent += 1

        # If this is the last mixnode, update the entropy taking into account probabilities
        # of packets leaving the network
        if self.id == packet.route[-2].id and self.mixlogging:
            self.update_entropy(packet)

        self.env.process(self.net.forward_packet(packet))

    def update_entropy(self, packet):
        for i, pr in enumerate(packet.probability_mass):
            if pr != 0.0:
                self.env.entropy[i] += -(float(pr) * math.log(float(pr), 2))

    def add_pkt_in_pool(self, packet):
        ''' Method adds incoming packet in mixnode pool and updates the vector
            of estimated probabilities, taking into account the new state of the pool.

            Keyword arguments:
            packet - the packet for which we update the probabilities vector
        '''
        self.inter_pkts += 1
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

    def set_start_logs(self, time=0.0):
        yield self.env.timeout(time)
        self.start_logs = True
        if self.verbose:
            print("> The startup phase done. Logs are now on for Client %s." % self.id)

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
