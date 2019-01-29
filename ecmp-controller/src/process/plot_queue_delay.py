# from util.helper import *

from collections import defaultdict

import argparse

import numpy as np

import matplotlib as m
from statsmodels.distributions.empirical_distribution import ECDF

m.use('Agg')

import matplotlib.pyplot as plt

import re


parser = argparse.ArgumentParser()

parser.add_argument('-f', dest="files",nargs='+', required=True)

parser.add_argument('-o', '--out', dest="out", default=None)
parser.add_argument('-b', '--bw', dest="bw",type=int, default=10)
parser.add_argument('-m', '--maxq', dest="maxq",type=int, default=100)

parser.add_argument('-p', '--proto', dest="proto", default=None)

args = parser.parse_args()


NUM_COLORS = 36
cm = plt.get_cmap('gist_rainbow')

colors=[cm(1.*i/NUM_COLORS) for i in range(NUM_COLORS)]


def cdf(values):
  values.sort()
  prob = 0
  l = len(values)
  x, y = [], []

  for v in values:
      prob += 1.0 / l
      x.append(v)
      y.append(prob)

  return x, y

def plot_queue_stats(queue):

  font = {'family' : 'sans serif','weight' :'normal','size': 10}

  plt.rc('font', **font)

  # colors=['blue','red','green','black','magenta','cyan','yellow','orange','purple']


  fig = plt.figure()

  axplot = fig.add_subplot(111)

  # axplot1 = fig.add_subplot(222)

  # axplot2 = fig.add_subplot(223)

  c=0;
  
  aqueue={'core':[],'agg':[],'edge':[]}
  for a in sorted(queue.keys()):
    if 'core' in a and len(queue[a]['time'])>0:
      # core.append(queue[a])
      # print(queue[a]['time'][0])
      if len(aqueue['core'])==0:
        aqueue['core']=queue[a]['queue']
      else:
        aqueue['core']=aqueue['core']+queue[a]['queue']
    elif 'agg' in a and len(queue[a]['time'])>0:
      if len(aqueue['agg'])==0:
        aqueue['agg']=queue[a]['queue']
      else:
        aqueue['agg']=aqueue['agg']+queue[a]['queue']

    elif 'edge' in a and len(queue[a]['time'])>0:
      if len(aqueue['edge'])==0:
        aqueue['edge']=queue[a]['queue']
      else:
        aqueue['edge']=aqueue['edge']+queue[a]['queue']

  x,y=cdf(aqueue['core'])
  axplot.plot(x,y,color='red',label='Core')
  x,y=cdf(aqueue['agg'])
  axplot.plot(x,y,color='blue',label='Agg')
  x,y=cdf(aqueue['edge'])
  axplot.plot(x,y,color='black',label='Edge')
  

  axplot.grid(True)
  axplot.set_xlabel('Queuing delay [ms]')
  axplot.set_ylabel('CDF')
  axplot.legend(loc='lower right')
  plt.savefig(args.out+'queuing-delay.pdf')


def main():

  queue={}
  for f in args.files:
    layer=None
    # queue_size_core-4_2_2-eth4_iter1.txt

    if 'queue_size' in f:
      ll=(f.split('queue_size'))
      for l in range (len(ll)):
        if '-eth' in ll[l]:
          layer=ll[l].split('iter')[0].strip('_')
          break
      
      if layer:

        if layer not in queue.keys():
          queue[layer]={'time':[],'queue':[]}
          first_entry=0

        for line in open(f).xreadlines():
          aline=(line.split(','))
          if len(aline)==2 and (int(aline[1])/1000.0) <=args.maxq:
            if first_entry==0:
              queue[layer]['time'].append(float(aline[0]))
              queue[layer]['queue'].append((0.008*int(aline[1])/args.bw))
              first_entry=1
            else:
              diff_time=float(aline[0])-queue[layer]['time'][0]
              queue[layer]['time'].append(diff_time)
              # queuing delay in ms
              queue[layer]['queue'].append((0.008*int(aline[1])/args.bw))


  if queue:
    plot_queue_stats(queue)

if __name__ == '__main__':
  main()





















