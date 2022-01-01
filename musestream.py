#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 22:00:56 2019

@author: wrichter
"""

import argparse
import sys
import muselsl
import muselsl.stream as stream
from muselsl import list_muses
import muselsl.record as record
import muselsl.view as view
import muselsl.helper as helper
import muselsl.muse as muse
import muselsl.constants as constants
from elevate import elevate

acc = False
address = '00:55:DA:B3:BE:F7'
backend = 'auto'
disable_eeg = False
gyro = False
interface = None
name = None
ppg = False

# must run in shell 
elevate()
# muses = list_muses()
# print(muses)
stream(address, backend, interface, name, ppg, acc, gyro, disable_eeg)

# to run: python /home/wrichter/Documents/Code/Projects/Python/neural/musestream.py
# To View: muselsl view --version 2
# To record EEG data into a CSV: muselsl record --duration 60  

# Brainwave Types:
    # Gamma: Frequency 32 - 100 Hz
    # -State: Heightened perception, learning, problem-solving tasks
    # Beta: Frequency: 13-32 Hz
    # -State: Alert, normal alert consciousness, active thinking
    # Alpha: Frequency: 8-13 Hz
    # -State: Physically and mentally relaxed
    # Theta: Frequency: 4-8 Hz
    # -State: Creativity, insight, dreams, reduced consciousness

# Electrodes:
    # Frontal Lobe: AF7, AF8
    # Temporal: TP9, TP10


# https://pypi.org/project/muselsl/2.1.0/
# https://choosemuse.com/blog/a-deep-dive-into-brainwaves-brainwave-frequencies-explained-2/
