/*
 *
 * Copyright (c) 2001
 *	Politecnico di Torino.  All rights reserved.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * For bug report and other information please visit Tstat site:
 * http://tstat.polito.it
 *
 * Tstat is deeply based on TCPTRACE. The authors would like to thank
 * Shawn Ostermann for the development of TCPTRACE.
 *
*/

// Extrapolate an IPv4 address from IPv6
void correlate_6to4(struct in6_addr *ip_src6,struct in_addr *ip_src4);

// Normalize an IPv6 address to a IPv4->6 address
// (i.e. the IPv6 DNSCache equivalent format for an IPv4 address
// Equivalent to the conversion from IPv6 to IPv4 and then the mapping of the
// IPv4 address to the normalized format used by DNSCache
void normalize_6to4(struct in6_addr *ip_src6,struct in6_addr *ip_dest6);
