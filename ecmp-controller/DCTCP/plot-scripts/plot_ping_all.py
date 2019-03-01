# from util.helper import *
from collections import defaultdict

import argparse

import numpy as np

import matplotlib as m
m.use('Agg')

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


def parse_ping(f):
  # goodput-mdtcp-20190204-bw10delay0.1ft4runtime60

  ping_delay=[]
  
  for line in open(f).xreadlines():
    aline=line.split()
    if len(aline)==8 and 'icmp_seq' in line:
      pingno=int(aline[4].split('=')[1])
      if pingno > 5:
        pdelay=float(aline[6].split('=')[1])
        ping_delay.append(pdelay)

  return ping_delay
        

def main():

  font = {'family' : 'sans serif','weight' :'normal','size': 10}

  plt.rc('font', **font)

  colors=['blue','red','green','black','magenta','cyan','yellow','orange','purple']

  fig=plt.figure()
  axPlot = fig.add_subplot(1, 1, 1)
  i=0
  for f in ['dctcp-n3-bw100/ping.txt','mdtcp-n3-bw100/ping.txt','mptcp-n3-bw100/ping.txt','tcpecn-n3-bw100/ping.txt','tcp-n3-bw100/ping.txt']:
    ping=parse_ping(f)
    delay_x,cdf_y=emcdf(ping)
    if 'dctcp' in f:
      llabel='DCTCP'
    elif 'mdtcp' in f:
      llabel='MDTCP[SF4]'
    elif 'mptcp' in f:
      llabel='MPTCP[SF4]'
    elif 'tcpecn' in f:
      llabel='TCP-ECN'
    elif 'tcp-n3' in f:
      llabel='TCP-RED'
    

    axPlot.plot(delay_x,cdf_y,label=llabel,color=colors[i],linewidth=4,marker='.')
    i+=1
  
  axPlot.set_xlabel('Ping delay (ms)')
  axPlot.set_ylabel('CDF')
  # axPlot.set_xlim(0,600)
  axPlot.grid(True)
  plt.legend(loc='lower right',ncol=1)
  
  #plt.show()

  plt.savefig(args.out+'delay.pdf')

if __name__ == '__main__':
  main()

