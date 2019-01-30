#!/bin/bash

# bws="100 1000"
bws="100"
t=20
n=5
maxq=425
delay="0.1ms"

function tcp {
	bw=$1
	odir=tcp-n$n-bw$bw
	sudo python dctcp.py --bw $bw --maxq $maxq --dir $odir -t $t -n $n 
	# sudo python ../util/plot_rate.py --maxy $bw -f $odir/txrate.txt -o $odir/rate.png
	# sudo python ../util/plot_queue.py -f $odir/qlen_s1-eth1.txt -o $odir/qlen.png
	# sudo python ../util/plot_tcpprobe.py -f $odir/tcp_probe.txt -o $odir/cwnd.png
}

function ecn {
	bw=$1
	odir=tcpecn-n$n-bw$bw
	sudo python dctcp.py --bw $bw --maxq $maxq --dir $odir -t $t -n $n --ecn 
	# sudo python ../util/plot_rate.py --maxy $bw -f $odir/txrate.txt -o $odir/rate.png
	# sudo python ../util/plot_queue.py -f $odir/qlen_s1-eth1.txt -o $odir/qlen.png
	# sudo python ../util/plot_tcpprobe.py -f $odir/tcp_probe.txt -o $odir/cwnd.png
}

function dctcp {
	bw=$1
	odir=dctcp-n$n-bw$bw
	sudo python dctcp.py --bw $bw --maxq $maxq --dir $odir -t $t -n $n --dctcp 
	# sudo python ../util/plot_rate.py --maxy $bw -f $odir/txrate.txt -o $odir/rate.png
	# sudo python ../util/plot_queue.py --maxy 50 -f $odir/qlen_s1-eth1.txt -o $odir/qlen.png
	# sudo python ../util/plot_tcpprobe.py -f $odir/tcp_probe.txt -o $odir/cwnd.png
}

function mptcp {
	bw=$1
	odir=mptcp-n$n-bw$bw
	sudo python dctcp.py --bw $bw --maxq $maxq --dir $odir -t $t -n $n --delay $delay --mptcp 
	# sudo python ../util/plot_rate.py --maxy $bw -f $odir/txrate.txt -o $odir/rate.png
	# sudo python ../util/plot_queue.py --maxy 50 -f $odir/qlen_s1-eth1.txt -o $odir/qlen.png
	# sudo python ../util/plot_tcpprobe.py -f $odir/tcp_probe.txt -o $odir/cwnd.png
}

function mdtcp {
	bw=$1
	odir=mdtcp-n$n-bw$bw
	sudo python dctcp.py --bw $bw --maxq $maxq --dir $odir -t $t -n $n --delay $delay --mdtcp 
	# sudo python ../util/plot_rate.py --maxy $bw -f $odir/txrate.txt -o $odir/rate.png
	# sudo python ../util/plot_queue.py --maxy 50 -f $odir/qlen_s1-eth1.txt -o $odir/qlen.png
	# sudo python ../util/plot_tcpprobe.py -f $odir/tcp_probe.txt -o $odir/cwnd.png
}


for bw in $bws; do
	# sysctl -w net.ipv4.tcp_congestion_control=reno
	# mn -c
    # tcp $bw
    # mn -c
    # sleep 2
    # ecn $bw
    # sleep 2
    # sysctl -w net.ipv4.tcp_ecn=1
    # sysctl -w net.ipv4.tcp_congestion_control=dctcp
    dctcp $bw
    # sleep 2
    # mptcp $bw
    # sleep 2
    # mdtcp $bw

done