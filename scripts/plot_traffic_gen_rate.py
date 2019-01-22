import sys
import os
import argparse
import csv
# import matplotlib as m
import matplotlib.pyplot as plt
import numpy as np
from numpy import average, std
from math import sqrt


parser = argparse.ArgumentParser()
parser.add_argument('-f', dest="file",nargs='+', required=True)
parser.add_argument('-o', '--out', dest="out", default=None)
# parser.add_argument('-k', dest="k", default=None)
# parser.add_argument('-w', dest="workload", default=None)
# parser.add_argument('-t', dest="time", type=int, default=None)

args = parser.parse_args()

packets=[]

def movingaverage (values, window):
    weights = np.repeat(1.0, window)/window
    sma = np.convolve(values, weights, 'same')
    return sma


''' Parse a file to get FCT and goodput results '''
def parse_file(file_name):
    results = {}


    f = open(file_name)
    tend=0.0
    size=0

    rate=[]
    ttime=[]
    
    while True:
        line = f.readline().rstrip()

        if not line:
            break
        arr = line.split()
        # ['963', '10.1.1.3', '10.2.1.3', '20123', '20124', '1555747', '8.679315398']
        srcdest=arr[1]+'_'+arr[2]

        # if float(arr[6]) < 300.0:

        if  (float(arr[6])-tend<5.0):
            # print(float(arr[6]),tend)
            size=size+int(arr[5])
            
        else:
            # print(size,8*1e-6*size,float(arr[6]))
            rate.append(8*1e-6*size/5.0)
            packets.append(1e-6*size/1500)
            ttime.append(float(arr[6]))
            tend=float(arr[6])
            size=int(arr[5])


        # else:
        #     print(size)
        #     tend=float(arr[6])
        #     size=int(arr[5])


        if srcdest not in results.keys():
            results[srcdest]={'flow':[int(arr[5])],'time':[float(arr[6])]}
        else:
            results[srcdest]['flow'].append(int(arr[5]))
            results[srcdest]['time'].append(float(arr[6]))
        
    f.close()

    # print(np.mean(util))

    return rate,ttime


if __name__ == '__main__':
 
    
    fig = plt.figure()
    ax={}
    for a in range(4):
        ax[a]= fig.add_subplot(2,2,(a+1))
        ax[a].grid(True)
    load=['20%','40%','60%','100%']
    
    a=0
    for f in args.file:
        rate,ttime=parse_file(f)
        label=(f.split('-')[1])
        ax[a].plot(ttime,rate,marker='.',color='red',label='Inst.rate')
        ax[a].plot(ttime, movingaverage(rate,10),marker='.',color='blue',label='Mavg')
        ax[a].set_title('('+str(a+1)+')'+' Load='+load[a],fontsize=8,loc='left')
        # if a<2:
        #     ax[a].set_xticklabels(fontsize=8)
        if a>1:
            ax[a].set_xlabel('Time[secs]',fontsize=8)
        if a % 2==0:
            ax[a].set_ylabel('Traffic rate [Mb/s]',fontsize=10)
        ax[a].legend(ncol=2,loc='upper right',fontsize=10)
        # ax[a].set_yticks(np.arange(0, 500, 50))
        a+=1
    
    plt.show()

    



       