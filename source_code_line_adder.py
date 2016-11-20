# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 21:49:38 2016

@author: David
"""

i = 2575 #start of source code line

with open('function_of_interest_raw.txt') as inf:
    with open('function_of_interest.txt', mode='w') as outf:
        for line in inf:
            outf.write('{0}\t{1}'.format(i, line))
            i += 1