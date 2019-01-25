'''
based on riplpox 
'''

import sys
#sys.path.append(".")

from mininet.topo import Topo
from mininet.node import Controller, RemoteController, OVSKernelSwitch, CPULimitedHost
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.util import custom
from mininet.log import setLogLevel, info, warn, error, debug
from random import choice, shuffle,randint,randrange,uniform
import random

#  For Reactive Routing with ECMP 
from DCTopo import FatTreeTopo, NonBlockingTopo
from DCRouting import Routing

from threading import Timer

# For custom ECMP 
# from DCTopo import FatTreeTopo
# from DCRouting import Routing

import termcolor as T
from subprocess import Popen, PIPE
from argparse import ArgumentParser
import multiprocessing
from multiprocessing import Process
from monitor.monitor import monitor_qlen
from time import time,sleep
from monitor.monitor import monitor_devs_ng
from collections import defaultdict, Counter
from flows import flow
import os
import subprocess
import pickle
import sys
import time
import datetime 



###################################### Hash & Dijkstras Test ######################################################
# import networkx as nx
# from Hashed import HashHelperFunction
# from Dijkstras import dijkstraHelperFunction
# G=nx.Graph()
###################################### Hash & Dijkstras Test ######################################################


# Number of pods in Fat-Tree 
K = 4

# Queue Size
QUEUE_SIZE = 100

# Link capacity (Mbps)
BW = 10 
# flowSource="../emp-tg/conf/DCTCP_CDF.txt"
conn_per_host=1
net_servers=[]
net_switches=[]

log_file = None 

parser = ArgumentParser(description="minient_fattree")

parser.add_argument('-d', '--dir', dest='output_dir', default='log',
        help='Output directory')

# parser.add_argument('-i', '--input', dest='input_file',
#         default='inputs/all_to_all_data',
#         help='Traffic generator input file')

parser.add_argument('-t', '--time', dest='time', type=int, default=30,
        help='Duration (sec) to run the experiment')

parser.add_argument('-K', '--K', dest='K', type=int, default=4,
        help='No. pods in Fattree topology')

parser.add_argument('-p', '--cpu', dest='cpu', type=float, default=-1,
        help='cpu fraction to allocate to each host')

parser.add_argument('--iperf', dest='iperf', default=False, action='store_true',
        help='Use iperf to generate traffics')

parser.add_argument('--ecmp',dest='ECMP',default=False,
        action='store_true',help='Run the experiment with ECMP routing')

parser.add_argument('--tlr',dest='tlr', default=False,
        action='store_true', help='Run the experiment with Fat-Tree two-level routing')

parser.add_argument('--dijkstra',dest='dij',default=False,
        action='store_true',help='Run the experiment with dijkstra routing')
parser.add_argument('--workload',dest="workload",default="one_to_one",action="store",help="Type of workload",required=True)
parser.add_argument('--subflows',type=int,help="Number of subflows",default=1)

parser.add_argument('--bw', '-b',dest="bw",type=float,action="store",help="Bandwidth of links",default=10)
parser.add_argument('--queue', '-q',dest="queue",type=int,action="store",help="Queue size (in packets)", default=200)

parser.add_argument('--enable_ecn',
                    dest="enable_ecn",
                    type=int,
                    help="Enable ECN or not",
                    default=0)
parser.add_argument('--enable_red',
                    dest="enable_red",
                    type=int,
                    help="Enable RED or not",
                    default=0)
parser.add_argument('--delay',
                    help="Link propagation delay (ms)",
                    required=True,
                    default='1ms')

parser.add_argument('--mdtcp',
                    type=int,
                    help="MDTCP test",
                    default=0)
parser.add_argument('--dctcp',
                    type=int,
                    help="DCTCP test",
                    default=0)
parser.add_argument('--redmax',
                    type=int,
                    help="RED max",
                    default=30001)
parser.add_argument('--redmin',
                    type=int,
                    help="RED min",
                    default=30000)
parser.add_argument('--burst',
                    type=int,
                    help="RED burst",
                    default=21)
parser.add_argument('--prob',
                    type=float,
                    help="RED prob",
                    default=1.0)
parser.add_argument('--lag',
                    type=int,
                    help="Time delay before starting MDTCP ",
                    default=0)

parser.add_argument('--load',
                    type=float,
                    help="Network load",
                    default=1.0)
parser.add_argument('--mdtcp_debug',
                    type=int,
                    help="enable debug output",
                    default=0)
parser.add_argument('--num_reqs',
                    type=int,
                    help="number of client requests",
                    default=1)

parser.add_argument('--iter',
                    type=int,
                    help="iteration number",
                    default=1)
