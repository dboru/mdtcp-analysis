#!/usr/bin/perl -w

use Text::CSV;
use IO::File;
use Socket;
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
	 
# substitute here the CSV filename, that must be the same than the
# corresponding MySQL table

my $fh_csv = new IO::File ">udp.csv";

{
 my $line;

 my @csv_line;
 my $csv_obj;
 $csv_obj = new Text::CSV->new({eol => "\n"});

 while($line = <>)
  {
    chomp $line;
    @main::field = split " ",$line;
    my $src_ip = unpack "N", inet_aton ($main::field[0]);
    my $dst_ip = unpack "N", inet_aton ($main::field[8]);
    
    @csv_line = (); 
    
    @csv_line =  (  "\\N",   $src_ip,
                       $main::field[1],
                       $main::field[2],
                       $main::field[3],
                       $main::field[4],
                       $main::field[5],
                       $main::field[6],
		       $main::type{$main::field[7]},
		       $dst_ip,
                       $main::field[9],
                       $main::field[10],
                       $main::field[11],
                       $main::field[12],
                       $main::field[13],
                       $main::field[14],
		       $main::type{$main::field[15]},
		       );
    my $status = $csv_obj->print($fh_csv,\@csv_line);
  }
}


# Close file

$fh_csv->close();
