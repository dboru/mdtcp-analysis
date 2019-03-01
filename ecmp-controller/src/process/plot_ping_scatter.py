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


def parse_ping(proto,sf):
  # goodput-mdtcp-20190204-bw10delay0.1ft4runtime60

  ping_delay=[]
  times=[]
 

  path =  'results/goodput-'+proto+'-'+args.path+str(sf)+'/'
  for f in os.listdir(path):
     if 'ping' in f:
        for line in open(path+f).xreadlines():
           aline=line.split()

           if len(aline)==8 and 'icmp_seq' in line:
              icmp_time=int(aline[4].split('=')[1])
              times.append(icmp_time)
              ping_delay.append(float(aline[6].split('=')[1]))
             

  return ping_delay,times
        

def main():

  font = {'family' : 'sans serif','weight' :'normal','size': 10}

  plt.rc('font', **font)

  colors=['blue','red','green','black','olive','steelblue','magenta','brown','cyan','darkblue','orange','purple','lime','yellow']

  fig=plt.figure()
  axPlot = fig.add_subplot(1, 1, 1)
  i=0
  for proto in ['mptcp','mdtcp']:
    for sf in [1,2,3,4,8]:
      ping,times=parse_ping(proto,sf)
      

      # delay_x,cdf_y=emcdf(ping)
      if sf==1 and proto=='mdtcp':
        llabel='DCTCP'
      elif sf==4 and proto=='mdtcp':
        llabel='MDTCP[4SFs]'
      elif sf==8 and proto=='mdtcp':
        llabel='MDTCP[8SFs]'

      elif sf==2 and proto=='mdtcp':
        llabel='MDTCP[2SFs]'
      elif sf==3 and proto=='mdtcp':
        llabel='MDTCP[3SFs]'

      elif sf==1 and proto=='mptcp':
        llabel='TCP'
      elif sf==4 and proto=='mptcp':
        llabel='MPTCP[4SFs]'
      elif sf==8 and proto=='mptcp':
        llabel='MPTCP[8SFs]'

      elif sf==2 and proto=='mptcp':
        llabel='MPTCP[2SFs]'
      elif sf==3 and proto=='mptcp':
        llabel='MPTCP[3SFs]'
      
      axPlot.scatter(times,ping,label=llabel,color=colors[i],marker='.')
      # axPlot.plot(delay_x,cdf_y,label=llabel,color=colors[i])
      i+=1
  
  axPlot.set_xlabel('Time (sec)')
  axPlot.set_ylabel('Ping delay (ms)')
  # axPlot.set_xlim(0,1000)
  axPlot.grid(True)
  plt.legend(loc='upper right',ncol=2)
  
  #plt.show()

  plt.savefig(args.out+'ping-scatter.pdf')

if __name__ == '__main__':
  main()

