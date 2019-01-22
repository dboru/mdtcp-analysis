# from helper import *
from collections import defaultdict
import argparse
import matplotlib.pyplot as plt
import os
from datetime import timedelta
# import process_tstat


# Indicate if the connection has full info or only a subset
TCP_COMPLETE = 'tcp_complete'
# Source IP address
SADDR = 'saddr'
# Destination IP address
DADDR = 'daddr'
# Source port
SPORT = 'sport'
# Destination port
DPORT = 'dport'
# Window scale for source
WSCALESRC = 'wscalesrc'
# Window scale for destination
WSCALEDST = 'wscaledst'
# Start of a connection (first packet)
START = 'start_time'
# Duration of a connection
DURATION = 'duration'
# Number of packets
PACKS = 'packets'
# Number of bytes
BYTES = 'bytes'
# Number of data bytes (according to tcptrace)
BYTES_DATA = 'bytes_data'
# Number of bytes missed by tcptrace (if non-zero, this connection should be take with care)
MISSED_DATA = 'missed_data'
# Number of packets retransmitted
PACKS_RETRANS = 'packets_retrans'
# Number of bytes retransmitted
BYTES_RETRANS = 'bytes_retrans'
# Timestamp of retransmissions
TIMESTAMP_RETRANS = 'timestamp_retrans'
# tcpcsm information about retransmissions
TCPCSM_RETRANS = 'tcpcsm_retrans'
# Number of packets out of orders
PACKS_OOO = 'packets_outoforder'
# Congestion window graph data dictionary
CWIN_DATA = 'congestion_window_data'
# Timestamp of reinjected packets
REINJ_ORIG_TIMESTAMP = 'reinjected_orig_timestamp'
# Reinjected packets
REINJ_ORIG_PACKS = 'reinjected_orig_packets'
# Reinjected bytes
REINJ_ORIG_BYTES = 'reinjected_orig_bytes'
# Reinjected origin
REINJ_ORIG = 'reinjected_orig'
# Is reinjection (timestamp in char + bytes reinjected)
IS_REINJ = 'is_reinjection'
# Number of bytes returned by mptcptrace (unique bytes)
BYTES_MPTCPTRACE = 'bytes_mptcptrace'
# Total number of bytes of frames
BYTES_FRAMES_TOTAL = 'bytes_frames_total'
# Total number of frames
FRAMES_TOTAL = 'frames_total'
# Total number of retransmitted bytes of frames
BYTES_FRAMES_RETRANS = 'bytes_frames_retrans'
# Total number of retransmitted frames
FRAMES_RETRANS = 'frames_retrans'
# Throughput returned by tpctrace
THGPT_TCPTRACE = 'throughput_tcptrace'
# Throughput returned by mptcptrace
THGPT_MPTCPTRACE = 'throughput_mptcptrace'
# MPTCP bursts
BURSTS = 'bursts'
# Flights information
FLIGHT = 'flight'

# RTT info
RTT_SAMPLES = 'rtt_samples'
RTT_MIN = 'rtt_min'
RTT_MAX = 'rtt_max'
RTT_AVG = 'rtt_avg'
RTT_STDEV = 'rtt_stdev'
RTT_3WHS = 'rtt_from_3whs'
RTT_99P = 'rtt_99p'
RTT_98P = 'rtt_98p'
RTT_97P = 'rtt_97p'
RTT_95P = 'rtt_95p'
RTT_90P = 'rtt_90p'
RTT_75P = 'rtt_75p'
RTT_MED = 'rtt_median'
RTT_25P = 'rtt_25p'

# For aggregation
C2S = 'client2server'
S2C = 'server2client'

# Kept for compatibility reasons
S2D = C2S
D2S = S2C

# Number of SYN, FIN, RST and ACK seen on a subflow
NB_SYN = 'nb_syn'
NB_FIN = 'nb_fin'
NB_RST = 'nb_rst'
NB_ACK = 'nb_ack'

