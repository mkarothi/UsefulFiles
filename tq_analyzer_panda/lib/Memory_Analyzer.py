import pandas as pd
import os
import logging
import configparser as cf
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


config = { "mem_percentage_crit" : float(con['MEMORY_CRIT']['mem_percentage']),\
 "instances_crit" : int(con['MEMORY_CRIT']['consecutive_intervals']),\
"mem_percentage_warn" : float(con['MEMORY_WARN']['mem_percentage']),\
 "instances_warn" : int(con['MEMORY_WARN']['consecutive_intervals']) }
 
 
 ##GLOBAL VARIABLE DECLARATION##############################

path=str('C:\project\TQClient\TQFiles\TQ_DATA_1530894769048')
server = "sawasq05"
#busy='%busy'
#runq='cpuq-sz'
high={}
kcrit=config["instances_crit"]
Percentage_crit=config["mem_percentage_crit"]
kwarn=config["instances_warn"]
Percentage_warn=config["mem_percentage_warn"]

#Result will be captured in the global variable
df1=pd.DataFrame()

def mem_analyzer_call(server, path, k, Percentage, status):
	#variable declaration inside function
	global df1
	Mempath = path + '/' + server + '/' + 'Memory_Busy.csv'
	log.info('memory  busy will be saved at %s' %Mempath)
	counter=0
	high_index=[]
	index=[]
	df = pd.read_csv(path + '/' + server + '/Memory_Util.csv')
	df["pct_mem_utilization"] = ((df['usedmem'] -df['cachedmem'] -df['buffermem'])/df['totalmem']) *100
	try:
		df.to_csv(Mempath,  columns=["Time:Date", "Time:Time", "Interval", "pct_mem_utilization"])
	except:
		log.exception("Error found during saving the memory busy data")
	df['Date-Time']=df['Time:Date']+' '+df['Time:Time']
	df.drop(['Time:Time', 'Time:Date'], axis=1, inplace=True)
	df['Date-Time'] = pd.to_datetime(df['Date-Time'], format='%m/%d/%Y %I:%M:%S %p')
	
	result = df
     	
	#result["pct_mem_utilization"] = ((result['usedmem'] -result['cachedmem'])/result['totalmem']) *100
	#result["pct_mem_utilization"] = ((result['usedmem'] -result['cachedmem'] -result['buffermem'])/result['totalmem']) *100
	
#	print(result.dtypes)
	#print(result["pct_mem_utilization"])
	total_row = result.shape[0]
	
	####Defining Plot Variables ########################################
	Title = server.upper() + '- ' + 'Percent MEM UTILIZATION'
	chart_path = path +'/' + 'Charts' + '/' + server + '-mem_util.png'
	
	result.drop(['System', 'Interval'], axis=1, inplace=True)
	result.round({'pct_mem_utilization': 1})
	fig, ax1 = plt.subplots(figsize=(1366/96,768/96))
	xfmt = mdates.DateFormatter('%m/%d/%Y %I:%M:%S %p')
	ax1.xaxis.set_major_formatter(xfmt)
	ax1.plot(result['Date-Time'], result['pct_mem_utilization'], 'b-')
	ax1.set_xlabel('TIME')
	# Make the y-axis label, ticks and tick labels match the line color.
	ax1.set_ylabel('%busy', color='b', fontsize=17)
	#ax1.set_xticks('%busy', result['date time'], rotation='vertical')
	plt.xticks(rotation=90)
	ax1.tick_params('%busy', colors='b')
	ax1.set_title(Title, fontsize=22, color='r')
	plt.gcf().autofmt_xdate()

	#fig.tight_layout()
	#plt.show()
	plt.savefig(chart_path, dpi=96)
	plt.close()
	##################################################################
	
	
	for i in range(0, total_row):

		if (result["pct_mem_utilization"].iloc[i] > Percentage):

			counter=counter+1
			high_index.append(i)
		#	print(high_index)
			
		elif (counter >= k):
			fin_index=list(high_index)
			index = index[0:] + fin_index[0:]
			fin_index=[]
			high_index=[]
			counter=0
			
			
		else:
			high_index=[]
			counter=0

		if ( i == total_row-1 ):
		#	print(i, total_row-1)
			if ( counter >= k):
				fin_index = list(high_index)
				index = index[0:] + fin_index[0:]
				fin_index = []
				high_index = []
				counter = 0
				break
			else:
				break
		
	if(len(index) >0):
		
		df1=result.ix[index]
		output= path + '/' + 'Memory/' + server + '-' + status + '-memory.csv'
		df1.to_csv(output, index=False, sep=',')
	else:
		df1=df1.iloc[0:0]


def mem_analyzer(server, path, interval1):
	if  (interval1 == 1 ):
		kcr = int(kcrit)
	elif ( interval1 == 5 ):
		kcr = int(kcrit/interval1)
	elif ( interval1 > 5 ):
		kcr = 1
	if ( interval1 == 1 ):
		kwr = int(kwarn)
	elif ( interval1 == 5 ):
		kwr = int(kwarn/interval1)
	elif ( interval1 > 5 ):
		kwr = 1
	status='crit'
	mem_analyzer_call(server, path, kcr, Percentage_crit, status)
	if not df1.empty:
		status='warn'
		mem_analyzer_call(server, path, kwr, Percentage_warn, status)
		return "CRITICAL"
	elif df1.empty:
		status='warn'
		mem_analyzer_call(server, path, kwr, Percentage_warn, status)
		if not df1.empty:
			return "WARN"
		else:
			return "OK"
def mem_analyze(server, path):
	file = path + '/' + server + '/Memory_Util.csv'
	
	Time_validate1 = FV.time_validator_call(file, path, server, 'memory')
	
	if Time_validate1 is "DNA":
		return("DNA")
	else:
		validator1 = FV.file_validator_call(file, kcrit, Time_validate1)
	
	if validator1 is not None:
		return('NED #' + validator1)
	value=mem_analyzer(server, path, Time_validate1)
	return(value)
#result = mem_analyze(server, path)
#print(result)
	
	