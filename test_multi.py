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
        os.system("pkill -9 -f test_multip.py")
        os.system("pkill -9 -f playground.py")

        # Remove the existing directories
        path = os.getcwd()
        del_paths = glob.glob(os.path.join(path, 'expdir_*'))
        for p in del_paths:
            print(">> Removing path: ", p)
            rmtree(p)
    except:
        pass

    nprocesses = 8
    reps = 15

    dirs = []
    for i in range(0, reps):
        d = 'expdir_%d' % i
        dirs.append(d)

    currentTimestamp = datetime.now().timestamp()
    repsSalt = range(reps)
    seeds = [(int(currentTimestamp) + x) for x in repsSalt]
    print(">> Seeds for the RNG: ", seeds)
    print(">> Dirs: ", dirs)

    with mp.Pool(nprocesses) as pool:
        pool.starmap(runSim, zip(dirs, seeds))

    pool.close()
    pool.join()
