import simpy
import random


class Queue:
    def __init__(self, env):
        self.env = env
        self.time_to_batch = env.event()
        self.resume_processing = env.event()
        self.queue = []
        env.process(self.add_packets())
        self.bn = 0

    def add_packets(self):
        print("Adding packet")
        i = 0
        while i < 1000:
            print("Added: ", i)
            self.queue.append(i)
            i += 1
            self.env.timeout(0.1)
            if len(self.queue) > 10:
                print("Larger")
                yield self.env.process(self.process_queue())
                # yield self.resume_processing
        return
        yield

    def queue_checking(self):
        if len(self.queue) > 10:
            self.env.process(self.process_queue())

    def process_queue(self):
        print("processing")
        self.bn += 1
        batch = self.queue[:10]
        for i in batch:
            self.queue.remove(i)
        # self.resume_processing.succeed()
        # self.resume_processing = self.env.event()
        print("Finished processing batch nr: ", self.bn)
        return
        yield


    # def add_packets(self):
    #     i = 0
    #     while i < 1000:
    #         self.queue.append(i)
    #         i += 1
    #         self.env.timeout(1)
    #
    # def start_processing(self):
    #     while len(self.queue) > 100:
    #         yield self.env.timeout(0)
    #         self.time_to_batch.succeed()
    #         self.time_to_batch = self.env.event()
    #         self.env.process(self.process_batch())
    #
    # def process_batch(self):
    #     batch = self.queue[:1000]
    #     for i in batch:
    #         self.queue.remove(i)
    #     print("My current batch to process: ", batch)
    #     # self.resume_processing.succeed()
    #     yield self.time_to_batch


    #     self.pupil_procs = [env.process(self.pupil()) for i in range(3)]
    #     self.bell_proc = env.process(self.bell())
    #
    # def bell(self):
    #     for i in range(2):
    #         yield self.env.timeout(45)
    #         self.class_ends.succeed()
    #         self.class_ends = self.env.event()
    #         # print()
    #
    # def pupil(self):
    #     for i in range(2):
    #         print(' \o/')
    #         yield self.class_ends
if __name__ == "__main__":
    env = simpy.Environment()
    school = Queue(env)
    env.run()
