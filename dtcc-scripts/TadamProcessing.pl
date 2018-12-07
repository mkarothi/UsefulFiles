#!/usr/bin/perl -w
use DBI;
use DateTime;
use File::Path;
use Sys::Hostname;
use Net::FTP;
use Cwd;
use IO::Uncompress::Unzip qw(unzip $UnzipError) ;


################################################################################
#                   Confidential
#   Disclosure And Distribution Solely to Employees of
#   DTCC and Its Affiliates Having a Need to Know
#
#   Copyright (c) 2018 DTCC Inc,
#               All Rights Reserved
################################################################################
##      FILE:    ProcessTADAMReports.pl
##
##      AUTHOR:  Murthy Karothi
##
##      DATE:    03/2018
##
##      PURPOSE: This script process the TADAM data and 
##               loads desired data into respective DB tables.
##
##      INPUT   FILES:	TADAM Ziple files 
##		OUTPUT  FILES:	
##      CODE REVIEW INFO:
##         Date      	Actions
##	 	03/08/2018		Intial Version of the Script
##
##      REVISION HISTORY:
##         Date      	Author				Actions
##		03/08/2018   	Murthy Karothi		Initial Version 1.0
##
################################################################################
# Following sub programs used in this script
sub ftpFile(@);
sub execCmd(@);
sub printLog(@);
sub trimString($);
sub printLogAndExit(@);

sub preConnectDB();
sub updateDBTables(@);

# Use the following line if you want to run for yesterdays file
#my $dt = DateTime->now->subtract(days => 1);
my $dt = DateTime->now(time_zone  => 'America/Chicago');

$year   = sprintf ("%04d", $dt->year);
$month  = sprintf ("%02d", $dt->month); 
$day  = sprintf ("%02d", $dt->day);  
$today = "${year}${month}${day}";

print "today : $today \n";
############################ Variable Initialization  ###############################
my $runningMachine = hostname();
my $homeDir = getcwd;

$TADAMInputFilesDir = $homeDir . "/InputFiles";
$logFile = "${homeDir}\\TodaysLog.txt";

############################### Main Program  ##################################
###-----------------------------------------------------------------------------
### Assign Database Variables Here like host, sid, port, userid, password, etc..

open(LOG, ">$logFile") or die "Cannot open the $logFile file for writing";
LOG->autoflush(1);

printLog ("processing started at " . scalar(localtime) );

###### Reading the input Excel files to extract data #################
print "Your Input files Directory : $TADAMInputFilesDir \n";
opendir(my $dh, $TADAMInputFilesDir) || printLogAndExit("The Source file $TADAMInputFile does not exist:$_ ");
  #  @TADAMInputfiles = grep { /\_${today}*.csv/ && -f "$TADAMInputFilesDir/$_" } readdir($dh);
   #  @TADAMInputfiles = grep { /\.csv/ && /$today/ && -f "$TADAMInputFilesDir/$_" } readdir($dh);
    @TADAMZipfiles = grep { /\.zip/ && /$today/ && -f "$TADAMInputFilesDir/$_" } readdir($dh);
closedir $dh;

### calling preconnect DB function here
preConnectDB();

###### Reading each csv file Here and updating table ##############
foreach $TADAMZipFile (@TADAMZipfiles) {
	print "Working on the file : $TADAMZipFile \n";
	###readExcelFile("${TADAMInputFilesDir}\\${TADAMInputFile}");
	
	$TADAMInputFile = "SYSID_Components.csv" if ($TADAMZipFile =~ /SYSID_Components/i);
	$TADAMInputFile = "SystemComponents.csv" if ($TADAMZipFile =~ /SystemComponents/i);
	unlink($TADAMInputFile) if (-f $TADAMInputFile);
	
	unzip "${TADAMInputFilesDir}/${TADAMZipFile}" => "${TADAMInputFilesDir}/${TADAMInputFile}"
		or die "unzip failed: $UnzipError\n";
	
	updateDBTables("${TADAMInputFilesDir}/${TADAMInputFile}", "epe_dtcc.tadam_sysid_components_tmp") if ($TADAMInputFile =~ /SYSID_Components/i);
	updateDBTables("${TADAMInputFilesDir}/${TADAMInputFile}", "epe_dtcc.tadam_system_components_datas") if ($TADAMInputFile =~ /SystemComponents/i);
}

$dbh->disconnect();
print "Done and Exiting \n";
################################################################################
# ##############################################################################
# Open DB connection and clean all files
# ##############################################################################
################################################################################
sub preConnectDB() {

########## Connecting to Database Server Here
	$database = "epe_dtcc";
	$host = "localhost";
	$port = "3306";
	$user = "epe_admi";
	$password = "Work4dtcc";

	#DATA SOURCE NAME
	$dbh = DBI->connect("DBI:mysql:database=$database;host=$host;port=$port",
					  $user, $password, {RaiseError => 1});
	return;
}

################################################################################
# ##############################################################################
# Update DB tables with respective data
# ##############################################################################
################################################################################
sub updateDBTables(@) {
	$IPFile = shift;
	$tableName = shift;

	print "table : $tableName \n";
	print "file : $IPFile \n";
	## truncate command execution
	#step 1# Delete exisitng table data

		$truncateCommand = "truncate table ${tableName}";
		$sth = $dbh->prepare($truncateCommand) || die "truncate table ${tableName} prepare: $truncateCommand: $DBI::errstr"; 
		$sth->execute || die "truncate table ${tableName}  execute: $truncateCommand: $DBI::errstr"; 


	#step 2# Updating CMDB Server data
	$loadCommand = "LOAD DATA LOCAL INFILE \'$IPFile\' INTO TABLE  ${tableName} \
					FIELDS TERMINATED BY \'\,\' \
					ENCLOSED BY \'\"\' \
					LINES TERMINATED BY \'\\n\' \
					IGNORE 1 LINES";

	$sth = $dbh->prepare($loadCommand) || die "table Update prepare: $loadCommand: $DBI::errstr"; 
	$sth->execute || die "table Update execute: $loadCommand: $DBI::errstr"; 
	
	return;
}




################################################################################
# Trim the string here
################################################################################
sub trimString($)
{
    my $string = shift;
    return 0 if (!defined($string));
    $string =~ s/^\s+//;
    $string =~ s/\s+$//;
    $string =~ s/\"+//g;
    return $string;
}

###-----------------------------------------------------------------------------

################################################################################
# send message to normal trace log
################################################################################
sub printLog(@)
{
    my ($message) = @_;
    print LOG "CiRBA Duplicates Processing: " . $message . "\n";
}

################################################################################
# send message to normal trace log, and exit app
################################################################################
sub printLogAndExit(@)
{
    my ($message) = @_;
    printLog($message);
    close(LOG);
    exit(1);
}

################################################################################
# Executing command line command
################################################################################
sub execCmd(@)
{
    my ($Cmd, $errMsg) = @_;
	#print "Executing : " . $Cmd ."\n";
	system($Cmd);
	# if ( $? >> 8 ) {
	if ( $? > 10 ) {
		printLog("$errMsg $! \n");
		printLog("Erros in executing $Cmd \n Please check the logs after completion of the program \n command return code : $? \n");
	}
}



