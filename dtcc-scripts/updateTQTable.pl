#!/usr/bin/perl -w
use DBI;
use DateTime;
use Cwd;


### Functions used in this scripts.

### program specific functions
sub preConnectDB();
sub updateDBTables(@);

$currDir = getcwd();

$Linux_DBFile = $currDir . "/" . "TQLinuxInputfile.csv";
$Vmware_DBFile = $currDir . "/" . "TQVMWareInputfile.csv";
### calling preconnect DB function here
preConnectDB();

## Update DB tables by passing table name and table data file
updateDBTables("epe_dtcc.tq_healthcheck_datas", $Linux_DBFile);  ## this line will be deleted after changing portal code
updateDBTables("epe_dtcc.tq_linux_healthcheck_datas", $Linux_DBFile);
updateDBTables("epe_dtcc.tq_vmware_healthcheck_datas", $Vmware_DBFile);


exit 0;



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
	$dbh->{mysql_auto_reconnect} = 1;
	return;
}

################################################################################
# ##############################################################################
# Update DB tables with respective data
# ##############################################################################
################################################################################
sub updateDBTables(@) {
	$TableName = shift;
	$IPFile = shift;

# ########## Connecting to Database Server Here
					  
	#print "\n####################################################################################\n\nNow, Started Working on updating Database Tables \n";
	
	##Step 1.
	$truncateCommand = "truncate table  epe_dtcc.tq_healthcheck_temp_datas";
	$sth = $dbh->prepare($truncateCommand) || die "truncate temp table prepare: $truncateCommand: $DBI::errstr"; 
	$sth->execute || die "Truncate temp table execute: $truncateCommand: $DBI::errstr"; 

	#step 2# Updating TQ health data
	$loadCommand = "LOAD DATA LOCAL INFILE \'$IPFile\' REPLACE INTO TABLE epe_dtcc.tq_healthcheck_temp_datas \
					FIELDS TERMINATED BY \'\,\' \
					ENCLOSED BY \'\"\' \
					LINES TERMINATED BY \'\\r\\n\'";

	
	$sth = $dbh->prepare($loadCommand) || die "DNS Update prepare: $loadCommand: $DBI::errstr"; 
	$sth->execute || die "DNS Update execute: $loadCommand: $DBI::errstr"; 
	
	#step 3# Updating TQ Health check data
	#$updateCommand = "INSERT INTO epe_dtcc.tq_healthcheck_datas (System_ID,Server_Name,epic_Time) \
	#				SELECT System_ID,Server_Name,epic_Time FROM epe_dtcc.tq_healthcheck_temp_datas \
	#				ON DUPLICATE KEY UPDATE epic_Time = VALUES(epic_Time), System_ID = VALUES(System_ID)";
	$updateCommand = "INSERT INTO ${TableName} (System_ID,Server_Name,epic_Time) \
					SELECT System_ID,Server_Name,epic_Time FROM epe_dtcc.tq_healthcheck_temp_datas \
					ON DUPLICATE KEY UPDATE epic_Time = VALUES(epic_Time), System_ID = VALUES(System_ID), Portal_Updated_Date = CURRENT_TIMESTAMP";
	
	#print ($updateCommand);
	$sth = $dbh->prepare($updateCommand) || die "TQ Health Check Update prepare: $updateCommand: $DBI::errstr"; 
	$sth->execute || die "TQ Healtch Check Update execute: $updateCommand: $DBI::errstr"; 
	
	
	$dbh->disconnect();
	return;
}

