#!/usr/bin/python
import re
import datetime
import pytz
import sys
import glob
import pandas as pd
#dir="C:/project/Dev/GIT-TQ-LOCAL/TQClient/TQFiles/TQ_DATA_GCA_10202018-100000_10202018-140000"
#data_dir=str(sys.argv[1])
def Get_Minutes(data_file, data_dir, server, metrics, interval):
		file= data_dir + "/test_time.txt"
		#print(file)
		zone_in=pytz.timezone('US/Eastern')
		target_zone = pytz.timezone('UTC')

		num_lines = sum(1 for line in open(file))

		with open (file, "r") as f:
			for i in range(4):
				content=f.readline()
				if re.match(r'^start', content):
					starttime = re.findall(r'(\d+:\d+)', content)
					starttime = starttime[0]
					#print(starttime)
				elif re.match(r'^end', content):
					endtime = re.findall(r'(\d+:\d+)', content)
					endtime = endtime[0]
					#print(endtime)
		
		start = datetime.datetime.strptime(starttime, '%m%d%Y:%H%M%S')
		start_est = zone_in.localize(start)
		start_utc = start_est.astimezone(target_zone)
		#print(start_utc)
		end = datetime.datetime.strptime(endtime, '%m%d%Y:%H%M%S')
		end_est = zone_in.localize(end)
		end_utc = end_est.astimezone(target_zone)
		#print(end_utc)
		One_Minutes_sample = int((end_utc - start_utc) / datetime.timedelta(minutes=1)) + 1
		#print(One_Minutes_sample)
		
		#For 5 minute sample
		rem = datetime.timedelta(minutes=start_utc.minute % 5)
		if rem != "0:00:00":
			start_utc += datetime.timedelta(minutes=5)
			#print(start_utc)
			start_utc -= datetime.timedelta(minutes=start_utc.minute % 5,
							seconds=start_utc.second,
							microseconds=start_utc.microsecond)
		#print(start_utc)
		rem = datetime.timedelta(minutes=end_utc.minute % 5)
		if rem != "0:00:00":
			#end_utc += datetime.timedelta(minutes=5)
			#print(end_utc)
			end_utc = end_utc - datetime.timedelta(minutes=end_utc.minute % 5,
							seconds=end_utc.second,
							microseconds=end_utc.microsecond)
		#print(end_utc)				
		Five_Minutes_sample = int((end_utc - start_utc) / datetime.timedelta(minutes=5)) + 1
		#print(Five_Minutes_sample)
		
		
		
		df = pd.read_csv(data_file)
		if interval == 1:
			#percent_data_accuracy = (One_Minutes_sample / df.shape[0])*100
			percent_data_accuracy = (df.shape[0] / One_Minutes_sample)*100
			Write_File(server, data_file, data_dir, metrics, interval, percent_data_accuracy, One_Minutes_sample, df.shape[0])
		
		elif interval == 5:
			#percent_data_accuracy = (Five_Minutes_sample / df.shape[0])*100
			percent_data_accuracy = (df.shape[0] / Five_Minutes_sample)*100
			Write_File(server, data_file, data_dir, metrics, interval, percent_data_accuracy, Five_Minutes_sample, df.shape[0])
		
		else:
			rem = datetime.timedelta(minutes=start_utc.minute % interval)
			if rem != "0:00:00":
				start_utc += datetime.timedelta(minutes=interval)
				start_utc -= datetime.timedelta(minutes=start_utc.minute % interval,
								seconds=start_utc.second,
								microseconds=start_utc.microsecond)
				#print(start_utc)
			rem = datetime.timedelta(minutes=end_utc.minute % interval)
			if rem != "0:00:00":
				#end_utc -= datetime.timedelta(minutes=interval)
				
				end_utc = end_utc - datetime.timedelta(minutes=end_utc.minute % interval,
								seconds=end_utc.second,
								microseconds=end_utc.microsecond)
				#print(end_utc)	
			sample = int((end_utc - start_utc) / datetime.timedelta(minutes=interval)) +1
				#percent_data_accuracy = (sample / df.shape[0])*100
			percent_data_accuracy = (df.shape[0] / sample)*100
			Write_File(server, data_file, data_dir, metrics, interval, percent_data_accuracy, sample, df.shape[0])
'''		
def Write_File(server, data_file, data_dir, metrics, interval, percent_data_accuracy, Num_Minutes, Actual_Sample):	
	data_accuracy_file = data_dir + '/' + 'data_accuracy.csv'
	print(data_dir)
	with open(data_accuracy_file, "a+") as myfile:
		data=server + ',' + data_file + ',' + metrics + ',' + str(interval) + ',' + str(percent_data_accuracy) + ',' + str(Num_Minutes) + '/' + str(Actual_Sample)
		myfile.write(data)
		myfile.write("\n")
'''

