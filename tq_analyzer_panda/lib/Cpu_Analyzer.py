import pandas as pd
import os
import configparser as cf
import logging
import lib.File_Validator as FV
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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

path=str('C:\project\TQClient\TQFiles\TQ_DATA_1530894769048')
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

def cpu_analyzer_call(server, path, k, Queue, Percentage, status):
	#variable declaration inside function

	counter=0
	high_index=[]
	index=[]
	global df1
	df1=df1.iloc[0:0]
	df = pd.read_csv(path + '/' + server + '/CPU_Busy.csv')
	df['Date-Time']=df['Time:Date']+' '+df['Time:Time']
	df.drop(['Time:Time', 'Time:Date'], axis=1, inplace=True)
	df['Date-Time'] = pd.to_datetime(df['Date-Time'], format='%m/%d/%Y %I:%M:%S %p')
	
	df1 = pd.read_csv(path + '/' + server + '/Kernel.csv')
	df1['Date-Time']=df1['Time:Date']+' '+df1['Time:Time']
	df1.drop(['Time:Time', 'Time:Date'], axis=1, inplace=True)
	df1['Date-Time'] = pd.to_datetime(df1['Date-Time'], format='%m/%d/%Y %I:%M:%S %p')
	
	result = pd.merge(df,df1[['Date-Time', 'cpuq-sz']],on='Date-Time')
	
	####Defining Plot Variables ########################################
	Title = server.upper() + '-' + 'Percent CPU UTILIZATION & CPU QUEUE'
	chart_path = path +'/' + 'Charts' + '/' + server + '-cpu_util.png'
	
	result.drop(['System', 'Interval'], axis=1, inplace=True)
	
	fig, ax1 = plt.subplots(figsize=(1366/96,768/96))
	xfmt = mdates.DateFormatter('%m/%d/%Y %I:%M:%S %p')
	ax1.xaxis.set_major_formatter(xfmt)
	ax1.plot(result['Date-Time'], result['%busy'], 'b-')
	ax1.set_xlabel('TIME')
	# Make the y-axis label, ticks and tick labels match the line color.
	ax1.set_ylabel('%busy', color='b', fontsize=17)
	#ax1.set_xticks('%busy', result['date time'], rotation='vertical')
	plt.xticks(rotation=90)
	ax1.tick_params('%busy', colors='b')

	ax2 = ax1.twinx()

	#s2 = np.sin(2 * np.pi * t)
	ax2.plot(result['Date-Time'], result['cpuq-sz'], 'g-')
	ax2.set_ylabel('cpuq-sz', color='g', fontsize=17)
	#ax2.tick_params('cpuq-sz', colors='r')
	ax1.set_title(Title, fontsize=22, color='r')
	#plt.xticks('time', df['date time'], rotations='vertical')
	plt.gcf().autofmt_xdate()

	#fig.tight_layout()
	#plt.show()
	plt.savefig(chart_path, dpi=96)
	plt.close()
	##################################################################
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
		output= path + '/' + 'CPU/' + server + '-' + status + '-cpu.csv'
		df1.to_csv(output, index=False, sep=',')
		#print(df1.head())
		
	else:
		df1=df1.iloc[0:0]

def cpu_analyzer(server, path, interval1):
	log.info('Call the CPU analyzer, server %s, path %s, Kcrit %s, Queue_crit %s, Percentage_crit %s, interval %d' %(server, path, kcrit, Queue_crit, Percentage_crit, interval1))
	
	#print(" I am in cpu_analyzer")
	
	if ( interval1 == 1 ):
		kcr = int(kcrit)
		#print(" I am in kcr = kcrit, interval = %d", interval1)
	elif ( int(interval1) == 5 ):
		kcr = int(kcrit/interval1)
		#print(" I am in kcr = kcrit/interval1")
	elif ( interval1 > 5 ):
		kcr = 1
		#print(" I am in kcr = 1")
	if ( interval1 == 1 ):
		kwr = int(kwarn)
		#print(" I am in kwr = kwarn")
	elif ( interval1 == 5 ):
		kwr = int(kwarn/interval1)
		#print(" I am in kwr = kwarn/interval1")
	elif ( interval1 > 5 ):
		kwr = 1
		#print(" I am in kwr = 1")
	status='crit'
	cpu_analyzer_call(server, path, kcr, Queue_crit, Percentage_crit, status)
	
	log.info('call cpu_analyzer_call with server %s, path %s, kcrit %d, Queue_crit %d, Percentage_crit %d' %(server, path, kcr, Queue_crit, Percentage_crit))
	
	
	
	
	
	if not df1.empty:
		status='warn'
		cpu_analyzer_call(server, path, kwr, Queue_warn, Percentage_warn, status)
		return "CRITICAL"
		
	elif df1.empty:
		status='warn'
		cpu_analyzer_call(server, path, kwr, Queue_warn, Percentage_warn, status)
		
		if not df1.empty:
			return "WARN"
		else:
			return "OK"
def cpu_analyze(server, path):
	#Validate Data interval for each input file, here the input files are CPU_Busy.csv and Kernel.csv
	
	log.info('Started for analyzing server %s in path %s' %(server, path))
	file1=path + '/' + server + '/CPU_Busy.csv'
	file2=path + '/' + server + '/Kernel.csv'
	
	Time_validate1 = FV.time_validator_call(file1, path, server, 'cpu - Busy')
	
	log.info('Validated Time for file %s and the interval is %s' %(file1, Time_validate1))
	
	Time_validate2 = FV.time_validator_call(file2, path, server, 'cpu - Kernel')
	
	log.info('Validated Time for file %s and the interval is %s' %(file2, Time_validate2))
	
	if Time_validate1 is "DNA" or Time_validate2 is "DNA":
		return("DNA")
		
	if Time_validate1!= Time_validate2:
		return('File1 interval not equal to File2')
	
		
	validator1 = FV.file_validator_call(file1, kcrit, Time_validate1)
	
	log.info('Validated data in file %s and the result is %s' %(file1, validator1))
	
	validator2 = FV.file_validator_call(file2, kcrit, Time_validate2)
	
	log.info('Validated data in file %s and the result is %s' %(file2, validator2))
	
	if validator1 is not None:
		log.info('NED %s' %(validator1))
		return('NED #' + validator1)
		
	if validator2 is not None:
		log.info('NED %s' %(validator2))
		return('NED #' + validator2)
	
	value=cpu_analyzer(server, path, Time_validate1)
	return (value)
#result = cpu_analyze(server, path)
#print(result)
	