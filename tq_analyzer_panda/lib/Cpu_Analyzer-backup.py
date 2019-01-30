import pandas as pd
import os
import configparser as cf
import logging
#import lib.File_Validator as FV
import File_Validator as FV

#*Call the logger************************
log = logging.getLogger(__name__)

#*******************************************************************
#********************set the properties of config ******************
#*******************************************************************

con =  cf.ConfigParser()

con.read('config.ini')


config = { "cpu_percentage_crit" : float(con['CPU_CRITICAL']['cpu_percentage']),\
 "cpuqueue_crit" : float(con['CPU_CRITICAL']['cpuqueue']), "instances_crit" : int(con['CPU_CRITICAL']['consecutive_intervals']),
 "cpu_percentage_warn" : float(con['CPU_WARN']['cpu_percentage']),\
 "cpuqueue_warn" : float(con['CPU_WARN']['cpuqueue']), "instances_warn" : int(con['CPU_WARN']['consecutive_intervals'])}
 
 
 ##GLOBAL VARIABLE DECLARATION##############################

path=str('C:\project\TQClient\TQFiles\TQ_DATA_1537792295157')
server = "sawasq05"
busy='%busy'
runq='cpuq-sz'
high={}

#warning variable declaration
kwarn=config["instances_warn"]
Queue_warn=config["cpuqueue_warn"]
Percentage_warn=config["cpu_percentage_warn"]

#critical variable declaration
kcrit=config["instances_crit"]
Queue_crit=config["cpuqueue_crit"]
Percentage_crit=config["cpu_percentage_crit"]

#Result will be captured in the global variable
df1=pd.DataFrame()

def cpu_analyzer_call(server, path, k, Queue, Percentage):
	#variable declaration inside function

	counter=0
	high_index=[]
	index=[]
	global df1
	df1=df1.iloc[0:0]
	df = pd.read_csv(path + '/' + server + '/CPU_Busy.csv')
	df['Time:Date']=df['Time:Date']+' '+df['Time:Time']
	df.drop(['Time:Time'], axis=1, inplace=True)
	df['Time:Date'] = pd.to_datetime(df['Time:Date'], format='%m/%d/%Y %I:%M:%S %p')
	
	df1 = pd.read_csv(path + '/' + server + '/Kernel.csv')
	df1['Time:Date']=df1['Time:Date']+' '+df1['Time:Time']
	df1.drop(['Time:Time'], axis=1, inplace=True)
	df1['Time:Date'] = pd.to_datetime(df1['Time:Date'], format='%m/%d/%Y %I:%M:%S %p')
	
	result = pd.merge(df,df1[['Time:Date', 'cpuq-sz']],on='Time:Date')
	
	
	
	total_row = result.shape[0]
	
	
	for i in range(0,total_row):
		
		if ((result[busy].iloc[i] > Percentage) & (result[runq].iloc[i] > Queue)):
			
			counter=counter+1
			high_index.append(i)
			
		elif (counter >= k):
			fin_index = list(high_index)
			index = index[0:] + fin_index[0:]
			fin_index = []
			high_index = []
			counter = 0
		else:
			high_index=[]
			counter=0
		
		if ( i == total_row-1 ):
		
			if ( counter >= k):
				fin_index = list(high_index)
				index = index[0:] + fin_index[0:]
				fin_index = []
				high_index = []
				counter = 0
				break
			else:
				break
		
	if(len(index) > 0):
	
		
		
		df1=result.ix[index]
		output= path + '/' + 'CPU/' + server + '-cpu.csv'
		df1.to_csv(output, index=False, sep=',')
		#print(df1.head())
		
	else:
		df1=df1.iloc[0:0]
'''	
def file_validator_call(file, kcrit):
			total_lines =  sum(1 for line in open(file))
			if total_lines < (kcrit*2):
				return(str(total_lines))
			#print (total_lines)
'''
def cpu_analyze(server, path):
	log.info('Call the CPU analyzer, server %s, path %s, Kcrit %s, Queue_crit %s, Percentage_crit %s, interval1 %d, interval2 %d' %(server, path, kcrit, Queue_crit, Percentage_crit, interval1, interval2))
	
	file1=path + '/' + server + '/CPU_Busy.csv'
	file2=path + '/' + server + '/Kernel.csv'
	kcrit = kcrit
	validator1 = FV.file_validator_call(file1, kcrit)
	validator2 = FV.file_validator_call(file2, kcrit)
	
	#Validate Data interval for each input file, here the input files are CPU_Busy.csv and Kernel.csv
	Time_validate1 = FV.time_validator_call(file1)
	Time_validate2 = FV.time_validator_call(file2)
		
	if validator1 is not None:
		return('DNA #' + validator1)
		
	if validator2 is not None:
		return('DNA #' + validator2)
	
	if file1 is not file2:
		return('File1 interval not equal to File2')
	else: 	
		
		log.info('Call the CPU analyzer, server %s, path %s, Kcrit %s, Queue_crit %s, Percentage_crit %s, interval1 %d, interval2 %d' %(server, path, kcrit, Queue_crit, Percentage_crit, interval1, interval2))
		
		if [interval1 == 1] or [kcrit < 5]:
			cpu_analyzer_call(server, path, kcrit, Queue_crit, Percentage_crit)
		elif [interval == 5]:
			kcrit = kcrit/interval
			cpu_analyzer_call(server, path, kcrit, Queue_crit, Percentage_crit)
	
	if not df1.empty:
		return "CRITICAL"
	
	elif df1.empty:
		if [interval1 == 1] or [kwarn < 5]:
			cpu_analyzer_call(server, path, kwarn, Queue_warn, Percentage_warn)
		elif [interval == 5]:
			kcrit = kcrit/interval
			cpu_analyzer_call(server, path, kwarn, Queue_warn, Percentage_warn)
		
		
		if not df1.empty:
			return "WARN"
		else:
			return "OK"

result = cpu_analyze(server, path)
print(result)
	