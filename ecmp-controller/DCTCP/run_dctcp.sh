#!/bin/bash

# bws="100 1000"
bws="100"
t=60
n=3
maxq=40
delay="0.1ms"

mn -c

function tcp {
	bw=$1
	odir=tcp-n$n-bw$bw
	sudo python dctcp.py --bw $bw --maxq $maxq --dir $odir -t $t -n $n --delay $delay --tcpdump
	# sudo python util/plot_rate.py --maxy $bw -f $odir/txrate.txt -o $odir/rate.png
	sudo python util/plot_queue.py --maxy 100 -f $odir/qlen_s1-eth1.txt -o $odir/qlen.pdf
	# sudo python util/plot_tcpprobe.py -f $odir/tcp_probe.txt -o $odir/cwnd.pdf
}

function tcp_red_dctcp {
	bw=$1
	odir=tcp_red_dctcp-n$n-bw$bw
	sudo python dctcp.py --bw $bw --maxq $maxq --dir $odir -t $t --tcp_reddctcp -n $n --delay $delay --tcpdump
	# sudo python util/plot_rate.py --maxy $bw -f $odir/txrate.txt -o $odir/rate.png
	sudo python util/plot_queue.py --maxy 100 -f $odir/qlen_s1-eth1.txt -o $odir/qlen.pdf
	# sudo python util/plot_tcpprobe.py -f $odir/tcp_probe.txt -o $odir/cwnd.pdf
}


function ecn {
	bw=$1
	odir=tcpecn-n$n-bw$bw
	sudo python dctcp.py --bw $bw --maxq $maxq --dir $odir -t $t -n $n --ecn --delay $delay --tcpdump
	# sudo python util/plot_rate.py --maxy $bw -f $odir/txrate.txt -o $odir/rate.png
	sudo python  util/plot_queue.py --maxy 100 -f $odir/qlen_s1-eth1.txt -o $odir/qlen.pdf
	# sudo python util/plot_tcpprobe.py -f $odir/tcp_probe.txt -o $odir/cwnd.png
}

function dctcp {
	bw=$1
	odir=dctcp-n$n-bw$bw
	sudo python dctcp.py --bw $bw --maxq $maxq --dir $odir -t $t -n $n --dctcp --delay $delay --tcpdump
	# sudo python util/plot_rate.py --maxy $bw -f $odir/txrate.txt -o $odir/rate.png
	sudo python  util/plot_queue.py --maxy 40 -f $odir/qlen_s1-eth1.txt -o $odir/qlen.pdf
	# sudo python util/plot_tcpprobe.py -f $odir/tcp_probe.txt -o $odir/cwnd.png
}

function mptcp {
	bw=$1
	odir=mptcp-n$n-bw$bw
	sudo python dctcp.py --bw $bw --maxq $maxq --dir $odir -t $t -n $n --delay $delay --mptcp --delay $delay --tcpdump
	# sudo python util/plot_rate.py --maxy $bw -f $odir/txrate.txt -o $odir/rate.png
	sudo python  util/plot_queue.py --maxy 100 -f $odir/qlen_s1-eth1.txt -o $odir/qlen.pdf
	# sudo python  util/plot_tcpprobe.py -f $odir/tcp_probe.txt -o $odir/cwnd.png
}

function mdtcp {
	bw=$1
	odir=mdtcp-n$n-bw$bw
	sudo python dctcp.py --bw $bw --maxq $maxq --dir $odir -t $t -n $n --delay $delay --mdtcp --delay $delay --tcpdump
	# sudo python  util/plot_rate.py --maxy $bw -f $odir/txrate.txt -o $odir/rate.png
	sudo python  util/plot_queue.py --maxy 100 -f $odir/qlen_s1-eth1.txt -o $odir/qlen.pdf
	# sudo python  util/plot_tcpprobe.py -f $odir/tcp_probe.txt -o $odir/cwnd.png
}


for bw in $bws; do
	# sysctl -w net.ipv4.tcp_congestion_control=reno
	# mn -c
    tcp $bw
    mn -c
    sleep 2
    ecn $bw
    sleep 2
    
    dctcp $bw
    sleep 2

    mptcp $bw
    sleep 2

    mdtcp $bw
    sleep 2 
    tcp_red_dctcp $bw

done
