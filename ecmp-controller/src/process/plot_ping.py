# from util.helper import *
from collections import defaultdict

import argparse

import numpy as np

import matplotlib as m
m.use('Agg')

import statsmodels.api as sm 
# recommended import according to the docs
import matplotlib.pyplot as plt



import re



parser = argparse.ArgumentParser()

parser.add_argument('-f', dest="file", nargs='+', required=True)

parser.add_argument('-o', '--out', dest="out", default=None)

parser.add_argument('-p', '--proto', dest="proto", default=None)

parser.add_argument('-b', '--bwd', dest="bwd", type=int,default=10,help="bandwidth")


args = parser.parse_args()


def emcdf(data):
  ecdf = sm.distributions.ECDF(data)
  x = np.linspace(min(data), max(data))
  y = ecdf(x)
  return x,y


def parse_ping():

  ping_delay=[]

  for f in args.file:
    for line in open(f).xreadlines():

      aline=line.split()
      if len(aline)==8 and 'icmp_seq' in line:

        pdelay=float(aline[6].split('=')[1])
        ping_delay.append(pdelay)

  return ping_delay
        

def main():

  font = {'family' : 'sans serif','weight' :'normal','size': 10}

  plt.rc('font', **font)

  colors=['blue','red','green','black','magenta','cyan','yellow','orange','purple']

  ping=parse_ping()


  delay_x,cdf_y=emcdf(ping)


  
  fig=plt.figure()
  axPlot = fig.add_subplot(1, 1, 1)
  axPlot.plot(delay_x,cdf_y)
  axPlot.set_xlabel('Ping delay (ms)')
  axPlot.set_ylabel('CDF')
  axPlot.grid(True)
  
  #plt.show()

  plt.savefig(args.out+'ping-delay.pdf')

if __name__ == '__main__':
  main()

