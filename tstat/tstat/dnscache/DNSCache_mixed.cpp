/*
 * DNSCache.cpp
 *
 * This module provide public methods
 * to be called from a C/C++ program.
 * C code must be compiled together
 * using a C++ compiler as g++.
 *
 * When it's called from C, since it isn't
 * an object oriented language, the function
 * cacheInitialize must be called first specifying
 * the maximum number of DNS entries the cache can
 * have.
 *
 * Input for the cache are
 * hostname, client_ip, and an array with server ip
 * addresses returned by the DNS server.
 *
 * To query the cache just ask for client_ip and
 * any server_ip, it returns a hostname if it
 * finds it in the cache, else it returns a NULL
 * that must be checked from C to avoid further
 * segmentation faults when using that piece of
 * data.
 *
 *  Created on: Oct 12, 2011
 *      Author: Ignacio Bermudez
 *  Modified on May 2016 by Maurizio M. Munafo' to manage IPv6 addresses
 */

#include "DNSCache_mixed.h"
//#include "DNSEntry.h"
#include <map>

/*
 * Functions to manage IPv4 (A) information contained in IPv6 DNS queries and IPv6 (AAAA) 
 * information contained in IPv4 DNS queries.
 * They are only used only if SUPPORT_MIXED_DNS is defined.
 *
 * For the sake of simplicity, DNSEntryIPv6 are used in both cases, and IPv4 addresses
 * are supposed having been converted in IPv6 format.
 * The code using these functions will know when and how to interprete the address as IPv4 
 * or IPv6.
 *
 * The functions here are the clones of the ones in DNSCache_ipv6.cpp, changed to refer to
 * different distinct static Maps/HashTables. 
 * In a future implementation we might change the interface so that also the map/hashtable is
 * passed as a parameter, so to avoid the code duplication.
 *
 * *4_dns6* are used for A records in IPv6 DNS queries, *6_dns4* for AAAA records in IPv4 DNS queries
 */ 


std::map <struct my_in6_addr, std::map <struct my_in6_addr, DNSEntryIPv6 *> > ipv4_dns6_hashtable;
unsigned int pointer_ipv4_dns6 = 0;
int size_ipv4_dns6;
DNSEntryIPv6 *cyclicList_ipv4_dns6;

std::map <struct my_in6_addr, std::map <struct my_in6_addr, DNSEntryIPv6 *> > ipv6_dns4_hashtable;
unsigned int pointer_ipv6_dns4 = 0;
int size_ipv6_dns4;
DNSEntryIPv6 *cyclicList_ipv6_dns4;

void cacheInitialize_ipv4_dns6(int s){
	DNSEntryIPv6 nullEntry;
	cyclicList_ipv4_dns6 = new DNSEntryIPv6 [s];
	for(int i=0;i<s;i++){
		cyclicList_ipv4_dns6[i] = nullEntry;
	}
	size_ipv4_dns6 = s;
}

void cacheInitialize_ipv6_dns4(int s){
	DNSEntryIPv6 nullEntry;
	cyclicList_ipv6_dns4 = new DNSEntryIPv6 [s];
	for(int i=0;i<s;i++){
		cyclicList_ipv6_dns4[i] = nullEntry;
	}
	size_ipv6_dns4 = s;
}

int insert_ipv4_dns6(
		unsigned char* hostname,
		struct my_in6_addr client_ip,
		struct my_in6_addr *servers,
		int n_servers,
		//unsigned long int dns_server,
		struct in6_addr dns_server,
		timeval request_time,
		timeval response_time){
	DNSEntryIPv6 entry (
			hostname,
			client_ip,
			servers,
			n_servers,
			dns_server,
			request_time,
			response_time);

	DNSEntryIPv6 &lastEntry = cyclicList_ipv4_dns6[pointer_ipv4_dns6%size_ipv4_dns6];
	lastEntry.deleteReferences(ipv4_dns6_hashtable);
	cyclicList_ipv4_dns6[pointer_ipv4_dns6%size_ipv4_dns6] = entry;
	for(unsigned int i=0; i<n_servers/sizeof(servers[0]);i++){
		ipv4_dns6_hashtable[client_ip][servers[i]] = &cyclicList_ipv4_dns6[pointer_ipv4_dns6%size_ipv4_dns6];
	}
	pointer_ipv4_dns6++;
	if (pointer_ipv4_dns6%size_ipv4_dns6==0) 
	 {
	   pointer_ipv4_dns6 = 0;
	   return size_ipv4_dns6;
	 }
	return 0;
}

