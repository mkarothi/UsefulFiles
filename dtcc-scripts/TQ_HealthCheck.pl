use CGI;
use strict;
use DBI;
use CGI::Carp qw(fatalsToBrowser); # gives detailed errors

my $hostname= "saorap71.dtcc.com";
my $sid="TMQWDP"; 
my $port = "5002";
my $username = "skarothi";
my $password = 'SK0817sk';

my $dbh;
$dbh = DBI->connect("dbi:Oracle:host=$hostname;sid=$sid", $username, $password) or die "connect failed: ". DBI->errstr() unless $dbh;