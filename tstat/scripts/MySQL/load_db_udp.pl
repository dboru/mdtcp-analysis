#!/usr/bin/perl -w

use DBI;
use strict;

%main::type = ( 0=>"unknown",   
                1=>"unknown",   
	        2=>"unknown",   
                3=>"rtp",       
                4=>"rtcp",      
                5=>"skype_e2e", 
                6=>"skype_out", 
                7=>"skype_sig", 
	        8=>"ed2k",      
	        9=>"kad",       
	       10=>"kadu",      
	       11=>"gnu",       
	       12=>"bt",        
	       13=>"dc",        
	       14=>"kazaa",     
               15=>"pplive",    
               16=>"sopcast",   
               17=>"tvants",
	       18=>"okad",
	       19=>"dns",    
	       20=>"utp",    
	       21=>"utpbt",    
	       22=>"vod",
	       23=>"ppstream",
	       24=>"teredo",    
);
	 
# substitute here the database name, username and password
# the user must have complete rights on the DB (or at least INSERT)
$main::dbh = DBI->connect("DBI:mysql:database","username","password");

$main::sth_udp    = $main::dbh->prepare(
             "INSERT INTO udp values (NULL,INET_ATON(?),?,?,?,?,?,?,?,INET_ATON(?),?,?,?,?,?,?,?)");    
 
# We need to disable indexes and keys while loading the data,
# otherwise operations can be very slow for big files

$main::dbh->do("ALTER TABLE udp DISABLE KEYS;");

{
 my $line;
 while($line = <>)
  {
    chomp $line;
    @main::field = split " ",$line;
    $main::sth_udp->execute( $main::field[0],
                       $main::field[1],
                       $main::field[2],
                       $main::field[3],
                       $main::field[4],
                       $main::field[5],
                       $main::field[6],
		       $main::type{$main::field[7]},
		       $main::field[8],
                       $main::field[9],
                       $main::field[10],
                       $main::field[11],
                       $main::field[12],
                       $main::field[13],
                       $main::field[14],
		       $main::type{$main::field[15]},
		       );
  }
}

# Enable keys
$main::dbh->do("ALTER TABLE udp ENABLE KEYS;");

$main::dbh->disconnect;