parser.add_argument('--test',
                    type=int,
                    help="Test type(throughput=0/FCT=1)",
                    default=0)

parser.add_argument('--qmon',
                    type=int,
                    dest="qmon",
                    help="Turns on queue monitoring at switches if true",
                    default=0)

parser.add_argument('--avg_flow_length',
                    type=int,
                    dest="flow_length",
                    help="Mean flow length for Pareto Traffic Generator",
                    default=30)

parser.add_argument('--bwm',
                    type=int,
                    dest="bwm_ng",
                    help="Eanble monitoring interface rates using bwm-ng",
                    default=0)
parser.add_argument('--tcpdump',
                    type=int,
                    dest="tcpdump",
                    help="dump trace",
                    default=0)
parser.add_argument('--tcpprobe',
                    type=int,
                    dest="tcpprobe",
                    help="trace cwnd using tcpprobe",
                    default=0)

args = parser.parse_args()

def median(l):
    "Compute median from an unsorted list of values"
    s = sorted(l)
    if len(s) % 2 == 1:
        return s[(len(l) + 1) / 2 - 1]
    else:
        lower = s[len(l) / 2 - 1]
        upper = s[len(l) / 2]
        return float(lower + upper) / 2
def saveClntServMapping(clnt_server_mappings,clnt):
    if clnt:
        with open('clnts', 'w') as fp:
            for item in clnt_server_mappings:
                fp.write("%s\n"%item)
            fp.close()
    else:
        with open('servs', 'w') as fp:
            for item in clnt_server_mappings:
                fp.write("%s\n"%item)
            fp.close()
def getClntServMapping(yclnt):
    clnt=[]
    if yclnt is True:
        with open ('clnts', 'r') as fp:
            lines = fp.readlines()
            for line in lines:
                clnt.append(line)
            fp.close()
    else:
        with open ('servs', 'r') as fp:
            lines = fp.readlines()
            for line in lines:
                clnt.append(line)
            fp.close()
    return clnt

def readTrace():
    trace=[]

    with open("../Trace-generator/trace_file/mdtcp-output.trace") as fp:
        lines = fp.readlines()
        for line in lines:
            trace.append(line.split())
    return trace
            

def start_tcpdump(output_dir,iface):
    Popen("tcpdump -i %s -s 96 net 10.0.0.0/16 or net 10.1.0.0/16 or \
        net 10.2.0.0/16 or net 10.3.0.0/16 -C 100 -w %s/trace-%s-%s.dmp \
        -z gzip &"%(iface,output_dir,iface,datetime.datetime.now().strftime("%y%m%d-%H:%M:%S")), shell=True)
    
def start_bwmng(output_dir):
    if args.iter==1 and args.bwm_ng:
        Popen('bwm-ng -t 100 -T rate -c 0  -o csv -C , -F %s/rates_iter.txt &'%(output_dir), shell=True)

