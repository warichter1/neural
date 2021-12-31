#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 30 21:50:45 2021

@author: wrichter
"""

import numpy as np 
from bandScan import GetWaves


def test(params):
    print('Test me', params)
    return 0
    
    
if __name__ == "__main__":
    print("Activating")
    waves = GetWaves()
    waves.run(test, ['1', '2', '3'])