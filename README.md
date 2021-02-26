# Simulator

This repository contains the Python implementation of a mix network simulator.
Originally, the simulator was build to perform an empirical analysis of the anonymity offered by the Loopix anonymity system https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/piotrowska and further extended as part of my work at Nym to support more experiments.

The implementation is done using Python 3. My version is `3.7.6` (not sure whether it will run on earlier versions.)
Before running the code remember to make sure that you have all the dependencies installed.

To install the dependencies run

`pip3 install -r requirements.txt`

(If any of the dependencies should be added in the requirements file please let me know.)

To run the simulator you need the command

`python3 playground.py`

You can change the parameters of the simulation in file `test_config.json`

This simulator is a part of an ongoing research work. If you have any questions, please contact me at `ania@nymtech.net`
