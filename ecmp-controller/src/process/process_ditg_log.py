
import os
import argparse

import numpy as np

parser = argparse.ArgumentParser()

parser.add_argument('-f', dest="file", nargs='+', required=True)

parser.add_argument('-o', '--out', dest="out", default=None)

parser.add_argument('-p', '--proto', dest="proto", default=None)

parser.add_argument('-b', '--bwd', dest="bwd", type=int,default=10,help="bandwidth")


args = parser.parse_args()


def parse_ditg_log():
	ditg_fct={}
	newflow=0
	fid=0;
	for f in args.file:
		log=os.popen("ITGDec %s"%f).read().split('\n')
	  	for line in log:
	  		if 'Flow number:' in line:
	  			newflow=1
	  			fid+=1
	  			ditg_fct[fid]={}
	  		elif 'Average loss-burst size' in line:
	  			newflow=0
	  		if newflow and 'Total time' in line:
	  			ditg_fct[fid]['fct']=float(line.split()[3])
	  		if newflow and 'Bytes received' in line:
	  			ditg_fct[fid]['size']=int(line.split()[3])

  	print(len(ditg_fct.keys()))


def main():

  # font = {'family' : 'sans serif','weight' :'normal','size': 10}

  # plt.rc('font', **font)

  # colors=['blue','red','green','black','magenta','cyan','yellow','orange','purple']

  ping=parse_ditg_log()

  # delay_x,cdf_y=emcdf(ping)
  
  # fig=plt.figure()
  # axPlot = fig.add_subplot(1, 1, 1)
  # axPlot.plot(delay_x,cdf_y)
  # axPlot.set_xlabel('Delay (ms)')
  # axPlot.set_ylabel('Emperical CDF')
  # axPlot.grid(True)
  # plt.show()

if __name__ == '__main__':
  main()