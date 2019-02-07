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

# parser.add_argument('-f', dest="files",nargs='+', required=True)
parser.add_argument('-path', '--path', dest="path", default=None)
parser.add_argument('-o', '--out', dest="out", default=None)
parser.add_argument('-b', '--bw', dest="bw",type=int, default=10)
parser.add_argument('-m', '--maxq', dest="maxq",type=int, default=1000)
parser.add_argument('-p', '--proto', dest="proto", default=None)

args = parser.parse_args()


NUM_COLORS = 36
cm = plt.get_cmap('gist_rainbow')

colors=[cm(1.*i/NUM_COLORS) for i in range(NUM_COLORS)]

def emcdf(data):
  ecdf = sm.distributions.ECDF(data)
  x = np.linspace(min(data), max(data))
  y = ecdf(x)
  return x,y


def parse_queue(proto,sf):
  # goodput-mdtcp-20190204-bw10delay0.1ft4runtime60

  queue=[]
  first_time=0
  path =  'results/goodput-'+proto+'-'+args.path+str(sf)+'/'
  for f in os.listdir(path):
     if 'queue_size' in f:
        for line in open(path+f).xreadlines():
          aline=line.split(',')
          if len(aline)==2 and int(aline[1]) <= (5*1000*args.maxq):
            if first_time==0:
              first_time=float(aline[0]);
            elif float(aline[0]) - first_time > 2.0:
              queue.append((int(aline[1])/1000.0))

  return queue


def main():

  font = {'family' : 'sans serif','weight' :'normal','size': 10}

  plt.rc('font', **font)

  colors=['blue','red','green','black','magenta','cyan','yellow','orange','purple']

  fig=plt.figure()
  axPlot = fig.add_subplot(1, 1, 1)
  i=0
  for proto in ['mptcp','mdtcp']:
    for sf in [1,4,8]:
      queue=parse_queue(proto,sf)
      queue_x,cdf_y=emcdf(queue)
      if sf==1 and proto=='mdtcp':
        llabel='DCTCP'
      elif sf==4 and proto=='mdtcp':
        llabel='MDTCP[4SFs]'
      elif sf==8 and proto=='mdtcp':
        llabel='MDTCP[8SFs]'
      elif sf==1 and proto=='mptcp':
        llabel='TCP'
      elif sf==4 and proto=='mptcp':
        llabel='MPTCP[4SFs]'
      elif sf==8 and proto=='mptcp':
        llabel='MPTCP[8SFs]'

      axPlot.plot(queue_x,cdf_y,label=llabel,color=colors[i])
      i+=1

  axPlot.set_xlabel('Queue (KBytes)')
  axPlot.set_ylabel('CDF')
  axPlot.grid(True)
  plt.legend(ncol=2,loc='lower right')
  plt.savefig(args.out+'-queue.pdf')
  

if __name__ == '__main__':
  main()























