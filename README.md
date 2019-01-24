# mdtcp-analysis

MDTCP is a coupled congestion control for multipath TCP (MPTCP). It behaves similar to DCTCP during congestion event at each subflow whereas for congestion avoidance MDTCP enforces a coupled congestion window increase. MDTCP is implemented as a congestion control module of MPTCP (v0.94) in Linux kernel (version 4.14.79). This repository comprises set of scripts to analyze the performance of MDTCP for a datacenter network in Mininet.

Additional details on MDTCP can be obtained from our paper (D. B. Oljira, K. Grinnemo, A. Brunstrom and J. Taheri, "MDTCP: Towards a Practical Multipath Transport Protocol for Telco Cloud Datacenters," NoF 2018 http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8598129&isnumber=8597588)