class Workload():
    def __init__(self, net, iperf, seconds):
        self.iperf = iperf
        self.seconds = seconds
        self.mappings = []
        self.incast_mappings=[]
        self.net = net
        self.conn_perhost=1

    def run(self, output_dir,subflows):
        servers = list(set([mapping[0] for mapping in self.mappings]))
        for server in servers:
            if args.test==0:
                server.cmd('iperf -s -p 5001 >> /dev/null & ')
        interfaces = []
        for node in self.net.switches:
            for intf in node.intfList():
                if intf.link:
                    interfaces.append(intf.link.intf1.name)
                    interfaces.append(intf.link.intf2.name)
        sleep(2)
        if args.qmon == 1 and args.iter==1:
            print('started queue monitoring! ',subflows)
            qmons = []
            switch_names = [switch.name for switch in self.net.switches]
            for iface in interfaces:
                
                if iface.split('-')[0] in switch_names:             
                    sw=self.layer(iface.split('-')[0])
                    if  args.tcpdump and args.iter==1 and sw =='edge' and ('eth1' in iface or 'eth2' in iface):
                        start_tcpdump(output_dir,iface)
                        # Popen("tstat -l -N net.conf -i %s -s %s/trace-iface-%s"%(iface,output_dir,iface), shell=True)    
                    qmons.append(start_qmon(iface,outfile="%s/queue_size_%s-%s_iter%s.txt"
                                            % (output_dir, sw,iface,str(args.iter))))

     
        if args.test==1:
            
            if args.tcpprobe and args.iter==1:
                start_tcpprobe(output_dir,"cwnd.txt")

            self.ditg_flow_gen(output_dir)

            # self.generate_request(output_dir,subflows)
                
        if args.test==0:
            if args.tcpprobe and args.iter==1:
                start_tcpprobe(output_dir,"cwnd.txt")

            for mapping in self.mappings:
                sleep(0.2)
                server, client = mapping
                client.cmd('iperf -c '+ server.IP()+ ' -p 5001 -t '+ str(self.seconds)+ \
                    ' -yc  -i 1 > '+output_dir+'/client_iperf-'+client.IP()+'-'+server.IP()+'_iter'+str(args.iter)+'.txt &')
                client.cmd('ping '+ server.IP()+ ' -i 1  > '+output_dir+'/ping-'+client.IP()+\
                   '-'+server.IP()+'_iter'+str(args.iter)+'.txt &')

            if args.bwm_ng and args.iter==1:
                start_bwmng(output_dir)
            sleep(args.time)
            os.system('killall -9 bwm-ng ss ping tcpdump')


        # get_rates(interfaces, output_dir)
        # time_run=time.time()+300
        # and time.time()-time_run < 0
        if args.test==0:
             os.system('killall -9 bwm-ng ss ping tcpdump')
             stop_tcpprobe()
             #progress(args.time)

        if args.qmon==1:
            for qmon in qmons:
                qmon.terminate()
    def layer(self, name):
        ''' Return layer of node '''
        # node = self.node_gen(name = name)
        # print(name)
        name_str=name.split('h')
        if int(name_str[0])==args.K:
            return 'core'
        elif int(name_str[2])==1:
            if int(name_str[1]) < args.K/2:
                return 'edge'
            else:
                return 'agg'
        else:
            return 'host'
    

    def ditg_flow_gen(self,output_dir):
        for server in self.net.hosts:
            server.cmd("ITGRecv >> /dev/null &")
        sleep(5)
        trace=readTrace()

        # rate=(args.load*args.bw)/(8*1500*1e-6)
        rate=(args.bw)/(8*1024*1e-6)
        print(rate)

        count=0
        cur_time=time.time()
        last_time=0
        prev_time=0.0 
        bwmng=0

        for clnt in self.net.hosts:
            with open('clnt_%s'%clnt.IP(),'w') as file:
                # os.system('cat > clnt_%s<<END\n'%clnt.IP())
                for conn in trace:
                    if clnt.IP()==conn[1]:
                        server=None
                        for serv in self.net.hosts:
                            if serv.IP()==conn[2]:
                                server=serv
                                break;
                        delayms=1000*float(conn[6])
                        last_time=float(conn[6])
                        fs=int(conn[5])
                        if fs > 1024:
                            fs=fs/1024
                        else:
                            fs=1
                        file.write('-a %s -C %d -c 1024 -T TCP -k %d -t 10000 -d %f -rp 5001\n'%\
                            (server.IP(),rate,fs,delayms))
                file.close()

        for client in self.net.hosts:
            client.cmd("ITGSend clnt_%s -l %s/sender_%s & "%(client.IP(),output_dir,client.IP()))
        print(last_time)
        sleep(last_time+120)

    
    def send_request(self,client, server,servport,flowsize,output_dir):
        client.popen("./../hk-traffic-generator/bin/simple-client -s  %s  -p %d  -n %d -c 1 >> %s/flows_10 &" % \
          (server.IP(), servport, flowsize, output_dir),shell=True)
        
    def generate_request(self,output_dir,subflows):
        load=int(args.bw*args.load/self.conn_perhost)
        server_port_map={}
        hosts=self.net.hosts
        for sserver in hosts:
            servport=5001
            #sserver.cmd('while sleep 1; do ss -i -t -4 ; done > %s/server-'+sserver.IP()+' &' % output_dir)
            sserver.cmd( "./../hk-traffic-generator/bin/server -p %s  >> /dev/null & " % servport)
        
        
        sleep(5)

        trace=readTrace()
        count=0
        cur_time=time.time()
        last_time=0
        prev_time=0.0 
        bwmng=0
        for conn in trace:
            count=count+1
            if count > (len(trace)-1):
                stop_tcpprobe()
                break
            client=None
            server=None
            for h in hosts:
                if h.IP()==conn[1]:
                   client=h
                if h.IP()==conn[2]:
                   server=h
                if client and server:
                   break
            flowsize=int(conn[5])
            start_time=float(conn[6])
            interval=start_time-prev_time

            next_request=trace[count]
            next_time=float(next_request[6])
            last_time=next_time

            # print(start_time,interval)
            # Timer(interval, self.send_request,(client,server,5001,flowsize,output_dir)).start()
            prev_time=start_time

            client.cmd("./../hk-traffic-generator/bin/simple-client -s  %s  -p %d  -n %d \
                -c 1 >> %s/flows_10 &" % (server.IP(), 5001, flowsize, output_dir))
            
            sleep(interval)

            if count > len(self.net.hosts)/2 and bwmng==0 :
                start_bwmng(output_dir)
                bwmng=1

        # print(time.time()-cur_time,last_time)
        
        sleep(60)
        os.system('killall -9 tcpdump tstat ss bwm-ng')
       
        # while True:
        #     clnt=os.popen("ps ax | grep 'ps ax | grep ITGSend' | wc -l").read()
        #     nclnt=clnt.split('\n')
        #     if  len(nclnt) == 2 and int(nclnt[0]) < 4:
        #         # Popen(' mergecap -a -F pcap -w %s/trace.pcap *.pcap'%output_dir,shell=True)
        #         # Popen('rm %s/trace-10.*'%output_dir,shell=True)
        #         os.system('killall -9 tcpdump tstat ss bwm-ng')
        #         break
        #     else:
        #         sleep(1)
            
    def emptraffic_generator(self, output_dir):
        # timeDelay=5.0 
        for mapping in self.mappings:
            server, client = mapping
             
            port=random.randrange(5000,10000)
            # port=5001
            server.cmd('./../emp-tg/bin/server -p '+str(port) +'  >> /dev/null &')
            
            client.cmd('rm ../emp-tg/conf/client_'+client.IP()+'_to_'+server.IP())
            client.cmd('echo server '+ server.IP() +' '+ str(port) +' >> ../emp-tg/conf/client_'+client.IP()+'_to_'+server.IP())
            client.cmd('echo req_size_dist ../emp-tg/conf/DCTCP_CDF.txt >> ../emp-tg/conf/client_'+client.IP()+'_to_'+server.IP())
            client.cmd('echo load '+str(args.bw*args.load)+'Mbps >> ../emp-tg/conf/client_'+client.IP()+'_to_'+server.IP())
            client.cmd('echo fanout 1 100 >> ../emp-tg/conf/client_'+client.IP()+'_to_'+server.IP())

            client.cmd('echo num_reqs '+str(args.num_reqs/self.conn_perhost)+' >> ../emp-tg/conf/client_'+client.IP()+'_to_'+server.IP())
            client.cmd('./../emp-tg/bin/client  -c ../emp-tg/conf/client_'+client.IP()+'_to_'+server.IP()+ \
                 '  -s ' +str(random.randrange(100,50000))+\
                 ' -l flows_'+client.IP()+'_to_'+server.IP()+'_iter'+str(args.iter)+ \
                 '  > log_'+client.IP()+'_to_'+server.IP()+'_iter'+ str(args.iter)+ ' &')
            # if args.iter==1:
            #      client.cmd('while sleep 1; do ss -i -t -4 | grep \'ESTAB\|cwnd\'; done > ss_clnt_'+client.IP()+'_to_serv_'+server.IP()+'&')
            #      # server.cmd('while sleep 1; do ss -i -t -4 | grep \'ESTAB\|cwnd\'; done  > ss_serv_'+server.IP()+'_to_clnt_'+client.IP()+'&')

            sleep(random.randrange(10,1000)/1000.0)
 
        
    def hktraffic_generator(self, output_dir):
        # timeDelay=5.0
        timeDelay = random.randrange(10, 100)
        srvrs={} 
        for mapping in self.mappings:
            server, client = mapping
            if server.IP() not in srvrs.keys():
               srvrs[server.IP()]=1
            elif srvrs[server.IP()] < 3:
               srvrs[server.IP()]=srvrs[server.IP()]+1
            else:
               continue  
            port=random.randrange(5000,10000)
            server.cmd('./../tg/bin/server -p '+str(port) +'  >> /dev/null &')
            sleep(1.0)
            client.cmd('rm ../tg/conf/client_'+client.IP()+'_to_'+server.IP())
            client.cmd('echo server '+ server.IP() +' '+ str(port) +' >> ../tg/conf/client_'+client.IP()+'_to_'+server.IP())
            client.cmd('echo req_size_dist ../tg/conf/DCTCP_CDF.txt >> ../tg/conf/client_'+client.IP()+'_to_'+server.IP())
            #client.cmd('echo rate 90Mbps 100 >> ../tg/conf/client_'+client.IP()+'_to_'+server.IP())
            #client.cmd('echo fanout 1 100 >> ../tg/conf/client_'+client.IP()+'_to_'+server.IP())
           
            client.cmd('./../tg/bin/client  -b '+str(args.bw*args.load/self.conn_perhost) +\
                    ' -c ../tg/conf/client_'+client.IP()+'_to_'+server.IP()+ \
                 ' -l flows_'+client.IP()+'_to_'+server.IP()+'_iter'+str(args.iter)+'.out' \
                 ' -t '+str(args.time)+'  > log_'+client.IP()+'_to_'+server.IP()+'_iter'+ str(args.iter)+ ' &')
            #Popen('bwm-ng -t 100 -T rate -c 0  -o csv -C , -F %s/rates.txt &'%output_dir, shell=True)

