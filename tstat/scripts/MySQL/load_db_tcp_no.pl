#!/usr/bin/perl -w

use DBI;
use strict;

# check_internal.pl provides is_internal() needed for logs 
# generated by Tstat before v.2.2 (r330)
#
# require 'check_internal.pl';

# substitute here the database name, username and password
# the user must have complete rights on the DB (or at least INSERT)
$main::dbh = DBI->connect("DBI:mysql:database","username","password");

$main::sth_tcp   = $main::dbh->prepare(
             "INSERT INTO tcp_no values (NULL,INET_ATON(?),?,?,?,?,?,?,INET_ATON(?),?,?,?,?,?,?,?,?,?,?)");    

# We need to disable indexes and keys while loading the data,
# otherwise operations can be very slow for big files

$main::dbh->do("ALTER TABLE tcp_no DISABLE KEYS;");

{
 my $line;
 while($line = <>)
  {
    chomp $line;
    @main::field = split " ",$line;
    $main::sth_tcp->execute( $main::field[0],  # src_ip
                       $main::field[1],        #src_port
                       $main::field[2],        #src_packets
                       $main::field[12],       #src_syn
                       $main::field[3],        #src_rst
                       $main::field[4],        #src_ack
                       $main::field[13],       #src_fin
                       $main::field[44],       #dst_ip
                       $main::field[45],       #dst_port 
                       $main::field[46],        #dst_packets
                       $main::field[56],       #dst_syn
                       $main::field[47],        #dst_rst
                       $main::field[48],        #dst_ack
                       $main::field[57],       #dst_fin
                       $main::field[89],       #start_time
                       $main::field[88],       #duration
                       $main::field[98],       #src_internal
                       $main::field[99],      # dst_internal
		       );
  }
}

# Enable keys
$main::dbh->do("ALTER TABLE tcp_no ENABLE KEYS;");

$main::dbh->disconnect;
