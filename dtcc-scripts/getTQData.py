import cx_Oracle
import os
import subprocess

username = 'skarothi'
password = 'Sadguru786!'
databaseName = "saorap71.dtcc.com:5002/tmqwdp"


currDir = os.getcwd()
os.chdir(currDir)

LinuxdbFile = 'TQLinuxInputfile.csv'
if os.path.isfile('currDir/LinuxdbFile') and os.access('currDir/LinuxdbFile', os.R_OK):
	os.remove('dbFile')

## Opening the DB file as a normal file
Linux = open(LinuxdbFile,'w')

VMWaredbFile = 'TQVMWareInputfile.csv'
if os.path.isfile('currDir/VMWaredbFile') and os.access('currDir/VMWaredbFile', os.R_OK):
	os.remove('dbFile')

## Opening the DB file as a normal file
VMWare = open(VMWaredbFile,'w')



def printf (format,*args):
	sys.stdout.write (format % args)

def printException (exception):
	error, = exception.args
	printf ("Error code = %s\n",error.code);
	printf ("Error message = %s\n",error.message);

try:
	connection = cx_Oracle.connect (username,password,databaseName)
except exception:
	printf ('Failed to connect to %s\n',databaseName)
	printException (exception)
	exit (1)

cursor = connection.cursor ()

#### getting Linux TQ healtch check Data
try:
	cursor.execute ('select max("SystemID"),"System",max("Time") from TQ_NATIVEOS2_OPERATOR.CPUSUM where  "Time" >   (select max("Time") - 7500 from TQ_NATIVEOS2_OPERATOR.CPUSUM ) group by "System"')
except exception:
	printf ('Failed to select from TQ_NATIVEOS2_OPERATOR.CPUSUM\n')
	printException (exception)
	exit (1)

data = cursor.fetchall ()

for row in data :
	Linux.write(str(row[0]))
	Linux.write(',')
	#Linux.write(row[1])
	fullName = str(row[1])
	fqdnArray = fullName.split('.')
	Linux.write(fqdnArray[0])
	Linux.write(',')
	Linux.write(str(row[2]))
	Linux.write('\n')

	
#### getting VMWare ESX Servers TQ healtch check Data
try:
	cursor.execute ('select max("SystemID"),"System",max("Time") from TQ_VMWARE_OPERATOR.CPUVMSUM where  "Time" >   (select max("Time") - 7500 from TQ_VMWARE_OPERATOR.CPUVMSUM ) group by "System"')
except exception:
	printf ('Failed to select from TQ_VMWARE_OPERATOR.CPUVMSUM\n')
	printException (exception)
	exit (1)

data = cursor.fetchall ()

for row in data :
	VMWare.write(str(row[0]))
	VMWare.write(',')
	#VMWare.write(row[1])
	fullName = str(row[1])
	fqdnArray = fullName.split('.')
	VMWare.write(fqdnArray[0])
	VMWare.write(',')
	VMWare.write(str(row[2]))
	VMWare.write('\n')


#### getting VMWare VM Servers TQ healtch check Data
try:
	cursor.execute ('select max("SystemID"),"Virtual_Machine",max("Time") from TQ_VMWARE_OPERATOR.CPUBYVM where  "Time" >   (select max("Time") - 7500 from TQ_VMWARE_OPERATOR.CPUBYVM ) group by "Virtual_Machine"')
except exception:
	printf ('Failed to select from TQ_VMWARE_OPERATOR.CPUBYVM\n')
	printException (exception)
	exit (1)

data = cursor.fetchall ()

for row in data :
	VMWare.write(str(row[0]))
	VMWare.write(',')
	#VMWare.write(row[1])
	fullName = str(row[1])
	fqdnArray = fullName.split('.')
	VMWare.write(fqdnArray[0])
	VMWare.write(',')
	VMWare.write(str(row[2]))
	VMWare.write('\n')

	
#print("Done")	
cursor.close ()
connection.close ()

Linux.close()
VMWare.close()

#3 Calling perl script to upload data to mysql databaseName
#subprocess.call("C:\Perl64\bin\perl.exe" , "updateTQTable.pl")
retcode = subprocess.call(["C:/Perl64/bin/perl.exe" , "C:/Portal-Scripts/TQHealthCheck/updateTQTable.pl", currDir])
if retcode == 0:
    print("Successfully Updated TQ Health Check Data!")
else:
    print("Failed in Updating TQ Health Check Data!!")

### Executing Script to update Exception Tables.
retcode = subprocess.call(["C:/Perl64/bin/perl.exe" , "C:/Portal-Scripts/TQHealthCheck/updateTQExceptionTables.pl", currDir])
if retcode == 0:
    print("Successfully Updated TQ Exception table Data!")
else:
    print("Failed in Updating TQ Exception table Data!!")

exit (0)
