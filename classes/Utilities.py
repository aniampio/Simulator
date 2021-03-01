from binascii import hexlify
from os import urandom
from math import ceil
import logging
import logging.handlers
import numpy 


def random_string(size):
    return hexlify(urandom(size)).decode('utf8')
    # return ''.join(random.choice(chars) for x in range(size))

def get_exponential_delay(avg_delay, cache=[]):
    if cache == []:
        cache.extend(list(numpy.random.exponential(avg_delay, 10000)))

    return cache.pop()

class StructuredMessage(object):
    def __init__(self, metadata):
        self.metadata = metadata

    def __str__(self):
        return ';'.join(str(x) for x in self.metadata)  # json.dumps(self.metadata)



def float_equlity(tested, correct=1.0):
    return correct * 0.99 < tested < correct * 1.01


def stream_to_file(filename, stream):
    with open(filename, 'a') as outfile:
        outfile.write(stream.getvalue())


def setup_logger(logger_name, filehandler_name, capacity=50000000):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    filehandler = logging.FileHandler(filehandler_name)
    memoryhandler = logging.handlers.MemoryHandler(
                    capacity=capacity,
                    flushLevel=logging.ERROR,
                    target=filehandler
                    )

    logger.addHandler(memoryhandler)
    return logger


def get_total_num_of_target_packets(conf):
    num_target_message = int(conf["misc"]["num_target_messages"])
    packet_size = int(conf["packet"]["packet_size"])
    msg_size = int(conf["message"]["exact_msg_size"])

    return int(num_target_message * (ceil(msg_size/packet_size)))

