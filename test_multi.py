import multiprocessing as mp
import os
import playground as pg


def run(edir):
    pg.run(edir)


if __name__ == "__main__":
    nprocesses = 8
    reps = 7

    if nprocesses <= reps:
        raise Exception('More reps than processes. Carefull, this might end up not well.')

    pool = mp.Pool(processes=nprocesses)

    dirs = []
    for i in range(0, reps):
        dirs.append('expdir_%d' % i)

    pool.map(run, dirs)
