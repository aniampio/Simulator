import multiprocessing as mp
import os
import glob
import playground as pg
from datetime import datetime
from shutil import rmtree
import time


def runSim(edir, rseed):
    pg.runSimulation(edir=edir, rseed=rseed)


if __name__ == "__main__":

    try:
        # Kill previously running ones in case left somewhere
        os.system('pkill -9 -f test_multip.py')
        os.system('pkill -9 -f playground.py')
        # Remove the existing directories
        del_paths = glob.glob(os.path.join(path, 'expdir_*'))
        for p in del_paths:
            shutil.rmtree(p)
    except:
        pass

    nprocesses = 8
    reps = 8

    if nprocesses < reps:
        raise Exception('More reps than processes. Carefull, this might end up not well.')

    pool = mp.Pool(processes=nprocesses)

    dirs = []
    for i in range(0, reps):
        d = 'expdir_%d' % i
        dirs.append(d)

    currentTimestamp = datetime.now().timestamp()
    repsSalt = range(reps)
    seeds = [(int(currentTimestamp) + x) for x in repsSalt]
    print(">> Seeds for the RNG: ", seeds)

with Pool(nprocesses) as pool:
    pool.starmap(runSim, zip(dirs, seeds))
    time.sleep(5)

pool.close()
pool.join()