# Relative time to the beginning of the connection
TIME_FIRST_PAYLD = 'time_first_payload'
TIME_LAST_PAYLD = 'time_last_payload'
TIME_FIRST_ACK = 'time_first_ack'

# Timestamp (absolute values)
TIME_FIN_ACK_TCP = 'time_fin_ack_tcp'
TIME_LAST_ACK_TCP = 'time_last_ack_tcp'
TIME_LAST_PAYLD_TCP = 'time_last_payload_tcp'
TIME_LAST_PAYLD_WITH_RETRANS_TCP = 'time_last_payload_with_retrans_tcp'

# Time to live
TTL_MIN = 'time_to_live_min'
TTL_MAX = 'time_to_live_max'

# Segment size
SS_MIN = 'segment_size_min'
SS_MAX = 'segment_size_max'

# Congestion window
CWIN_MIN = 'minimum_in_flight_size'
CWIN_MAX = 'maximum_in_flight_size'

# Subflow inefficiencies
NB_RTX_RTO = 'nb_rtx_rto'
NB_RTX_FR = 'nb_rtx_fr'
NB_REORDERING = 'nb_reordering'
NB_NET_DUP = 'nb_network_duplicate'
NB_UNKNOWN = 'nb_unknown'
NB_FLOW_CONTROL = 'nb_flow_control'
NB_UNNECE_RTX_RTO = 'nb_unnecessary_rtx_rto'
NB_UNNECE_RTX_FR = 'nb_unnecessary_rtx_fr'

# Multipath TCP inefficiencies
REINJ_BYTES = 'reinj_bytes'
REINJ_PC = 'reinj_pc'

# To process both directions
DIRECTIONS = [C2S, S2C]

IPv4 = 'IPv4'
IPv6 = 'IPv6'

# IPv4 localhost address
LOCALHOST_IPv4 = '127.0.0.1'
# Port number of RedSocks
PORT_RSOCKS = '8123'
# Prefix of the Wi-Fi interface IP address
PREFIX_WIFI_IF = '192.168.'
# Size of Latin alphabet
SIZE_LAT_ALPH = 26
# IP address of the proxy (has to be overriden)
IP_PROXY = False
# Size of the header of frame of a MPTCP packet with data (16 + 20 + 52)
FRAME_MPTCP_OVERHEAD = 88

# Those values have to be overriden
PREFIX_IP_WIFI = False
PREFIX_IP_PROXY = False

IP_WIFI = False
IP_CELL = False

TIMESTAMP = 'timestamp'
CONN_ID = 'conn_id'
FLOW_ID = 'flow_id'

# Info from the SOCKS command
SOCKS_PORT = 'socks_port'
SOCKS_DADDR = 'socks_daddr'

# ADD_ADDRs and REMOVE_ADDRs
ADD_ADDRS = 'add_addrs'
RM_ADDRS = 'rm_addrs'

# Backup bit of a subflow
BACKUP = 'backup'

# Retransmission of DSS
RETRANS_DSS = 'retrans_dss'




parser = argparse.ArgumentParser()
# parser.add_argument('-p', '--port', dest="port", default='5001')
parser.add_argument('-f', dest="files", nargs='+', required=True)
parser.add_argument('-o', '--out', dest="out", default=None)
# parser.add_argument('-H', '--histogram', dest="histogram",
#                     help="Plot histogram of sum(cwnd_i)",
#                     action="store_true",
#                     default=False)

args = parser.parse_args()

def first(lst):
    return map(lambda e: e[0], lst)

def second(lst):
    return map(lambda e: e[1], lst)


connections = {}
conn_id = 0