# prev version
class OneToOneWorkload(Workload):
    def __init__(self, net, iperf, seconds):
        Workload.__init__(self, net, iperf, seconds)
        hosts = list(net.hosts)
        shuffle(hosts)
        group1, group2 = hosts[::2], hosts[1::2]
        self.create_mappings(list(group1), list(group2))
        self.create_mappings(group2, group1)

    def create_mappings(self, group1, group2):
        while group1:
            server = choice(group1)
            group1.remove(server)
            client = choice(group2)
            group2.remove(client)
            self.mappings.append((server, client)) 


class PermutationMatrix(Workload):
    def __init__(self, net, iperf, seconds, num_conn=1):
        Workload.__init__(self, net, iperf, seconds)
        #num_conn=random.randrange(1,3)
        #num_conn=6
        self.conn_perhost=num_conn
        
        self.create_mappings(net.hosts, num_conn,net.hosts)

    def create_mappings(self, group, num_conn,nets):
        clnts=[]
        serv=[]
        used_server=[]
        clients=(list(group))
        shuffle(clients)
        group=(list(group))
        shuffle(group)

        if args.mdtcp and args.subflows==1:
            for client in clients:
                mapped=False
                while True:
                    for server in group:
                        if server not in used_server and server !=client:
                            clnts.append(client)
                            serv.append(server)
                            self.mappings.append((server, client))                        
                            used_server.append(server)
                            mapped=True
                            break
                    if mapped:
                        break

            saveClntServMapping(clnts,True)
            saveClntServMapping(serv,False)

        else:
            clnts=getClntServMapping(True)
            serv=getClntServMapping(False)
            for i in range(len(clnts)):
                for h in nets:
                    if str(h) in serv[i].split('\n')[0]:
                        srv=h
                        for hh in nets:
                            if clnts[i].split('\n')[0] in str(hh):
                                clnt=hh
                                self.mappings.append((srv, clnt))
                                break

