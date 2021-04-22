import multiprocessing as mp
import os
import playground as pg


def run(edir):
    pg.run(edir)


if __name__ == "__main__":

    # Kill previously running ones in case left somewhere
    os.system('pkill -9 -f test_multip.py')
    os.system('pkill -9 -f playground.py')

    # Remove the existing directories
    os.system('rm -r expdir_*')

    nprocesses = 10
    reps = 3

    if nprocesses <= reps:
        raise Exception('More reps than processes. Carefull, this might end up not well.')

    pool = mp.Pool(processes=nprocesses)

    dirs = []
    for i in range(0, reps):
        d = 'expdir_%d' % i
        dirs.append(d)


    pool.map(run, dirs)
