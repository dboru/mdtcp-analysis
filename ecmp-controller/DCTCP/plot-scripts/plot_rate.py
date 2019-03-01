# from util.helper import *
from collections import defaultdict

import argparse

import numpy as np

import matplotlib as m
# m.use('Agg')

import statsmodels.api as sm 
# recommended import according to the docs
import matplotlib.pyplot as plt
import os


import re



parser = argparse.ArgumentParser()

# parser.add_argument('-f', dest="file", nargs='+', required=True)

parser.add_argument('-o', '--out', dest="out", default=None)

parser.add_argument('-path', '--path', dest="path", default=None)

# parser.add_argument('-l', '--load', dest="load", type=int,default=,help="bandwidth")

parser.add_argument('-s', '--subflows', dest="subflows", type=int,default=1,help="no. subflows")


args = parser.parse_args()


def emcdf(data):
  ecdf = sm.distributions.ECDF(data)
  x = np.linspace(min(data), max(data))
  y = ecdf(x)
  return x,y

def main():

  font = {'family' : 'sans serif','weight' :'normal','size': 12}

  plt.rc('font', **font)

  colors=['blue','red','green','black','magenta','cyan','yellow','orange','purple']
  markers=['.','x','*','v','d','D','>','<']
  fig=plt.figure()
  axPlot = fig.add_subplot(1, 1, 1)
  i=0
  rate={}

  for f in os.listdir(args.path):
    if 'iperf' in f:
      rate[i]=[]
      for line in open(args.path+f).xreadlines():
        aline=line.split()
        if 'Mbits/sec' in line:
          rate[i].append(float(aline[-2]))
      i+=1

  for i in range(2):
    axPlot.plot(rate[i],color=colors[i],marker=markers[i],markersize=10,linewidth=2,label='MPTCP'+str(i+1))
    i+=1
  axPlot.set_xlabel('Time (secs)')
  axPlot.set_ylabel('Throughput (Mb/s)')
  axPlot.grid(True)
  plt.legend(loc='upper right',ncol=2)
  # plt.title('TCP ECN with RED-ECN2')
  plt.savefig('mptcp-rate.pdf')
  #axPlot.set_ylim(1,9)
  plt.show()

          


        



  # fig=plt.figure()
  # axPlot = fig.add_subplot(1, 1, 1)
  # i=0
  # for proto in ['mptcp','mdtcp']:
  #   for sf in [1,4]:
  #     ping=parse_ping(proto,sf)
  #     delay_x,cdf_y=emcdf(ping)
  #     if sf==1 and proto=='mdtcp':
  #       llabel='DCTCP'
  #     elif sf==4 and proto=='mdtcp':
  #       llabel='MDTCP[SF4]'
  #     elif sf==8 and proto=='mdtcp':
  #       llabel='MDTCP[SF8]'
  #     elif sf==1 and proto=='mptcp':
  #       llabel='TCP'
  #     elif sf==4 and proto=='mptcp':
  #       llabel='MPTCP[SF4]'
  #     elif sf==8 and proto=='mptcp':
  #       llabel='MPTCP[SF8]'

  #     axPlot.plot(delay_x,cdf_y,label=llabel,color=colors[i])
  #     i+=1
  
  # axPlot.set_xlabel('Ping delay (ms)')
  # axPlot.set_ylabel('CDF')
  # # axPlot.set_xlim(0,600)
  # axPlot.grid(True)
  # plt.legend(loc='lower right',ncol=2)
  
  # #plt.show()

  # plt.savefig(args.out+'ping-delay.pdf')

if __name__ == '__main__':
  main()