class OneToSeveralWorkload(Workload):
    def __init__(self, net, iperf, seconds, num_conn=3):
        Workload.__init__(self, net, iperf, seconds)
        #num_conn=random.randrange(1,3)
        #num_conn=6
        self.conn_perhost=num_conn
        self.create_mappings(net.hosts, num_conn,net.hosts)
    def create_mappings(self, group, num_conn,nets):
        clnts=[]
        serv=[]
        if args.mdtcp or args.mdtcp==0:
            for server in group:
                clients = list(group)
                clients.remove(server)
                shuffle(clients)
                for client in clients[:num_conn]:
                    clnts.append(client)
                    serv.append(server)
                    self.mappings.append((server, client))
            saveClntServMapping(clnts,True)
            saveClntServMapping(serv,False)
        else:
            clnts=getClntServMapping(True)
            serv=getClntServMapping(False)
            for i in range(len(clnts)):
                for h in nets:
                    if str(h) in serv[i].split('\n')[0]:
                        srv=h
                        for hh in nets:
                            if clnts[i].split('\n')[0] in str(hh):
                                clnt=hh
                                self.mappings.append((srv, clnt))
                                break

class OneToSeveralOffPodWorkload(Workload):
    def __init__(self, net, iperf, seconds, num_conn=2):
        Workload.__init__(self, net, iperf, seconds)
        # num_conn=randrange(1,2)
        self.create_mappings(net.hosts, num_conn)

    def create_mappings(self, group, num_conn):

        for server in group:
            clients = list(group)
            # remove self
            clients.remove(server)
            shuffle(clients)

            for client in clients[:num_conn]:
                self.mappings.append((server, client))

class AllToAllWorkload(Workload):
    def __init__(self, net, iperf, seconds):
        Workload.__init__(self, net, iperf, seconds)
        self.create_mappings(net.hosts)

    def create_mappings(self, group):
        for server in group:
            for client in group:
                if client != server:
                    self.mappings.append((server, client))

def get_workload(net):
    if args.workload == "one_to_one":
        # return OneToOneWorkload(net, args.iperf, args.time)
        # Permutation==OneToOne but Permu.. enables the same 
        # clnt-server mapping test for all protocols
        return PermutationMatrix(net, args.iperf, args.time)
    elif args.workload == "one_to_several":
        return OneToSeveralWorkload(net, args.iperf, args.time)
    else:
        return AllToAllWorkload(net, args.iperf, args.time)


