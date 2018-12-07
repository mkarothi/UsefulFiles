#!/usr/bin/perl -w
use DBI;
use DateTime;
use Cwd;


$currEpocTime = time;
$twelveHrsBackTime = $currEpocTime - 43200;
$sixtyDaysBackTime = $currEpocTime - 5184000;

#$Query = "Select Server_Name, FROM_UNIXTIME(epic_Time), ((${currEpocTime} - epic_Time ) / 3600) From epe_dtcc.tq_linux_healthcheck_datas where epic_time > ${sixtyDaysBackTime} and epic_time < ${twelveHrsBackTime}";


### Functions used in this scripts.

### program specific functions
sub preConnectDB();
sub updateDBTables(@);

### Calling Functions here
preConnectDB();
updateDBTables("epe_dtcc.tq_linux_healthcheck_datas", "epe_dtcc.tq_os_exception_datas");
updateDBTables("epe_dtcc.tq_vmware_healthcheck_datas", "epe_dtcc.tq_vmware_exception_datas");

$dbh->disconnect();
print "Done";
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
	$FromTableName = shift;
	$ToTableName = shift;

# ########## Connecting to Database Server Here
					  
	#print "\n####################################################################################\n\nNow, Started Working on updating Database Tables \n";
	
	##Step 1.
	$truncateCommand = "truncate table  ${ToTableName}";
	$sth = $dbh->prepare($truncateCommand) || die "truncate temp table prepare: $truncateCommand: $DBI::errstr"; 
	$sth->execute || die "Truncate temp table execute: $truncateCommand: $DBI::errstr"; 
	
	#$loadCommand = "INSERT INTO ${ToTableName} (Server_Name, TQ_Last_Collection_Time, Hrs_Since_Last_Collection) Select Server_Name, FROM_UNIXTIME(epic_Time), ((${currEpocTime} - epic_Time ) / 3600) From ${FromTableName} where epic_time > ${sixtyDaysBackTime} and epic_time < ${twelveHrsBackTime} and Server_Name IN (select Server_Name from  epe_dtcc.tq_linux_healthcheck_datas) and Server_Name NOT IN ( 'SAARDA01')";

	#step 2# Updating TQ health data
	$loadCommand = "INSERT INTO ${ToTableName} (Server_Name, TQ_Last_Collection_Time_CT, Time_Since_Last_Collection) Select Server_Name, FROM_UNIXTIME(epic_Time), CONCAT( FLOOR(TIME_FORMAT(SEC_TO_TIME(${currEpocTime} - epic_Time), '%H') / 24), ' Days , ', MOD(TIME_FORMAT(SEC_TO_TIME(${currEpocTime} - epic_Time), ' %H'), 24), ' Hrs , ',TIME_FORMAT(SEC_TO_TIME(${currEpocTime} - epic_Time), '%i'), '  Mins ' ) From ${FromTableName} where epic_time > ${sixtyDaysBackTime} and epic_time < ${twelveHrsBackTime} and Server_Name IN (select Server_Name from  epe_dtcc.tq_linux_healthcheck_datas) and Server_Name NOT IN ( 'SAARDA01','SAARDD01','SABLDD0001','SACASP01','sagemq10','sagemq11','sagemq12','sagemq13','sagemq14','sagemq15','sagemq16','sagemq17','samqmp0002','samqmp0003','samqmp0004','samqmp0006','samqmp0008','samqmp0009','samqmp0010','samqmp0011','samqmp0012','snmqmp12','snorap16','snorap24','swgemp10','swgemp11','swgemp12','swgemp13','swgemp14','swgemq0006','swgemq0007','swgemq0008','swmqmd03','swmqmq0029','swmqmq0031','swmqmq26','swtmtd01','swtmtd02','SWVCDQ01','SWVSSOQ01','SXEGWP02','SXEHTP03','SABGPD01','sagemp0009','sagemp0010','sagemp0011','sagemp10','sagemp11','sagemp12','sagemp13','sagemp14','sgispp0024','sgispp0025','sgispp0026','sgmqmp0003','swgemp0012','swgemp0013','swgemp0014','sxgemp0015','sxgemp0016','sxgemp0017','sxgemp10','sxgemp11','sxgemp12','sxgemp13','sxgemp14','swwaxq0066','swwaxq0067','swwaxq0068','swwaxq0060','sawaxu0094','swwaxq0069','swwaxd0070','swwaxd0071','sawaxu0093','WN74726')";
	
	#print "$loadCommand \n";
	
	
	# $loadCommand = "LOAD DATA LOCAL INFILE \'$IPFile\' REPLACE INTO TABLE epe_dtcc.tq_healthcheck_temp_datas \
					# FIELDS TERMINATED BY \'\,\' \
					# ENCLOSED BY \'\"\' \
					# LINES TERMINATED BY \'\\r\\n\'";

	
	$sth = $dbh->prepare($loadCommand) || die "Insert prepare: $loadCommand: $DBI::errstr"; 
	$sth->execute || die "Insert execute: $loadCommand: $DBI::errstr"; 
	
	#step 3# Updating TQ Health check data
	#$updateCommand = "INSERT INTO epe_dtcc.tq_healthcheck_datas (System_ID,Server_Name,epic_Time) \
	# #				SELECT System_ID,Server_Name,epic_Time FROM epe_dtcc.tq_healthcheck_temp_datas \
	# #				ON DUPLICATE KEY UPDATE epic_Time = VALUES(epic_Time), System_ID = VALUES(System_ID)";
	# $updateCommand = "INSERT INTO ${TableName} (System_ID,Server_Name,epic_Time) \
					# SELECT System_ID,Server_Name,epic_Time FROM epe_dtcc.tq_healthcheck_temp_datas \
					# ON DUPLICATE KEY UPDATE epic_Time = VALUES(epic_Time), System_ID = VALUES(System_ID), Portal_Updated_Date = CURRENT_TIMESTAMP";
	
	#print ($updateCommand);
	#$sth = $dbh->prepare($updateCommand) || die "TQ Health Check Update prepare: $updateCommand: $DBI::errstr"; 
	#$sth->execute || die "TQ Healtch Check Update execute: $updateCommand: $DBI::errstr"; 
	
	
	#$dbh->disconnect();
	return;
}

