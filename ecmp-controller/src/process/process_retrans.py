import sys
import os
import argparse
import csv

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest="files", nargs='+', required=True)

args = parser.parse_args()
retrans=0
for f in args.files:
	if 'trace' in f:
		nconn=os.popen("tcptrace -lr %s | grep 'rexmt data pkts:'"%f).read()
		nlist=nconn.split('\n')
		for n in nlist:
			l=n.split();
			if len(l)==8:
				retrans+=(int(l[3]))
print(retrans)


	
