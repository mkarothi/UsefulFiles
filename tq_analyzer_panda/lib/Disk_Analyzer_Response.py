import pandas as pd
import os
import configparser as cf
import lib.File_Validator as FV


#*******************************************************************
#********************set the properties of config ******************
#*******************************************************************

con =  cf.ConfigParser()

con.read('config.ini')

config = { "disk_response_crit" : float(con['DISK_RESPONSE_CRIT']['disk_response_time']),\
 "instances_crit" : int(con['DISK_RESPONSE_CRIT']['consecutive_intervals']), \
 "disk_response_warn" : float(con['DISK_RESPONSE_WARN']['disk_response_time']),\
 "instances_warn" : int(con['DISK_RESPONSE_WARN']['consecutive_intervals']) }

'''
config = { "disk_percentage_crit" : float(con['DISK_UTIL_CRIT']['disk_percentage']),\
 "diskqueue_crit" : float(con['DISK_UTIL_CRIT']['diskqueue']), "instances_crit" : int(con['DISK_UTIL_CRIT']['consecutive_intervals']),\
 "disk_percentage_warn" : float(con['DISK_UTIL_WARN']['disk_percentage']),\
 "diskqueue_warn" : float(con['DISK_UTIL_WARN']['diskqueue']), "instances_warn" : int(con['DISK_UTIL_WARN']['consecutive_intervals']) }
'''

 
 
 ##GLOBAL VARIABLE DECLARATION##############################
 
 
path=str('C:\project\TQClient\TQFiles\TQ_DATA_1530894769048')
server = "sworaq0201"
busy='%busy'
runq='cpuq-sz'
high={}

#Critical Declaration

kcrit=config["instances_crit"]
Response_crit=config["disk_response_crit"]

#Warning Declaration

kwarn=config["instances_warn"]
Response_warn=config["disk_response_warn"]

#Result will be captured in the global variable
df2=pd.DataFrame(columns=['Time:Date', 'Interval', 'System', 'Resource', 'avwait', 'avserv', 'avresp'])

fields = ['Time:Date', 'Time:Time', 'Interval', 'System', 'Resource', 'avwait', 'avserv',]

def disk_response_call(server, path, k, Response, df, i, status):
	
	#print(df.head())
	df1 = df.loc[df['Resource'] == i]
	df1 = df1.reset_index()
	df1.rename(columns={'index': 'ORG_INDEX'}, inplace=True)
	df1['avresp'] = df1['avserv'] + df1['avwait']
	total_row = df1.shape[0]
	
	counter = 0
	index=[]
	high_index=[]
	for j in range(0, total_row):
		
		if(df1['avresp'].iloc[j] > Response):
			counter=counter+1
			high_index.append(j)
		else:
			if ( counter >= k):
				fin_index = list(high_index)
				index = index[0:] + fin_index[0:]
				high_index=[]
				fin_index=[]
				counter=0
				continue
			elif ( counter < k ):
				high_index=[]
				counter=0
				continue
	if ( len(index) > 0):
		df1=(df1.ix[index])
		output= path + '/' + 'Disk_Response/' + server + '-' + status + '-disk-response.csv'
		df1.to_csv(output, mode='a', index=False, sep=',')
		return "not"
	else:
		return "ok"
	
def disk_response_call_resource(server, path, interval1):

	global kcrit, Response_crit, kwarn, Response_warn
	#print(kcrit, Response_crit, kwarn, Response_warn)
	critical=[]
	warn=[]
	if ( interval1 == 1 ):
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
		
		
	df = pd.read_csv(path + '/' + server + '/Disk_Summary.csv', skipinitialspace=True, usecols=fields)
	resources=df.Resource.unique()
	for i in resources:
		result=disk_response_call(server, path, kcrit, Response_crit, df, i, 'crit')
		if (result == "not"):
			result=disk_response_call(server, path, kwarn, Response_warn, df, i, 'warn')
			critical.append(i)
		
		else:
			if (result == "ok"):
				result=disk_response_call(server, path, kwarn, Response_warn, df, i, 'warn')
				if (result == "not"):
					warn.append(i)
		
	if (len(critical)>0):
		return "CRITICAL"
		
	elif (len(warn)>0):
		return "WARN"
	else:
		return "OK"
	
def disk_response_call_resources(server, path):
	file = path + '/' + server + '/Disk_Summary.csv'
	
	Time_validate1 = FV.time_validator_call(file, path, server, "diskresponse")
	if Time_validate1 is "DNA":
		return("DNA")
	
	
	validator1 = FV.file_validator_call(file, kcrit, Time_validate1)
	if validator1 is not None:
		return('NED #' + validator1)
	value=disk_response_call_resource(server, path, Time_validate1)
	return(value)
#result=disk_response_call_resources(server, path)			
#print(result)

		
		
	