def Get_Minutes_Resources(data_file, data_dir, server, metrics, interval, resource):
		file= data_dir + "/test_time.txt"
		#print(file)
		zone_in=pytz.timezone('US/Eastern')
		target_zone = pytz.timezone('UTC')

		num_lines = sum(1 for line in open(file))

		with open (file, "r") as f:
			for i in range(4):
				content=f.readline()
				if re.match(r'^start', content):
					starttime = re.findall(r'(\d+:\d+)', content)
					starttime = starttime[0]
					#print(starttime)
				elif re.match(r'^end', content):
					endtime = re.findall(r'(\d+:\d+)', content)
					endtime = endtime[0]
					#print(endtime)
		
		start = datetime.datetime.strptime(starttime, '%m%d%Y:%H%M%S')
		start_est = zone_in.localize(start)
		start_utc = start_est.astimezone(target_zone)
		#print(start_utc)
		end = datetime.datetime.strptime(endtime, '%m%d%Y:%H%M%S')
		end_est = zone_in.localize(end)
		end_utc = end_est.astimezone(target_zone)
		#print(end_utc)
		One_Minutes_sample = (int((end_utc - start_utc) / datetime.timedelta(minutes=1))*resource) + resource
		#print(One_Minutes_sample)
		
		#For 5 minute sample
		rem = datetime.timedelta(minutes=start_utc.minute % 5)
		if rem != "0:00:00":
			start_utc += datetime.timedelta(minutes=5)
			start_utc -= datetime.timedelta(minutes=start_utc.minute % 5,
							seconds=start_utc.second,
							microseconds=start_utc.microsecond)
		#print(start_utc)
		rem = datetime.timedelta(minutes=end_utc.minute % 5)
		if rem != "0:00:00":
			#end_utc -= datetime.timedelta(minutes=5)
			end_utc = end_utc - datetime.timedelta(minutes=end_utc.minute % 5,
							seconds=end_utc.second,
							microseconds=end_utc.microsecond)
		#print(end_utc)				
		Five_Minutes_sample = (int((end_utc - start_utc) / datetime.timedelta(minutes=5))*resource) + resource
		#print(Five_Minutes_sample)
		
		
		df = pd.read_csv(data_file)
		if interval == 1:
			#percent_data_accuracy = (One_Minutes_sample / df.shape[0])*100
			percent_data_accuracy = (df.shape[0] / One_Minutes_sample)*100
			Write_File(server, data_file, data_dir, metrics, interval, percent_data_accuracy, One_Minutes_sample, df.shape[0])
		
		elif interval == 5:
			#percent_data_accuracy = (Five_Minutes_sample / df.shape[0])*100
			percent_data_accuracy = (df.shape[0] / Five_Minutes_sample)*100
			Write_File(server, data_file, data_dir, metrics, interval, percent_data_accuracy, Five_Minutes_sample, df.shape[0])
		
		else:
			rem = datetime.timedelta(minutes=start_utc.minute % interval)
			if rem != "0:00:00":
				start_utc += datetime.timedelta(minutes=interval)
				start_utc -= datetime.timedelta(minutes=start_utc.minute % interval,
								seconds=start_utc.second,
								microseconds=start_utc.microsecond)
				#print(start_utc)
			rem = datetime.timedelta(minutes=end_utc.minute % interval)
			if rem != "0:00:00":
				#end_utc += datetime.timedelta(minutes=interval)
				end_utc = end_utc - datetime.timedelta(minutes=end_utc.minute % interval,
								seconds=end_utc.second,
								microseconds=end_utc.microsecond)
				#print(end_utc)	
			sample = (int((end_utc - start_utc) / datetime.timedelta(minutes=interval))*resource) + resource
				#percent_data_accuracy = (sample / df.shape[0])*100
			percent_data_accuracy = (df.shape[0] / sample)*100
			Write_File(server, data_file, data_dir, metrics, interval, percent_data_accuracy, sample, df.shape[0])
		
def Write_File(server, data_file, data_dir, metrics, interval, percent_data_accuracy, Num_Minutes, Actual_Sample):	
	data_accuracy_file = data_dir + '/' + 'data_accuracy.csv'
	#print(data_dir)
	with open(data_accuracy_file, "a+") as myfile:
		data=server + ',' + data_file + ',' + metrics + ',' + str(interval) + ',' + str(percent_data_accuracy) + ',' + str(Num_Minutes) + '/' + str(Actual_Sample)
		myfile.write(data)
		myfile.write("\n")

#Get_Minutes(file, data_dir, server, interval)
#ef data_accuracy(file, tot_minutes):
#		df = pd.read_csv(file, usecols=[2])
			
		