def get_txbytes(iface):
    f = open('/proc/net/dev', 'r')
    lines = f.readlines()
    for line in lines:
        if iface in line:
            break
    f.close()
    if not line:
        raise Exception("could not find iface %s in /proc/net/dev:%s" %
                        (iface, lines))
    # Extract TX bytes from:                                                           
    #Inter-|   Receive                                                |  Transmit      
    # face |bytes    packets errs drop fifo frame compressed multicast|bytes packets \errs drop fifo colls carrier compressed                                                   
# lo: 6175728   53444    0    0    0     0          0         0  6175728   53444 0    0    0     0       0          0                                                          
    return float(line.split()[9])

NSAMPLES = 5
SAMPLE_PERIOD_SEC = 1.0
SAMPLE_WAIT_SEC = 15.0

def get_rates(ifaces, output_dir, nsamples=NSAMPLES, period=SAMPLE_PERIOD_SEC,
              wait=SAMPLE_WAIT_SEC):
    """Returns the interface @iface's current utilization in Mb/s.  It                 
    returns @nsamples samples, and each sample is the average                          
    utilization measured over @period time.  Before measuring it waits                 
    for @wait seconds to 'warm up'."""
    # Returning nsamples requires one extra to start the timer.                        
    nsamples += 1
    last_time = 0
    last_txbytes = Counter()
    ret = []
    sleep(wait)
    txbytes = Counter()
    ret = defaultdict(list)
    while nsamples:
        nsamples -= 1
        for iface in ifaces:
            txbytes[iface] = get_txbytes(iface)
        now = time.time()
        elapsed = now - last_time
        #if last_time:                                                                 
        #    print "elapsed: %0.4f" % (now - last_time)                                
        last_time = now
        # Get rate in Mbps; correct for elapsed time.
        for iface in txbytes:
            rate = (txbytes[iface] - last_txbytes[iface]) * 8.0 / 1e6 / elapsed
            if last_txbytes[iface] != 0:
                # Wait for 1 second sample
                ret[iface].append(rate)
        last_txbytes = txbytes.copy()
        print '.',
        sys.stdout.flush()
        sleep(period)
    f = open("%s/link_util.txt" % output_dir, 'a')
    for iface in ret:
        f.write("%f\n" % median(ret[iface]))
    f.close()

def start_qmon(iface, interval_sec=0.001, outfile="q.txt"):
    monitor = Process(target=monitor_qlen,
                      args=(iface, interval_sec, outfile))
    monitor.start()
    return monitor

def start_tcpprobe(outdir="test",outfile="cwnd.txt"):
    os.system("rmmod tcp_probe; modprobe tcp_probe port=5001 full=0;")

    Popen("cat /proc/net/tcpprobe > %s/%s" % (outdir, outfile),
          shell=True)
def stop_tcpprobe():
    Popen("killall -9 cat", shell=True).wait()

def FatTreeNet(args, bw=10, cpu=-1, queue=100, controller='DCController'):
    droptail = {'max_queue_size': args.queue}
    red = {'max_queue_size': args.queue,'enable_red':1,'enable_ecn': 0, \
    'red_burst':55,'red_prob':0.01,'red_avpkt':1000,\
         'red_min':30000, 'red_max':90000,'red_limit':400000}
    red_ecn = {'max_queue_size': args.queue, 'enable_ecn': args.enable_ecn, \
    'enable_red': args.enable_red,\
            'red_min': args.redmin, 'red_max': args.redmax, 'red_burst': args.burst, \
            'red_prob': args.prob, 'red_avpkt': 1000, 'red_limit': 400000}

    info('*** Creating the topology')
    topo = FatTreeTopo(args.K)
    host = custom(CPULimitedHost, cpu=cpu)
    if args.mdtcp or args.dctcp:
        link = custom(TCLink, bw=args.bw,delay=str(args.delay)+'ms',**red_ecn)
    else:
        link = custom(TCLink, bw=args.bw,delay=str(args.delay)+'ms',**red)
    net = Mininet(topo, host=host, link=link, switch=OVSKernelSwitch,
            controller=RemoteController, autoStaticArp=True)

    return net


def get_max_throughput(net, output_dir):
    
    cprint("Finding max throughput...", 'red')
    seconds = args.time
    server, client = net.hosts[0], net.hosts[1]
    server.cmd('iperf -s -p 5001 & ')

    client.cmd('iperf -c '+ server.IP()+ ' -p 5001 -t '+ str(seconds)+ \
        ' -yc  -i 10 > '+output_dir+'/max_throughput.txt &')
    progress(args.time + 1)
    # proc.communicate()
    os.system('killall -9 iperf  iperf3' )

