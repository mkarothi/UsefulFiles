#******************************************************************************************************
#**************This library collect the path argument and verifies did the file contains enough data***********
#******************************************************************************************************
import os
import pandas as pd
import subprocess
import lib.Minutes_Calc as mc
def file_validator_call(file, kcrit, interval):
			if interval == 1:
				kcrit = kcrit
			elif interval == 5:
				kcrit = kcrit/5
			else:
				kcrit = 1
			total_lines =  sum(1 for line in open(file))
			
			if total_lines < ((kcrit*2)+2):
				
				return(str(total_lines-1))
def time_validator_call(file, data_dir, server, metrics):
			df = pd.read_csv(file,usecols=[2])
			if df.empty:
				return("DNA")
			else:
				interval = df.loc[:0, 'Interval'].values[0]
				interval = interval / 60
				df1 = pd.read_csv(file)
				#print(metrics)
				#print(data_dir)
				if metrics in ['diskbusy']:
					
					
					df1 = pd.read_csv(file, skipinitialspace=True, usecols=[4])
					resources=len(df1.Resource.unique())
					#print("analyzing Disk busy")
					#print(resources)
					execute_mc = mc.Get_Minutes_Resources(file, data_dir, server, metrics, int(interval), int(resources))
				elif metrics == 'diskresponse':
					#print('good')
					return(int(interval))
				else:
					execute_mc = mc.Get_Minutes(file, data_dir, server, metrics, int(interval))
				
				return(int(interval))

#interval=time_validator_call('C:/project/TQClient/TQFiles/TQ_DATA_1537792295157/sawasq05/CPU_Busy.csv', '15')
#print(interval)
