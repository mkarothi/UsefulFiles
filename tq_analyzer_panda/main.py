###############################################################################################################################
#                   Confidential
#   Disclosure And Distribution Solely to Employees of
#   DTCC and Its Affiliates Having a Need to Know
#
#   Copyright (c) 2018 DTCC Inc,
#               All Rights Reserved
#################################################################################################################################
##		TOOL Name: Teamquest Automatino Analyzer
##		
##      FILE:    main.py
##
##      AUTHOR:  Rafiq Shaikh
##
##      DATE:    08/24/2018
##		 
##      PURPOSE: This main.py was developed to analyze the teamquest data supplied as input to it.
##				 It reads the file placed on the input argument path
##				 Example input argument C:\EPE_ExtractionFiles\TQExtraction\TQ_DATA_GTR_10182018-100000_10182018-150000
##				 It analyze all the metrics based on the threshold defined in config.ini
##               It generates the output in file Infrastrucure_analysis.xlsx
##				 The output file indicates the server and metrics that was critical
##      
##
##		INPUT:	Path where TQ data was placed, example 	"C:\EPE_ExtractionFiles\TQExtraction\TQ_DATA_GTR_10182018-100000_10182018-150000"
##		OUTPUT  FILES:	Infrastrucure_analysis.xlsx
##		
##		How To Execute It: Execute from the folder path of this main.py file
##			from cmd line run 	"python main.py 	C:\EPE_ExtractionFiles\TQExtraction\TQ_DATA_GTR_10182018-100000_10182018-150000"
##
##
##      CODE REVIEW INFO:
##         Date      	Actions
##	 	10/24/2018		Intial Version of the Script
##
##      REVISION HISTORY:
##         Date      	Author				Actions
##		10/24/2018   	Shaikh Rafiq		Initial Version 1.0
##
##############################################################################################
#		Program Starts Here
#		Import all the necessary External and internal modules 
# 		Here Internal modules refer the module developed for each of the metrics
#		Incase if you want to create a new module, place it in ~/tq_analyzer_panda/lib/
##############################################################################################
import os
import sys
import logging as log
import re
import pandas as pd
from shutil import make_archive as archive
from shutil import rmtree as rmdir
import getpass
import subprocess
###############################################################################################
#	Below are the modules developed for each metrics, Internal modules
###############################################################################################
import lib.Cpu_Analyzer as Cpu_Analyzer
import lib.Memory_Analyzer as Memory_Analyzer
import lib.Disk_Analyzer as Disk_Analyzer
import lib.Disk_Analyzer_Response as Disk_Analyzer_Response
import lib.Swap_Analyzer as Swap_Analyzer
import lib.Report_Format  as RF
################################################################################################


#########################################################################################################
#	Define the Logging Format
#########################################################################################################
log.basicConfig(filename='TQ_Analyzer_Log.log',level=log.DEBUG,format='%(asctime)s {%(pathname)s:%(lineno)d} %(message)s')




#*********************************************************************************************************
#*************Import the configuration from the config.ini file*******************************************
#**************Global Variable Declaration***********************************************************************
#*********************************************************************************************************


#data_dir=str('C:\project\TQClient\TQFiles\TQ_DATA_1530894769048')


#Collect the Directory path that's the first argument from command line and verify, did user entered directory path or not?

try:
	data_dir=str(sys.argv[1])
except IndexError:
	print ("You missed directory path, that needs to be passed as arguments")
	print ("Example:  python main.py C:\project\TQClient\TQFiles\TQ_DATA_1530894769048")
	print ("where C:\project\TQClient\TQFiles\TQ_DATA_1530894769048 is the directory which contains data that needs to be analyzed")
	sys.exit(1)
except:
	raise
	sys.exit(1)
else:
	log.info('TQ Analyzer Started Analyzing the data from path %s' %data_dir)
	
	
#CPU related output evidence will be placed in the CPU_dir directory
CPU_dir=data_dir + '/CPU'
#Memory related output evidence will be placed in the Mem_dir directory
Mem_dir=data_dir + '/Memory'
#Swap related output evidence will be placed in the Swap_dir directory
Swap_dir=data_dir + '/Swap'
#Disk related output evidence will be placed in the Disk_dir directory
Disk_dir=data_dir + '/Disk'
#Disk response related evidence will be placed in the Disk_resp directory
Disk_resp_dir=data_dir + '/Disk_Response'
####Charts dir
Charts=data_dir + '/Charts'
#End report will be saved in the file Output, where  Output is a variable
Output=data_dir + '/Report.csv'

#List which contains all the metrics directory
Metrics_path=[CPU_dir, Mem_dir, Swap_dir, Disk_dir, Disk_resp_dir, Charts]
#print(Metrics_path)

#Verify Each directory it didn't exist, if exist, remove the directory

for i in Metrics_path:
	if os.path.exists(i):
		log.info('Already directory %s exist, so remove it' %i)
		try:
			rmdir(i)
		except:
			log.exception('Unable to remove directory %s' %i)
		else:
			log.info('Directory %s deleted' %i)


		