def install_proactive(net, topo):
    """
        Install proactive flow entries for switches.
    """
    pass

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i 
def progress(t):
    while t > 0:

        print T.colored('  %3d seconds left \r' % (t), 'cyan'),
        t -= 1
        sys.stdout.flush()
        sleep(1)
    print '\r\n'

def cprint(s, color, cr=True):
    """Print in color
       s: string to print
       color: color to use"""
    if cr:
        print T.colored(s, color)
    else:
        print T.colored(s, color),

def enableMPTCP(subflows):
    os.system("sudo sysctl -w net.ipv4.tcp_ecn=0")
    os.system("sudo sysctl -w net.mptcp.mptcp_enabled=1")
    os.system("sudo sysctl -w net.mptcp.mptcp_debug=0")
    os.system("sudo sysctl -w net.mptcp.mptcp_path_manager=ndiffports")
    os.system("sudo echo -n %i > /sys/module/mptcp_ndiffports/parameters/num_subflows" % int(subflows))
    # os.system("sudo sysctl -w net.mptcp.mptcp_path_manager=fullmesh")
    os.system("sudo sysctl -w net.ipv4.tcp_congestion_control=olia")

def enableTCP():
    os.system("sudo sysctl -w net.ipv4.tcp_ecn=0")
    os.system("sudo sysctl -w net.mptcp.mptcp_enabled=0")
    os.system("sudo sysctl -w net.ipv4.tcp_congestion_control=reno")


def enableMDTCP(subflows):
    os.system("sudo sysctl -w net.ipv4.tcp_ecn=1")
    os.system("sudo sysctl -w net.mptcp.mptcp_enabled=1")
    os.system("sudo sysctl -w net.mptcp.mptcp_debug=0")
    os.system("sudo sysctl -w net.mptcp.mptcp_path_manager=ndiffports")
    os.system("sudo echo -n %i > /sys/module/mptcp_ndiffports/parameters/num_subflows" % int(subflows))
    # os.system("sudo sysctl -w net.mptcp.mptcp_path_manager=fullmesh")
    os.system("sudo sysctl -w net.ipv4.tcp_congestion_control=mdtcp")
    
def enableDCTCP():
    os.system("sudo sysctl -w net.ipv4.tcp_ecn=1")
    os.system("sudo sysctl -w net.mptcp.mptcp_enabled=0")
    os.system("sudo sysctl -w net.ipv4.tcp_congestion_control=dctcp")
    

def disableMDTCP():
    os.system("sudo sysctl -w net.ipv4.tcp_ecn=0")
    os.system("sudo sysctl -w net.mptcp.mptcp_enabled=1")
    os.system("sudo sysctl -w net.mptcp.mptcp_path_manager=ndiffports")
    os.system("sudo echo -n 1 > /sys/module/mptcp_ndiffports/parameters/num_subflows")
    os.system("sudo sysctl -w net.ipv4.tcp_congestion_control=olia")

def ConfigureOffloadingAndQdisc(args,net):
    nodes = net.switches
    for node in nodes:
        node.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        node.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        node.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
        for port in node.ports:
            if str.format('{}', port) != 'lo':
                #node.cmd(str.format('ethtool --offload {} tx off rx off gro off tso off', port))
                node.cmd(str.format('ethtool -K {} gso off tso off gro off tx off rx off', port))
                if args.mdtcp or args.dctcp:
                    node.cmd(str.format('tc qdisc del dev {} root',port))
                    node.cmd(str.format('tc qdisc add dev {} root handle 1: htb default 1', port))
                    node.cmd(str.format('tc class add dev {} parent 1: classid 1:1 htb rate {}Mbit ', port,args.bw))
                    node.cmd(str.format('tc qdisc add dev {} parent 1:1 handle 2: red limit 400000 min {} max {} avpkt 1000 burst {} \
                        bandwidth {} probability {} ecn', port,args.redmin,args.redmax,args.burst,args.bw, args.prob))
                else:
                    node.cmd(str.format('tc qdisc del dev {} root',port))
                    node.cmd(str.format('tc qdisc add dev {} root handle 1: htb default 1', port))
                    node.cmd(str.format('tc class add dev {} parent 1: classid 1:1 htb rate {}Mbit ', port,args.bw))
                    node.cmd(str.format('tc qdisc add dev {} parent 1:1 handle 2: red limit 400000 min 30000 max 90000 avpkt 1000 burst 55 \
                        bandwidth {} probability 0.01',port,args.bw))
                    

    # disable offloading and configure qdisc on switch interfaces
    nodes = net.hosts
    # nodes = net.switches
    for node in nodes:
        node.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        node.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        node.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
        for port in node.ports:
            if str.format('{}', port) != 'lo':
                node.cmd(str.format('ethtool -K {} gro off gso off tso off rx off tx off', port))
                node.cmd(str.format('tc qdisc del dev {} root',port))
                node.cmd(str.format('tc qdisc add dev {} root handle 5:0 htb default 1', port))
                node.cmd(str.format('tc class add dev {} parent 5:0 classid 5:1 htb rate {}Mbit ceil {}Mbit burst 15k', port,args.bw,args.bw))
                # node_route = node.cmd("ip route show")
                # node_route=node_route.rstrip()
                # node.popen('ip route replace %s %s %s' % (node_route, 'rto_min','10ms')).wait()
                # node.popen('ip route flush cache').wait()
                # # node.cmd('sysctl -w net.ipv4.tcp_no_metrics_save=1')
                # node.cmd('sysctl -w net.ipv4.route.flush=1')                
                #node.cmdPrint('tc -s -d qdisc show dev %s'%port)
                # node.cmdPrint('ip route')

    return net

