# from util.helper import *
from collections import defaultdict

import argparse

import numpy as np

import matplotlib as m
m.use('Agg')

import statsmodels.api as sm # recommended import according to the docs
import matplotlib.pyplot as plt

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
  axPlot.set_xlabel('Delay (ms)')
  axPlot.set_ylabel('Emperical CDF')
  axPlot.grid(True)
  plt.show()


#     if k==0:
#       axPlot.legend(loc='upper center', bbox_to_anchor=(1.2, 1.4),ncol=4, fontsize=8, columnspacing=1.0, handlelength=0.5,fancybox=False, shadow=True)
#     if k%2==0:
#       axPlot.set_ylabel('Utlization',fontsize=8)
#     axPlot.set_yticks(np.arange(0, 1.2, 0.3))
#     if k==6 or k==7:
#       axPlot.set_xlabel('Time (secs)')
#     else:
#       axPlot.set_xticklabels([])
#     if k==1:
#       axPlot.set_title('Edge('+str(k)+')',fontsize=6,loc='right')
#     else:
#       axPlot.set_title('Edge('+str(k)+')',fontsize=6,loc='left')

    


#   plt.savefig(args.out+'-edge-util.pdf')

if __name__ == '__main__':
  main()

