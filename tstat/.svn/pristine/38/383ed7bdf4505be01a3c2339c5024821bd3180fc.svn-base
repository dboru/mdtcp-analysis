#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <net/if_arp.h>
#include "cap_utils.h"
#include <unistd.h>
#define _GNU_SOURCE
#include <getopt.h>

#define STPBRIDGES 0x0026
#define CDPVTP 0x016E
#define ETHERTYPE_VLAN 0x8100

#define APP_VERSION_MAJOR 0
#define APP_VERSION_MINOR 2

int main (int argc, char **argv)
{

  extern int optind, opterr, optopt;
  register int op;

  int this_option_optind;
  int option_index;
  int portnumber=0;
  int i;
  static struct option long_options[]= {
    {"content",0,0,'c'},
    {"output",1,0, 'o'},
    {"pkts", 1, 0, 'p'},
    {"help", 0, 0, 'h'},
    {"if", 1,0,'i'},
    {"tcp", 1,0,'t'},
    {"udp", 1,0,'u'},
    {"port", 1,0, 'v'},
    {"calender",0,0,'d'},
    {0, 0, 0, 0}
  };
  
  struct my_arpreq {
   unsigned char arp_sha[ETH_ALEN];	/* Sender hardware address.  */
   unsigned char arp_sip[4];		  /* Sender IP address.  */
   unsigned char arp_tha[ETH_ALEN];	/* Target hardware address.  */
   unsigned char arp_tip[4];      /* Target IP address.  */
  };


  struct vlan_proto {
    u_int16_t type; /* Encoded VLAN */
  };

  cap_head *caphead;
  char* outFilename=0;
  int capOutfile=0;
  int content=0;
  int cDate=0; /* Way to display date, cDate=0 => seconds since 1970. cDate=1 => calender date */  
  char *filename;
  char *nic;
  int streamType;
  char timeStr[25];
  int l,rpStatus;
  char d;
  char* data=&d;
  char** dataPtr=&data;
  u_char* payload=0;
  u_char* payString=0;
  time_t myTime;
  struct filter* myfilter;
  struct ethhdr *ether;
  struct ether_vlan_header *vlan;  
  struct ip *ip_hdr;
  struct tcphdr *tcp;
  struct udphdr *udp;
  struct icmphdr *icmp;
  struct arphdr *arp;
  struct my_arpreq *arpreqHDR;
  struct vlan_proto *vlanPROTO;

  
  streamType=0; // Default a file
  nic=0;
  struct tm tm;
  double pkts,pktCount;
  op=0;

  myfilter=createfilter(argc,argv);
  

  pkts=-1;
  pktCount=0;

  payString = (char*)malloc(20);
  

  if(argc<2){
    printf("use %s -h or --help for help\n",argv[0]);
    exit(0);
  }
  
  while (1) {
    this_option_optind = optind ? optind : 1;
    option_index = 0;
    
    op = getopt_long  (argc, argv, "hp:o:cdi:tuv:",
		       long_options, &option_index);
    if (op == -1)
      break;
//    printf("The OPTION is %c \t",op);
    switch (op){
      case 'd':
	printf("Calender date\n");
	cDate=1;
	break;
      case 'p':
	printf("No packets. Argument %s\n", optarg);
	pkts=atoi(optarg);
	break;
      case 'c':
	printf("Content printing..\n");
	content=1;
	break;
      case 'i':
	printf("Ethernet Argument %s\n", optarg);
	l=strlen(optarg);
	nic=(char*)malloc(l+1);
	strcpy(nic,optarg);
	streamType=1;
	break;
      case 'u':
	printf("UDP \n");
	streamType=2;
	break;
      case 't':
	printf("TCP \n");
	streamType=3;
	break;
      case 'v':
	printf("port %d\n", atoi(optarg));
	portnumber=atoi(optarg);
	break;	
      case 'o':
	printf("Output to file.\n");
	l=strlen(optarg);
	outFilename=(char*)malloc(l+1);
	outFilename=optarg;
	capOutfile=1;              
	printf("Output to data file %s\n",outFilename);
	break;	  
      case 'h':
	printf("-------------------------------------------------------\n");
	printf("Application Version %d.%d\n",APP_VERSION_MAJOR,APP_VERSION_MINOR);
	printf("Application Options\n");
	printf("-p or --pkts   <NO>     Number of pkts to show [default all]\n");
	printf("-o or --output <name>   Store results to a CAP file. \n");
	printf("-d or --calender        Display date/time in YYYY-MM-DD HH:MM:SS.xx.\n");
	printf("-i or --if <NIC>        Listen to NIC for Ethernet multicast address,\n");
	printf("                        identified by <INPUT> (01:00:00:00:00:01).\n");
	printf("-t or --tcp             Listen to a TCP stream.\n");
	printf("                        identified by <INPUT> (192.168.0.10). \n");
	printf("-u or --udp             Listen to a UDP multicast address.\n");
	printf("                        identified by <INPUT> (225.10.11.10).\n");
	printf("-v or --port            TCP/UDP port to listen to. Default 0x0810.\n");
	printf("<INPUT>                 If n,t or u hasn't been declared, this \n");
	printf("                        is interpreted as a filename.\n");
	printf("Usage:\n");
	printf("%s [filter options] [application options] <INPUT>\n", argv[0]);

	exit(0);
	break;
      default:
	printf ("?? getopt returned character code 0%o ??\n", op);
    }
  }
  
  l=strlen(argv[argc-1]);
  filename=(char*)malloc(l+1);
  filename=argv[argc-1];
  struct stream inStream;
  struct stream outStream;
  
  if(!openstream(&inStream,filename,streamType,nic,portnumber)) {
    exit(0);
  }
  if(capOutfile==1) {
    printf("Creating FILE!\n.");
    createstream(&outStream, outFilename, 0, NULL);
    printf("OK.\n");
  }

//output fileheader
  printf("Comment size: %d, ver: %d.%d id: %s \n comments: %s\n",
	 inStream.FH.comment_size, 
	 inStream.FH.version.major, 
	 inStream.FH.version.minor, 
	 inStream.FH.mpid, 
	 inStream.comment);

//allocate buffer memory
  pktCount=0;
//Begin Packet processing

  payload=0;
  char NIC[9];
  char MP[9];

  printf("myFilter.index = %u \n",myfilter->index);
  printf("----------------------------\n");
  rpStatus=read_post(&inStream, dataPtr,myfilter);

  while (rpStatus!=0 ){
//    printf("dataPtr = %p \n",*dataPtr);
    data=*dataPtr;
    pktCount++;
    caphead=(cap_head*)data;
/*
    if(caphead->len<60) {
      printf("!");
    }
*/
    myTime=(time_t)caphead->ts.tv_sec;
    tm = *gmtime(&myTime);
    strftime(timeStr,sizeof(timeStr),"%Y-%m-%d %H:%M:%S",&tm);
    bzero(&MP,9);
    bzero(&NIC,9);
    strncpy(NIC,caphead->nic,8);
    strncpy(MP,caphead->mampid,8);

    printf("[%g]:%s:%s:", pktCount, NIC,MP);
    if(cDate == 0) {
      printf("%lu.", caphead->ts.tv_sec);
    }
    if(cDate == 1 ) {
      printf("%s.", timeStr);
    }
    printf("%012llu:LINK(%4d): \t",caphead->ts.tv_psec, caphead->len);

    if(capOutfile==1) {
      // Save a copy of the frame to the new file.
      if(!(write_post(&outStream,data,caphead->caplen+sizeof(struct cap_header)))) {
	printf("Problems writing data to file!");
      }
    }
    ether=(struct ethhdr*)(data+sizeof(cap_head));
    if(caphead->len<60) {
      printf("%02x:%02x:%02x:%02x:%02x:%02x -> %02x:%02x:%02x:%02x:%02x:%02x [%04x]:", 
	     ether->h_source[0],ether->h_source[1],ether->h_source[2],ether->h_source[3],ether->h_source[4],ether->h_source[5],
	     ether->h_dest[0],  ether->h_dest[1],  ether->h_dest[2],  ether->h_dest[3],  ether->h_dest[4],  ether->h_dest[5], 
	     ntohs(ether->h_proto));
    }
                 
    switch(ntohs(ether->h_proto)) {
      case ETHERTYPE_VLAN:
        vlan=(struct ether_vlan_header*)(data+sizeof(cap_head));
        vlanPROTO=(struct vlan_proto*)(data+sizeof(cap_head)+sizeof(struct ether_vlan_header));
        printf("802.1Q vlan# %d: ", 0x0FFF&ntohs(vlan->vlan_tci));

        if(ntohs(vlanPROTO->type)==ETHERTYPE_IP){
          ip_hdr=(struct ip*)(data+sizeof(cap_head)+sizeof(struct ether_vlan_header)+sizeof(struct vlan_proto));
          goto ipparse;
        } else {
          printf(": Encapsulation type [%0x] ", ntohs(vlanPROTO->type));
          printf("Not a IP .\n");
        }
        break;

      case ETHERTYPE_IP:
        /* Packet contains an IP, PASS TWO! */
	ip_hdr=(struct ip*)(data+sizeof(cap_head)+sizeof(struct ethhdr));
    ipparse:
        printf("IP(HDR[%d])[", 4*ip_hdr->ip_hl);
	printf("Len=%d:",(u_int16_t)ntohs(ip_hdr->ip_len));
	printf("Seq=%d:",(u_int16_t)ntohs(ip_hdr->ip_id));
	printf("TTL=%d:",(u_int8_t)ip_hdr->ip_ttl);
	printf("Chk=%d:",(u_int16_t)ntohs(ip_hdr->ip_sum));
 
        if(ntohs(ip_hdr->ip_off) & IP_DF) {
           printf("DF");
        }
        if(ntohs(ip_hdr->ip_off) & IP_MF) {
           printf("MF");
        }

        printf(" Tos:%0x]:\t",(u_int8_t)ip_hdr->ip_tos);
         /* Packet uses the right transport protocol, PASS FOUR! */
          switch(ip_hdr->ip_p) {
             case IPPROTO_TCP: /* TCP */
                  tcp=(struct tcphdr*)(data+sizeof(cap_head)+sizeof(struct ethhdr)+4*ip_hdr->ip_hl);
		  payload=(void*)tcp+sizeof(struct tcphdr);
                  printf("TCP(HDR[%d]DATA[%0x]):\t [",4*tcp->doff,ntohs(ip_hdr->ip_len)-4*tcp->doff-4*ip_hdr->ip_hl);
                  if(tcp->syn) {
                    printf("S");
                  }
                  if(tcp->fin) {
                    printf("F");
                  }
                  if(tcp->ack) {
                    printf("A");
                  }
                  if(tcp->psh) {
                    printf("P");
                  }
                  if(tcp->urg) {
                    printf("U");
                  }
                  if(tcp->rst) {
                    printf("R");
                  }

                  printf("] %s:%d ",inet_ntoa(ip_hdr->ip_src),(u_int16_t)ntohs(tcp->source));
                  printf(" --> %s:%d",inet_ntoa(ip_hdr->ip_dst),(u_int16_t)ntohs(tcp->dest));
                  break;
             case IPPROTO_UDP: /* UDP */
                  udp=(struct udphdr*)(data+sizeof(cap_head)+sizeof(struct ethhdr)+4*ip_hdr->ip_hl);
		  payload=(void*)udp+sizeof(struct udphdr);
                  printf("UDP(HDR[8]DATA[%d]):\t %s:%d ",(u_int16_t)(ntohs(udp->len)-8),inet_ntoa(ip_hdr->ip_src),(u_int16_t)ntohs(udp->source));
                  printf(" --> %s:%d",inet_ntoa(ip_hdr->ip_dst),(u_int16_t)ntohs(udp->dest));
                  break;
	    case IPPROTO_ICMP: /* ICMP */
	      
	      icmp=(struct icmphdr*)(data+sizeof(cap_head)+sizeof(struct ethhdr)+4*ip_hdr->ip_hl);
	      printf("ICMP:\t %s ",inet_ntoa(ip_hdr->ip_src));
	      printf(" --> %s ",inet_ntoa(ip_hdr->ip_dst));
	      printf("Type %d , code %d \n",(u_int8_t)ntohs(icmp->type),(u_int8_t)ntohs(icmp->code));
/*                  printf("ICMP:"); */
	      break;
	      
	    default:
	      printf("Unknown transport protocol: %d \n", ip_hdr->ip_p);
                  break;
          }
	  if(content==1 && payload!=0){
	    /* Print parts of the payload */
	    memcpy(payString,payload,19);
	    printf("PL:");
	    for(i=0;i<19;i++){
	      printf("%02X",payString[i]);
	    }
          }
	  printf("\n");
	  break;
	  

    case ETHERTYPE_ARP:
      /* Packet contains an ARP */
       arp=(struct arphdr*)(data+sizeof(cap_head)+sizeof(struct ethhdr));
       printf("ARP");
       if(ntohs(arp->ar_op)==ARPOP_REQUEST ) {
         arpreqHDR=(struct my_arpreq*)(data+sizeof(cap_head)+sizeof(struct ethhdr)+sizeof(struct arphdr));
         printf("(HDR[%d]):Request: %02d.%02d.%02d.%02d tell ",sizeof(struct my_arpreq)+sizeof(struct arphdr),arpreqHDR->arp_tip[0],arpreqHDR->arp_tip[1],arpreqHDR->arp_tip[2],arpreqHDR->arp_tip[3]);
         printf("%02d.%02d.%02d.%02d ",arpreqHDR->arp_sip[0],arpreqHDR->arp_sip[1],arpreqHDR->arp_sip[2],arpreqHDR->arp_sip[3]);
         printf("(%02X:%02X:%02X:%02X:%02X:%02X)",arpreqHDR->arp_sha[0],arpreqHDR->arp_sha[1],arpreqHDR->arp_sha[2],arpreqHDR->arp_sha[3],arpreqHDR->arp_sha[4],arpreqHDR->arp_sha[5]);
       }
       if(ntohs(arp->ar_op)==ARPOP_REPLY ) {
         arpreqHDR=(struct my_arpreq*)(data+sizeof(cap_head)+sizeof(struct ethhdr)+sizeof(struct arphdr));
         printf("(HDR[%d]):Reply: %02d.%02d.%02d.%02d is at (%02X:%02X:%02X:%02X:%02X:%02X) tell ",sizeof(struct my_arpreq)+sizeof(struct arphdr),arpreqHDR->arp_tip[0],arpreqHDR->arp_tip[1],arpreqHDR->arp_tip[2],arpreqHDR->arp_tip[3],arpreqHDR->arp_tha[0],arpreqHDR->arp_tha[1],arpreqHDR->arp_tha[2],arpreqHDR->arp_tha[3],arpreqHDR->arp_tha[4],arpreqHDR->arp_tha[5]);
         printf(" %02d.%02d.%02d.%02d (%02X:%02X:%02X:%02X:%02X:%02X)",arpreqHDR->arp_sip[0],arpreqHDR->arp_sip[1],arpreqHDR->arp_sip[2],arpreqHDR->arp_sip[3],arpreqHDR->arp_sha[0],arpreqHDR->arp_sha[1],arpreqHDR->arp_sha[2],arpreqHDR->arp_sha[3],arpreqHDR->arp_sha[4],arpreqHDR->arp_sha[5]);
       }

       printf("\n");
       break;
    case STPBRIDGES:
      printf("STP(0x%x): (spanning-tree for bridges)\n",ntohs(ether->h_proto));
      break;
    case CDPVTP:
      printf("CDP(0x%x): (CISCO Discovery Protocol)\n",ntohs(ether->h_proto));
      break;

    default:
      printf("Not an IP: %0x \n", ntohs(ether->h_proto));
      /* Packet does not contain a IP. */
      break;
    }

    if(pkts>0 && (pktCount+1)>pkts) {
      /* Read enough pkts lets break. */
      break;
    }
    payload=0;
    // Read next packet.
    rpStatus=read_post(&inStream, dataPtr,myfilter);
   }
//End Packet processing

	  
  closestream(&inStream);
  if(capOutfile==1) {
    closestream(&outStream);
  }
  printf("There was a total of %g pkts that matched the filter.\n",pktCount);
  return 0;
}