#***********list the directory and get the server names********************************************		
log.info('listout the directory in %s and capture each of the server name folder in a list called servers' %data_dir)	
servers=[d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
log.info('servers found in %s are %s' %(data_dir, servers))	


#Design the Report template in Pandas dataframe, Modify it based on your needs

Report=pd.DataFrame(columns=['Servers', 'CPU_Util and CPU Queue', 'Disk_Util and Disk_Queue',\
'Disk_Response', 'Memory_Util', 'Swap'])

#Add the server names into the report
se_servers = pd.Series(servers)
Report['Servers'] = se_servers


#***************Function define for Report Generation
def report(server, col_name, value):
	log.info('Update the report  based on server %s and based on the metrics column %s  and assign the value %s' %(server, col_name, value))
	Report.loc[Report.Servers == server, col_name] = value

#***************function to call cpu_analyzer to analyze the data
def cpu(servers, path):
	log.info('Start the CPU Analyzer for servers %s' %servers)
	for server in servers:
		log.info('Analyze the CPU for server %s' %server)
		cpufile = path + '/' + server + '/' + 'CPU_Busy.csv'
		kernelfile = path + '/' + server + '/' + 'Kernel.csv'
		if os.path.isfile(cpufile):
			log.info('File exist %s' %cpufile)
			if os.path.isfile(kernelfile):
				log.info('File exist %s' %kernelfile)
				log.info('call the CPU analyzer with server %s and path %s' %(server, path))
				result = Cpu_Analyzer.cpu_analyze(server, path)
				log.info('Result captured - status is - %s' %result)
				report(server, 'CPU_Util and CPU Queue', result)
				log.info('status added into report')
			else:
				log.info('File not found - %s' %kernelfile)
				report(server, 'CPU_Util and CPU Queue', 'FNA')
			
		else:
			log.info('File not found - %s' %cpufile)
			report(server, 'CPU_Util and CPU Queue', 'FNA')
	dir_empty(CPU_dir)
#****************function to call Memory_Analyzer to analyze the memory data			
def memory(server, path):
	log.info('Start the Memory Analyzer for servers %s' %servers)
	for server in servers:
		log.info('Analyze the Memory for server %s' %server)
		filepath=path + '/' + server + '/' + 'Memory_Util.csv'
		if os.path.isfile(filepath):
			log.info('File exist %s' %filepath)
			log.info('call the memory analyzer with server %s and path %s' %(server, path))
			result = Memory_Analyzer.mem_analyze(server, path)
			log.info('Result captured - status is - %s' %result)
			report(server, 'Memory_Util', result)
			log.info('status added into report')
		else:
			log.info('File not found - %s' %filepath)
			report(server, 'Memory_Util', 'FNA')
	dir_empty(Mem_dir)
#****************function to call Swap_Analyzer to analyze the swap data
def swap(server, path):
	log.info('Start the Swap Analyzer for servers %s' %servers)
	for server in servers:
		log.info('Analyze the Swap for server %s' %server)
		filepath=path + '/' + server + '/' + 'Swap.csv'
		if os.path.isfile(filepath):
			log.info('File exist %s' %filepath)
			log.info('call the swap analyzer with server %s and path %s' %(server, path))
			result=Swap_Analyzer.swap_analyze(server, path)
			log.info('Result captured - status is - %s' %result)
			report(server, 'Swap', result)
			log.info('status added into report')
		else:
			log.info('File not found - %s' %filepath)
			report(server, 'Swap', 'FNA')	
	dir_empty(Swap_dir)
	
#****************function to call Disk_Analyzer to analyze the disk data		
def disk(server, path):
	log.info('Start the Disk Analyzer for servers %s' %servers)
	for server in servers:
		log.info('Analyze the Disk for server %s' %server)
		filepath=path + '/' + server + '/' + 'Disk_Summary.csv'
		if os.path.isfile(filepath):
			log.info('File exist %s' %filepath)
			log.info('call the Disk analyzer with server %s and path %s' %(server, path))
			result = Disk_Analyzer.disk_analyzer_call_resources(server, path)
			log.info('Result captured - status is - %s' %result)
			report(server, 'Disk_Util and Disk_Queue', result)
			log.info('status added into report')
		else:
			log.info('File not found - %s' %filepath)
			report(server, 'Disk_Util and Disk_Queue', 'FNA')	
	dir_empty(Disk_dir)
#****************function to call Disk_Analyzer_Response to analyze the disk response time data		

def disk_response(server, path):
	log.info('Start the Disk Latency Analyzer for servers %s' %servers)
	for server in servers:
		log.info('Analyze the Disk Latency for server %s' %server)
		filepath=path + '/' + server + '/' + 'Disk_Summary.csv'
		if os.path.isfile(filepath):
			log.info('File exist %s' %filepath)
			log.info('call the Disk Latency analyzer with server %s and path %s' %(server, path))
			result = Disk_Analyzer_Response.disk_response_call_resources(server, path)
			log.info('Result captured - status is - %s' %result)
			report(server, 'Disk_Response', result)
			log.info('status added into report')
		else:
			log.info('File not found - %s' %filepath)
			report(server, 'Disk_Util and Disk_Queue', 'FNA')	
	dir_empty(Disk_resp_dir)

#****************Remove the metrics directory which doesn't have critical or warn data

def dir_empty(path):
	servers=[d for d in os.listdir(path) if os.path.isfile(os.path.join(path, d))]
	if len(servers) >0 :
		return
	else:
		os.rmdir(path)
		
##########################################################
#Create the directory to store Each Metrics Evidence
##########################################################
for i in Metrics_path:
	if not os.path.exists(i):
		log.info('Directory %s not found' %i)
		try:
			os.makedirs(i)
		except:
			log.exception('Unable to Create %s' %i)
		else:
			log.info('Directory %s created' %i)

############################################################
##########################################################
#Create file to store accuracy data
#########################################################

try:
	Accuracy_file = data_dir + '/' + 'data_accuracy.csv' 
	Accuracy = open(Accuracy_file, "w")
	line = 'server,' + 'file-name,' + 'metrics,' + 'Interval in min,' + 'data_accuracy in percentage,' + 'Num Of Sample / Actual Sample in File'
	Accuracy.write(line)
	Accuracy.write("\n")
	Accuracy.close()
except:
	log.exception('Error while executing Accurac in main')
else:
	log.info('Accuracy file created with header')

##########################################################
# call the function cpu to analyze the cpu
############################################################
try:
	log.info('Call the function cpu with the servers %s and directory %s' %(servers, data_dir))
	cpu(servers, data_dir)
except:
	log.exception("Exception During Executing CPU Analyzer")
else:
	log.info("CPU analyzer done for server %s" %(servers))



# call the function memory to analyze the memory
try:
	log.info('Call the function memory with the servers %s and directory %s' %(servers, data_dir))
	memory(servers, data_dir)
except:
	log.exception("Exception During Executing Memory Analyzer")
else:
	log.info("Memory analyzer done for server %s" %(servers))
	
	
# call the function disk to analyze the disk
try:
	log.info('Call the function disk with the servers %s and directory %s' %(servers, data_dir))
	disk(servers, data_dir)
except:
	log.exception("Exception During Executing Disk Analyzer")
else:
	log.info("disk analyzer done for server %s" %(servers))
	

# call the function disk response  to analyze the disk response
try:
	log.info('Call the function disk response with the servers %s and directory %s' %(servers, data_dir))
	disk_response(servers, data_dir)
except:
	log.exception("Exception During Executing Disk response Analyzer")
else:
	log.info("disk response analyzer done for server %s" %(servers))
	
	
# call the function swap  to analyze the swap

try:
	log.info('Call the function swap with the servers %s and directory %s' %(servers, data_dir))
	swap(servers, data_dir)
except:
	log.exception("Exception During Executing Swap Analyzer")
else:
	log.info("Swap analyzer done for server %s" %(servers))
	
	
#Generate the End report in the Output directory, here Output is a variable
try:
	log.info('Program going to generate the report')
	Report.to_csv(Output, mode='w', index=False, sep=',')
except:
	log.exception("Exception During genrating the output")
else:
	log.info('Output Generated')
#########################################################################

try:
	RF.formatter(data_dir)
	log.info('Finished  analyzing, report  was placed  on the following path %s' %(data_dir))
	log.info('Finished  analyzing, report  was placed  on the following file %s' %(Output))
	log.info('Getting into ShareDrive')
except:
	log.exception('Error while formatting data')
else:
	log.info('Formatting Done')
#log.info('Current Working Directory %s' %(Working_Dir))
try:
	log.info('%s' %(data_dir))
	zipfilename=re.search(r'C:\\(.*)\\(.*)', (data_dir).replace('/', '\\'))
	log.info('%s' %(zipfilename))
	log.info('re searchg group 0 %s' %(zipfilename.group(0)))
	log.info('re searchg group 1 %s' %(zipfilename.group(1)))
	log.info('re searchg group 2 %s' %(zipfilename.group(2)))
except:
	log.exception("Error occured in the regex")
#print(zipfilename.group(2))


try:
	User_info=getpass.getuser()
	log.info('%s' %(User_info))
	#sharearchive=os.path.join(('G:/').replace('/', '\\'), zipfilename.group(2) + '.zip')
	sharearchive=os.path.join(('C:/jenkins/data/workspace/epe-dev/TQ_Automation_Analyzer/'), zipfilename.group(2)) #+ '.zip')
	print("Archieve File : ", sharearchive)
	log.info('%s' %(sharearchive))
	print("Data Dir: ", data_dir)
	archive(sharearchive, 'zip', data_dir)
	
except:
	log.exception("Exception During Archival")
else:
	log.info("Archieve success file placed in ShareDrive")
print("Finished Analyzing, Report was placed on the following path")
print(Output)



#print(Report)