def extract_tcp_complete(filename, connections, conn_id):
    """ Subpart of extract_tstat_data dedicated to the processing of the log_tcp_complete file
        Returns the connections seen and the conn_id reached
    """
    log_file = open(filename)
    data = log_file.readlines()
    for line in data:
        # Case 1: line start with #; skip it
        
        if not line.startswith("#"):
            # Case 2: extract info from the line
            info = line.split()
            # print(int(info[22]),float(info[30]) / 1000.0,info[0],info[14],info[1],info[15])

            if len(info)<134:
                continue
            conn_id += 1
            connections[conn_id]={}
            connections[conn_id][TCP_COMPLETE]=True
            connections[conn_id][SADDR]=info[0]
            connections[conn_id][DADDR]=info[14]
            connections[conn_id][SPORT]=info[1]
            connections[conn_id][DPORT]=info[15]


            # Except RTT, all time (in ms in tstat) shoud be converted into seconds
            connections[conn_id][START] = timedelta(seconds=float(info[28])/1000)
            connections[conn_id][DURATION] = float(info[30]) / 1000.0
            connections[conn_id][C2S]={}
            connections[conn_id][S2C]={}
            connections[conn_id][C2S][PACKS] = int(info[2])
            connections[conn_id][S2C][PACKS] = int(info[16])
            # Note that this count is about unique data bytes (sent in the payload)
            connections[conn_id][C2S][BYTES] = int(info[6])
            connections[conn_id][S2C][BYTES] = int(info[20])
            # This is about actual data bytes (sent in the payload, including retransmissions)
            connections[conn_id][C2S][BYTES_DATA] = int(info[8])
            connections[conn_id][S2C][BYTES_DATA] = int(info[22])

            # print(int(info[22]),float(info[30]) / 1000.0,info[0],info[14],info[1],info[15])

            connections[conn_id][C2S][PACKS_RETRANS] = int(info[9])
            connections[conn_id][S2C][PACKS_RETRANS] = int(info[23])
            connections[conn_id][C2S][BYTES_RETRANS] = int(info[10])
            connections[conn_id][S2C][BYTES_RETRANS] = int(info[24])

            print(int(info[9]),int(info[23]),int(info[78]),int(info[101]),int(info[79]),int(info[102]),info[0],info[14],info[1],info[15])

            connections[conn_id][C2S][PACKS_OOO] = int(info[11])
            connections[conn_id][S2C][PACKS_OOO] = int(info[25])

            connections[conn_id][C2S][NB_SYN] = int(info[12])
            connections[conn_id][S2C][NB_SYN] = int(info[26])
            connections[conn_id][C2S][NB_FIN] = int(info[13])
            connections[conn_id][S2C][NB_FIN] = int(info[27])
            connections[conn_id][C2S][NB_RST] = int(info[3])
            connections[conn_id][S2C][NB_RST] = int(info[17])
            connections[conn_id][C2S][NB_ACK] = int(info[4])
            connections[conn_id][S2C][NB_ACK] = int(info[18])

            # Except RTT, all time (in ms in tstat) shoud be converted into seconds
            connections[conn_id][C2S][TIME_FIRST_PAYLD] = float(info[31]) / 1000.0
            connections[conn_id][S2C][TIME_FIRST_PAYLD] = float(info[32]) / 1000.0
            connections[conn_id][C2S][TIME_LAST_PAYLD] = float(info[33]) / 1000.0
            connections[conn_id][S2C][TIME_LAST_PAYLD] = float(info[34]) / 1000.0
            connections[conn_id][C2S][TIME_FIRST_ACK] = float(info[35]) / 1000.0
            connections[conn_id][S2C][TIME_FIRST_ACK] = float(info[36]) / 1000.0

            connections[conn_id][C2S][RTT_SAMPLES] = int(info[48])

            connections[conn_id][S2C][RTT_SAMPLES] = int(info[55])
            connections[conn_id][C2S][RTT_MIN] = float(info[45])
            connections[conn_id][S2C][RTT_MIN] = float(info[52])
            connections[conn_id][C2S][RTT_MAX] = float(info[46])
            connections[conn_id][S2C][RTT_MAX] = float(info[53])
            connections[conn_id][C2S][RTT_AVG] = float(info[44])
            connections[conn_id][S2C][RTT_AVG] = float(info[51])
            connections[conn_id][C2S][RTT_STDEV] = float(info[47])
            connections[conn_id][S2C][RTT_STDEV] = float(info[54])
            connections[conn_id][C2S][TTL_MIN] = float(info[49])
            connections[conn_id][S2C][TTL_MIN] = float(info[56])
            connections[conn_id][C2S][TTL_MAX] = float(info[50])
            connections[conn_id][S2C][TTL_MAX] = float(info[57])

            connections[conn_id][C2S][SS_MIN] = int(info[71])
            connections[conn_id][S2C][SS_MIN] = int(info[94])
            connections[conn_id][C2S][SS_MAX] = int(info[70])
            connections[conn_id][S2C][SS_MAX] = int(info[93])

            connections[conn_id][C2S][CWIN_MIN] = int(info[76])
            connections[conn_id][S2C][CWIN_MIN] = int(info[99])
            connections[conn_id][C2S][CWIN_MAX] = int(info[75])
            connections[conn_id][S2C][CWIN_MAX] = int(info[98])

            connections[conn_id][C2S][NB_RTX_RTO] = int(info[78])
            connections[conn_id][S2C][NB_RTX_RTO] = int(info[101])
            connections[conn_id][C2S][NB_RTX_FR] = int(info[79])
            connections[conn_id][S2C][NB_RTX_FR] = int(info[102])
            connections[conn_id][C2S][NB_REORDERING] = int(info[80])
            connections[conn_id][S2C][NB_REORDERING] = int(info[103])
            connections[conn_id][C2S][NB_NET_DUP] = int(info[81])
            connections[conn_id][S2C][NB_NET_DUP] = int(info[104])
            connections[conn_id][C2S][NB_UNKNOWN] = int(info[82])
            connections[conn_id][S2C][NB_UNKNOWN] = int(info[105])
            connections[conn_id][C2S][NB_FLOW_CONTROL] = int(info[83])
            connections[conn_id][S2C][NB_FLOW_CONTROL] = int(info[106])
            connections[conn_id][C2S][NB_UNNECE_RTX_RTO] = int(info[84])
            connections[conn_id][S2C][NB_UNNECE_RTX_RTO] = int(info[107])
            connections[conn_id][C2S][NB_UNNECE_RTX_FR] = int(info[85])
            connections[conn_id][S2C][NB_UNNECE_RTX_FR] = int(info[108])

    log_file.close()
    return connections,conn_id

