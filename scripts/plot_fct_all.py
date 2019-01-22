import sys
import os
import argparse
import csv
# import matplotlib as m
# import matplotlib.pyplot as plt
import numpy as np
from numpy import average, std
from math import sqrt
from monitor.helper import *

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest="files", nargs='+', required=True)
parser.add_argument('-o', '--out', dest="out", default=None)
# parser.add_argument('-k', dest="k", default=None)
# parser.add_argument('-w', dest="workload", default=None)
parser.add_argument('-s', dest="subflows", type=int, default=None)

args = parser.parse_args()


''' Parse a file to get FCT and goodput results '''
def parse_file(file_name):
    results = {'size':[],'fct':[]}
    f = open(file_name)

    while True:
        line = f.readline().rstrip()

        if not line:
            break
        arr = line.split(',')
        # Size:34075, Duration(usec):9098403
        
        '''Size:flowsize, Duration(usec):fct'''
        if len(arr) == 2:
            '''[size, fct]'''
           
            measured_fct=float(arr[1].split(':')[1])/1000;
            results['size'].append(int(arr[0].split(':')[1]))
            results['fct'].append(measured_fct)
           
    f.close()
    return results


if __name__ == '__main__':

    fct=[]
    size=[]
    
    for f in args.files:
        results=parse_file(f)

        size=sorted(results['size'])
        
        for s in size:
            for k in range(len(results['size'])):
                if s==results['size'][k]:
                    fct.append(results['fct'][k])
                    break


        
       