def FatTreeTest(args,controller):

    net = FatTreeNet(args, cpu=args.cpu, bw=BW, queue=QUEUE_SIZE,
            controller=controller)
    #pods = range(0, args.K)
    #edge_sw = range(0, args.K/2)
    #agg_sw = range(args.K/2, args.K)
    #core_sw = range(1, args.K/2+1)
    #hosts = range(2, args.K/2+2)
    
    net.start()
    
    net=ConfigureOffloadingAndQdisc(args,net)

    '''
    uncomment and implement the following fucntion if flow tables are installed proactively, 
    in this mode, the mininet can work without a controller
    '''
    # install_proactive(net, topo)
    # wait for the switches to connect to the controller
    print('Waiting for switches to connect to the controller')
    sleep(5)

    workload = get_workload(net)

    # disableMDTCP()
    # enableDCTCP()

    if args.test==0:
        get_max_throughput(net, args.output_dir)

    for nflows in [args.subflows]:
        cwd = os.path.join(args.output_dir, "flows%d" % (nflows))

        # Popen("echo > /dev/null | sudo tee /var/log/syslog",shell=True).wait()
        # Popen("echo > /dev/null | sudo tee /var/log/kern.log",shell=True).wait()
        Popen("rm conf/client_* ",shell=True).wait()
        Popen("rm *reqs.out flows_10.* log_10.*  ",shell=True).wait()

        if not os.path.exists(cwd):
            os.makedirs(cwd)

        if args.mdtcp:
            if nflows==1:
                enableDCTCP()
            else:
                enableMDTCP(nflows)
        elif args.dctcp:
            enableDCTCP()
        else:
            if nflows == 1:
                enableTCP()
            else:
                enableMPTCP(nflows)
        cprint("Starting experiment for workload %s with %i subflows" % (
            args.workload, nflows), "green")

        workload.run(cwd,nflows)

        # Shut down iperf processes
        os.system('killall -9 iperf ping iperf3 netperf netserver server \
            simple-client tcpdump fcttest client tg' )
        Popen("rm *reqs.out ",shell=True).wait()

        Popen("mv flows_10.*  %s"%cwd,shell=True).wait()
        Popen("mv log_10.*  %s"%cwd,shell=True).wait()
        Popen("mv server-10*  %s"%cwd,shell=True).wait()
        # os.system('killall  python pox/pox.py DCController --topo=ft,4 --routing=ECMP')
        sleep(5)

    # disableMDTCP() 
    net.stop()


def clean():
    ''' Clean any running instances of POX '''

    p = Popen("ps aux | grep 'pox' | awk '{print $2}'",
            stdout=PIPE, shell=True)
    p.wait()
    procs = (p.communicate()[0]).split('\n')
    for pid in procs:
        try:
            pid = int(pid)
            Popen('kill %d' % pid, shell=True).wait()
        except:
            pass
    Popen("killall -9 top bwm-ng iperf ping fcttest ", shell=True).wait()

if __name__ == '__main__':

    # Popen("killall -9 top bwm-ng iperf", shell=True).wait()

    setLogLevel( 'output' )
    if not os.path.exists(args.output_dir):
        print args.output_dir
        os.makedirs(args.output_dir)
    Popen("killall -9 top bwm-ng iperf ping tcpdump tg netperf netserver", shell=True).wait()

    # clean()

    if args.ECMP:
        FatTreeTest(args,controller='DCController')
    elif args.dij:
        FatTreeTest(args,controller='DCController')
    elif args.tlr:
        FatTreeTest(args,controller= None) 
    else:
        info('**error** please specify either ecmp, dijkstra or tlr\n')
    #clean()
    Popen("killall -9 top bwm-ng iperf tcpdump ", shell=True).wait()
   