int insert_ipv6_dns4(
		unsigned char* hostname,
		struct my_in6_addr client_ip,
		struct my_in6_addr *servers,
		int n_servers,
		//unsigned long int dns_server,
		struct in6_addr dns_server,
		timeval request_time,
		timeval response_time){
	DNSEntryIPv6 entry (
			hostname,
			client_ip,
			servers,
			n_servers,
			dns_server,
			request_time,
			response_time);

	DNSEntryIPv6 &lastEntry = cyclicList_ipv6_dns4[pointer_ipv6_dns4%size_ipv6_dns4];
	lastEntry.deleteReferences(ipv6_dns4_hashtable);
	cyclicList_ipv6_dns4[pointer_ipv6_dns4%size_ipv6_dns4] = entry;
	for(unsigned int i=0; i<n_servers/sizeof(servers[0]);i++){
		ipv6_dns4_hashtable[client_ip][servers[i]] = &cyclicList_ipv6_dns4[pointer_ipv6_dns4%size_ipv6_dns4];
	}
	pointer_ipv6_dns4++;
	if (pointer_ipv6_dns4%size_ipv6_dns4==0) 
	 {
	   pointer_ipv6_dns4 = 0;
	   return size_ipv6_dns4;
	 }
	return 0;
}

struct DNS_data_IPv6* getEntry_ipv4_dns6(struct my_in6_addr client_ip, struct my_in6_addr server_ip){
	if(ipv4_dns6_hashtable.count(client_ip)>0){
		std::map<struct my_in6_addr, DNSEntryIPv6*> &server_map = ipv4_dns6_hashtable[client_ip];
		if(server_map.count(server_ip)>0){
			DNSEntryIPv6 entry = *server_map[server_ip];
			return entry.getDNSData();
		}
	}
	return NULL;
}

struct DNS_data_IPv6* getEntry_ipv6_dns4(struct my_in6_addr client_ip, struct my_in6_addr server_ip){
	if(ipv6_dns4_hashtable.count(client_ip)>0){
		std::map<struct my_in6_addr, DNSEntryIPv6*> &server_map = ipv6_dns4_hashtable[client_ip];
		if(server_map.count(server_ip)>0){
			DNSEntryIPv6 entry = *server_map[server_ip];
			return entry.getDNSData();
		}
	}
	return NULL;
}

unsigned char* get_ipv4_dns6(struct my_in6_addr client_ip, struct my_in6_addr server_ip){
	if(ipv4_dns6_hashtable.count(client_ip)>0){
		std::map<struct my_in6_addr, DNSEntryIPv6*> &server_map = ipv4_dns6_hashtable[client_ip];
		if(server_map.count(server_ip)>0){
			DNSEntryIPv6 entry = *server_map[server_ip];
			return entry.getHostname();
		}
	}
	return NULL;
}

unsigned char* get_ipv6_dns4(struct my_in6_addr client_ip, struct my_in6_addr server_ip){
	if(ipv6_dns4_hashtable.count(client_ip)>0){
		std::map<struct my_in6_addr, DNSEntryIPv6*> &server_map = ipv6_dns4_hashtable[client_ip];
		if(server_map.count(server_ip)>0){
			DNSEntryIPv6 entry = *server_map[server_ip];
			return entry.getHostname();
		}
	}
	return NULL;
}

struct in6_addr* get_dns_server_ipv4_dns6(struct my_in6_addr client_ip, struct my_in6_addr server_ip){
	if(ipv4_dns6_hashtable.count(client_ip)>0){
			std::map<struct my_in6_addr, DNSEntryIPv6*> &server_map = ipv4_dns6_hashtable[client_ip];
			if(server_map.count(server_ip)>0){
				DNSEntryIPv6 entry = *server_map[server_ip];
				return entry.getDNSServer();
			}
		}
	return NULL;
}

struct in6_addr* get_dns_server_ipv6_dns4(struct my_in6_addr client_ip, struct my_in6_addr server_ip){
	if(ipv6_dns4_hashtable.count(client_ip)>0){
			std::map<struct my_in6_addr, DNSEntryIPv6*> &server_map = ipv6_dns4_hashtable[client_ip];
			if(server_map.count(server_ip)>0){
				DNSEntryIPv6 entry = *server_map[server_ip];
				return entry.getDNSServer();
			}
		}
	return NULL;
}
