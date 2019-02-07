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

parser.add_argument('-f', dest="files",nargs='+', required=True)

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


def main():
  
  font = {'family' : 'sans serif','weight' :'normal','size': 10}

  plt.rc('font', **font)
  queue={'Core':[],'Agg':[],'Edge':[]}
  first_time=0;

  colors=['blue','red','green','black','magenta','cyan','yellow','orange','purple']

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
          # queue[layer]={'time':[],'queue':[]}
          first_entry=0

        for line in open(f).xreadlines():
          aline=(line.split(','))
          if len(aline)==2 and int(aline[1]) <= (5*1000*args.maxq):
            if first_time==0:
              first_time=float(aline[0]);
            elif float(aline[0]) - first_time > 2.0:
              if 'core' in layer:
                queue['Core'].append((int(aline[1])))
              elif 'agg' in layer:
                queue['Agg'].append((int(aline[1])))
              elif 'edge' in layer:
                queue['Edge'].append((int(aline[1])))

  if queue:
    fig=plt.figure()
    axPlot = fig.add_subplot(1, 1, 1)
    i=0
 
    for a in queue.keys():
      queue_x,cdf_y=emcdf(queue[a])
      axPlot.plot(queue_x,cdf_y,label=a,color=colors[i])
      i+=1

    axPlot.set_xlabel('Queue (Bytes)')
    axPlot.set_ylabel('CDF')
    axPlot.grid(True)
    plt.legend(ncol=3,loc='lower right')
    plt.savefig(args.out+'queue.pdf')


if __name__ == '__main__':
  main()





