def parse_file(f):
    tstat = {}
    
    for l in open(f).xreadlines():
        fields = l.strip().split(' ')
        if 'c_pkts_all' in l:
            for key in fields:
                tstat[key.split(':')[0]]=0
        else:
            clntserv=fields[0]+':'+fields[1]+'_'+fields[14]+':'+fields[15]
            if clntserv not in tstat.keys():
                tstat[clntserv]={}
                tstat[clntserv]={'clnt_bytes':int(fields[8]),'srv_bytes':int(fields[22]),'fct':float(fields[30])}
                # print (int(fields[8]),int(fields[22]),float(fields[30]))
                print(clntserv)
            else:
                print(clntserv)

    return tstat

def findInSubdir(subdirectory,connections,conn_id):
    if subdirectory:
        path=subdirectory
    else:
        os.getcwd()
    for root, dirs, names in os.walk(path):
        if 'out' in root:
            for file in os.listdir(root):
                if 'tcp_complete' in file:


                    tcp_file=os.path.join(root,file)

                    connections,conn_id=extract_tcp_complete(tcp_file, connections, conn_id)
                    conn_id += 1
def process_tstat():
    connections={}
    conn_id=0

    fpath=findInSubdir(str(args.files[0]),connections,conn_id)
    

process_tstat()


