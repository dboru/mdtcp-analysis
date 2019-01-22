#!/usr/bin/env python

"""
    Version: 1.1
    Author: Kirth Gersen
    Date created: 6/5/2016
    Date modified: 9/12/2016
    Python Version: 2.7
"""

from __future__ import print_function
import json
import sys
import csv
import argparse
import glob
import os

parser = argparse.ArgumentParser()
# parser.add_argument('--files', '-f',
#                     help="iperf3 json file",
#                     required=True,
#                     action="store",
#                     nargs='+')
parser.add_argument('--files', '-f',
                    help="iperf3 json file",
                    required=True,
                    action="store"
                    )

parser.add_argument('--out', '-o',
                    help="Output json file for the plot.",
                    default=None) # Will show the plot
parser.add_argument('-k', 
                    dest="k", 
                    help="Degree of the Fat Tree",
                    default=None)
parser.add_argument('-w', dest="workload", default=None)
# parser.add_argument('-s', dest="subflows", type=int,required=True,default=None)

args = parser.parse_args()



db = {}

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def main():
    global db
    """main program"""

    with open(args.out, 'w') as csvfile:
        csv.register_dialect('iperf3log', delimiter=',', quoting=csv.QUOTE_MINIMAL)
        csvwriter = csv.writer(csvfile, 'iperf3log')

        if len(sys.argv) == 2:
            if (sys.argv[1] != "-h"):
                sys.exit("unknown option")
            else:
                csvwriter.writerow(["date", "ip", "localport", "remoteport", "duration", "protocol", "num_streams", "cookie", "sent", "sent_mbps", "rcvd", "rcvd_mbps", "totalsent", "totalreceived","fct"])
                sys.exit(0)

        # accummulate volume per ip in a dict
        db = {}
        for fdir in os.listdir(args.files):
            path=args.files+'/'+fdir
            for f in glob.glob(os.path.join(path, 'client_iperf3*')):
                # for f in args.files:
                # if not f.find('client_iperf3'):
                    # continue
                with open(f, 'r') as js:
                    try:
                        obj = json.load(js)
                        # print(obj)
                    except ValueError:
                        continue

                    if "error" in obj.keys() or "error" in obj["end"].keys() or len(obj["start"]["connected"])==0:
                        continue
                    else:
                        
                        subflows=int(f.split("/")[3][5])


                        ip = (obj["start"]["connected"][0]["local_host"]).encode('ascii', 'ignore')
                        local_port = obj["start"]["connected"][0]["local_port"]
                        remote_port = obj["start"]["connected"][0]["remote_port"]
                        size=obj["start"]["test_start"]["bytes"]/1000

                        sent = obj["end"]["sum_sent"]["bytes"]/1000.0
                        rcvd = obj["end"]["sum_received"]["bytes"]/1000.0
                        tstart=obj["end"]["sum_sent"]["start"]
                        tfinish=obj["end"]["sum_sent"]["end"]
                        retransmits=obj["end"]["sum_sent"]["retransmits"]
                        # seconds
                        fct=tfinish-tstart
                        sent_speed = obj["end"]["sum_sent"]["bits_per_second"] / 1000 / 1000
                        rcvd_speed = obj["end"]["sum_received"]["bits_per_second"] / 1000 / 1000
                        

                        reverse = obj["start"]["test_start"]["reverse"]
                        time = (obj["start"]["timestamp"]["time"]).encode('ascii', 'ignore')
                        cookie = (obj["start"]["cookie"]).encode('ascii', 'ignore')
                        protocol = (obj["start"]["test_start"]["protocol"]).encode('ascii', 'ignore')
                        duration = obj["start"]["test_start"]["duration"]
                        num_streams = obj["start"]["test_start"]["num_streams"]
                        if reverse not in [0, 1]:
                            sys.exit("unknown reverse")

                        s = 0
                        r = 0
                        if ip in db:
                            (s, r) = db[ip]

                        if reverse == 0:
                            s+=sent
                            r+=rcvd


                        # if reverse == 0:
                        #     r += rcvd
                        #     sent = 0
                        #     sent_speed = 0
                        # else:
                        #     s += sent
                        #     rcvd = 0
                        #     rcvd_speed = 0

                        db[ip] = (s, r)
                        csvwriter.writerow([ip,duration, protocol, num_streams, sent, sent_speed, rcvd, rcvd_speed, s, r,retransmits,size,fct,subflows])

                        # csvwriter.writerow([time, ip, local_port, remote_port, duration, protocol, num_streams, cookie, sent, sent_speed, rcvd, rcvd_speed, s, r,fct])


def dumpdb(database):
    """ dump db to text """
    for i in database:
        (s, r) = database[i]
        print("%s, %d , %d " % (i, s, r))
if __name__ == '__main__':
    main()
