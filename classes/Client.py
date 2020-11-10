import numpy as np
import copy
import sys
import random

from classes.Packet import Packet
from classes.Message import Message
from classes.Utilities import StructuredMessage, setup_logger, random_string
import experiments.Settings

class Client(object):
    def __init__(self, env, conf, net, loggers=None, label=0, id=None, p2p=False):
        self.conf = conf
        self.p2p = p2p

        #Buffers
        self.msg_buffer_in = {}
        self.pkt_buffer_out = []
        self.ack_buffer_out = []
        self.pkt_buffer_out_not_ack = {}
        self.env = env

        self.rate_sending = 1.0/float(self.conf["clients"]["rate_sending"])
        self.rate_generating = float(self.conf["clients"]["sim_add_buffer"]) # this specifies how often we put a real message into a buffer
        self.rate_ack = 1.0/float(self.conf["clients"]["rate_ack"])

        self.net = net

        self.label = label
        self.id = id or 'C' + random_string(self.conf["misc"]["id_len"])
        self.send_ACK = self.conf["clients"]["ACK"]
        self.send_dummy_ACK = self.conf["clients"]["dummies_acks"]
        self.max_retransmissions = self.conf["clients"]["max_retransmissions"]
        #State
        self.alive = True
        # This field is used to notify whether we can start logging. It should be set
        # to true when the system in a stady state
        self.start_logs = False
        #Monitoring
        self.RTT_estimate = 5
        self.rolling_mean_depth = self.conf["clients"]["rolling_mean_depth"]
        self.RTTs = np.array([])
        # (self.packet_logger, self.message_logger) = None, None
        # if loggers is not None:
        (self.packet_logger, self.message_logger) = loggers if loggers else (None, None)
        self.verbose = False
        self.num_received_packets = 0


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

        # if packet.type == "DUMMY":
        #     self.pkt_buffer_out_not_ack[packet.id] = packet #Add to ack waiting list

        # if self.verbose:
        #   print(">> Send message: %s, %s at %s" % (packet.msg_id, packet.type, self.env.now))
        self.env.process(self.net.forward_packet(packet))


    def update_RTT(self, packet):
        '''Update estimated RTT time for packets based on incoming ACKS.
        Uses rolling mean.'''
        if packet.type=="ACK":
            time_pkt_sent = self.pkt_buffer_out_not_ack[packet.id].time_sent
            time_ack_received = packet.time_delivered
            tmp_RTT =time_ack_received - time_pkt_sent
            self.RTTs = np.append(self.RTTs,tmp_RTT)

            #Rolling mean
            c = 1.5
            self.RTT_estimate = c * np.mean(self.RTTs[(len(self.RTTs)-self.rolling_mean_depth):])
            #print(self.RTTs[(len(self.RTTs)-self.rolling_mean_depth):])
            #print("RTT estimate: ", self.RTT_estimate)


    def schedule_retransmits(self):
        while self.alive:
            yield self.env.timeout(1) # this time influences the retransmission. We have to pick a value which allows as to wait for the acks long enough.
            #threshold = self.estimate_RTT() #Estimate the RTT with the current network conditions (is it correct? Some pkts may've been sent earlier...)
            stale_pkts = self.pop_stale_non_acked(self.RTT_estimate) #Grab all packets that need to be retransmitte
            retransmit_pkts = [pkt for pkt in stale_pkts if (pkt.times_transmitted < self.max_retransmissions)] #Remove pkts that have exceeded the retransmission limit.
            if len(stale_pkts) != len(retransmit_pkts):
                print("Retransmission limit reached: Client %s dropped %d packets. Number left %d" %(self.id, len(stale_pkts)-len(retransmit_pkts), len(retransmit_pkts)))
            self.add_to_buffer(retransmit_pkts)


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


    # Reconstructs messages as packets come
    def process_packet(self, packet):
        ''' 1. Processes the received packets and logs informatiomn about them.
            2. If enabled, it sends an ACK packet to the sender.
            3. Checks whether all the packets of particular message were received and logs the information about the reconstructed message.
            Keyword arguments:
            packet - the received packet.
        '''

        # print("> Received packet")
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

    def pop_stale_non_acked(self, expected_RTT):
        now = self.env.now
        stale_pkts = []
        tmp_dict = self.pkt_buffer_out_not_ack.copy()
        for id in tmp_dict:
            tmp_pkt = copy.copy(self.pkt_buffer_out_not_ack[id])
            if (expected_RTT < (now-tmp_pkt.time_sent)):
                stale_pkts.append(tmp_pkt)
                self.pkt_buffer_out_not_ack.pop(tmp_pkt.id, None)
        #print("ACK was not received for %d packets." %len(stale_pkts))
        return stale_pkts

    def set_start_logs(self, time=0.0):
        yield self.env.timeout(time)
        self.start_logs = True
        if self.verbose:
            print("> The startup phase done. Logs are now on for Client %s." % self.id)

    def __repr__(self):
        return self.id
