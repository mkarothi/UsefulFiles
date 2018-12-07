################################################################################
#                   Confidential
#   Disclosure And Distribution Solely to Employees of
#   DTCC and Its Affiliates Having a Need to Know
#
#   Copyright (c) 2018 DTCC Inc,
#               All Rights Reserved
################################################################################
##      FILE:    ParityCheck.py
##
##      AUTHOR:  Satya Karothi
##
##      DATE:    10/2018
##
##      PURPOSE: This script process the Server details from SNOW ,
##				 Takes the Server OS, DB and MW versions data and for each SYS ID it provides whether
##				 QA versions match with PROD versions.
##               Script generates desired output for management team.
##
##      INPUT   FILES:	SNowInputFile.xlsx and SYSIDs as input
##		OUTPUT  FILES:	ParityOutput.xlsx
##
##      CODE REVIEW INFO:
##         Date      	Actions
##	 	11/08/2018		Intial Version of the Script
##
##      REVISION HISTORY:
##         Date      	Author				Actions
##		11/08/2018   	Satya Karothi		Initial Version 1.0
##
################################################################################

import getopt, sys, os
import pandas as pd
import numpy as np
from pandas import ExcelWriter

def usage():
	print("Script Usage:")
	print("-h OR --help					: To print Help")
	print("-i <input-file>  OR --input-file <input-file>	: To provide input file taken from SNOW")
	print("-o <output-file> OR --output-file <output-file>	: To provide output file name")
	print("-r <report-flag> OR --report-flag <report-flag>	: To provide report flag. report-flag options are 'all','os','db','mw'")
	print("-s <subset-file> OR --subset-file <subset-file>	: To provide subset sysIDs input file")

def readArgs():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:i:r:s:v", ["help", "output-file=", "input-file=", "report-flag=", "subset-file="])
    except getopt.GetoptError as err:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        #print(opt,arg)
        if opt in ('-o', '--output-file'):
            print('Setting output_file = ' , arg)
            global output_file
            output_file = arg
        elif opt in ('-i', '--input-file'):
            print('Setting input_file = ' , arg)
            global input_file
            input_file = arg
        elif opt in ('-r', '--report-flag'):
            print('Setting report_flag = ' , arg)
            global report_flag
            report_flag = arg
        elif opt in ('-s', '--subset-file'):
            print('Setting subset_sysID_file= ' , arg)
            global subset_file
            subset_file = arg
        elif opt in ("-h", "--help"):
            usage()
            sys.exit()
        else:
            assert False, "Un-handled option"

def getSubsetApps(subset_file):
    apps  = open(subset_file).read()
    apps = apps.split('\n')
    return apps


def add_stats(row, di):
	if(di[row[0]+ ' ' +row[1]][0] >= 1 ):
		label = 'Match'
	elif(di[row[0]+ ' ' +row[1]][1] > 0 and di[row[0]+ ' ' +row[1]][2] > 0):
		label = 'Mismatch'
	else:
		label = row[5]
	### Adding code to mark mismatch in case of match and (no prod or no qa) on same OS entry
	if label == 'Match':
		if(di[row[0]+ ' ' +row[1]][1] > 0 or di[row[0]+ ' ' +row[1]][2] > 0):
			label = 'Mismatch'
	return label

def process_data(sub_table):
    data = sub_table.values.tolist()
    for each in data:
        if(each[3] == 0):
            each.append('No Prod')
        if(each[4] == 0):
            each.append('No QA')
        if(each[3]>0 and each[4]>0):
            each.append('Match')

    di = {}
    for each in data:
        di[each[0]+ ' ' + each[1]] = [0,0,0]

    for each in data:
        key = each[0]+ ' ' + each[1]
        if(each[5] == 'Match'):
            di[key][0] +=  1
        if(each[5] == 'No Prod'):
            di[key][1] +=  1
        if(each[5] == 'No QA'):
            di[key][2] +=  1

    data = pd.DataFrame(data, columns=['Application', 'OS', 'Version', 'Prod', 'QA', 'Temp'])
    data['Stats'] = data.apply(lambda row: add_stats(row, di), axis=1)
    df = data.drop('Temp', 1)
    return df

def write_to_file(df,type):
    df1, df2, df3, df4 = df.loc[df['Stats'] == 'Match'], df.loc[df['Stats'] == 'Mismatch'], df.loc[df['Stats'] == 'No Prod'], df.loc[df['Stats'] == 'No QA']
    df1.to_excel(wr,type + ' Apps Match', index = False)
    df2.to_excel(wr,type + ' Apps Mismatch', index = False)
    df3.to_excel(wr,type + ' Apps - No Prod', index = False)
    df4.to_excel(wr,type + ' Apps - No QA', index = False)



##################################### Main Script Starts Here ########################
#### Assigning all Default Values Here ######
input_file = "SNOW-Data-File.xlsx"  ## This is default value and can be over written using input arguements
output_file = "Parity-Check-output.xlsx"  ## This is default value and can be over written using input arguements
report_flag = "all"
subset_file = None

## read arguements and overwrite default variables
readArgs()
print("")
print('Final Parameters are :')
print('Input File  : ', input_file)
print('Output File : ', output_file)
print('Report Flag : ', report_flag)
print('Subset File : ', subset_file)

if os.path.isfile(input_file):
    print("")
else:
    print("Input File :", input_file , "Does not exist, Please verify and re run the script")
    sys.exit(-1)
    print("")

if subset_file != None:
	if os.path.isfile(subset_file):
	    print("")
	else:
	    print("Subset SysID File :", subset_file , "Does not exist, Please verify and re run the script")
	    sys.exit(-1)
	    print("")

if os.path.isfile(output_file):
    try:
        os.remove(output_file)
    except:
        print("Unable to Delete old Output File :", output_file, ", May be it is opened by someone. please verify and close it and then re run the script")
        sys.exit(-1)

### Read Input file and read data into Dataframe
df = pd.read_excel(input_file,sheet_name='Raw Data')
df_subset = df[['Application','Component', 'Environment','Server Operating System','Server OS Version','Database Type','Database Version','Middleware Type','Middleware Version']]
### Get sub table based on input File here
if subset_file is None:
    print("Subset File Not Defined, so Going to consider all Sys IDs in ", input_file , " file")
else:
    print("Subset File Defined and subset Apps are :")
    apps = getSubsetApps(subset_file)
    print(apps)
    df_subset = df[df_subset['Application'].isin(apps)]

columns = df_subset.head(0)  ## Getting top row as header

### Open an Excel file for writing
wr = ExcelWriter(output_file)

##### Writing Raw Data to Output File #################
df_subset.to_excel(wr,'Raw Data', index = False)

##### Writing OS differences here ################
if report_flag in ('all','os'):
    table=pd.pivot_table(df_subset,index=["Application","Server Operating System","Server OS Version"],values=["Component"],columns=["Environment"],aggfunc=[len],fill_value=0,dropna=True).reset_index()
    sub_table = pd.DataFrame(table)
    df = process_data(sub_table)
    write_to_file(df,'OS')

##### Writing DB differences here ################
if report_flag in ('all','db'):
    table=pd.pivot_table(df_subset,index=["Application","Database Type","Database Version"],values=["Component"],columns=["Environment"],aggfunc=[len],fill_value=0,dropna=True).reset_index()
    sub_table = pd.DataFrame(table)
    df = process_data(sub_table)
    write_to_file(df,'DB')

##### Writing MW differences here ################
if report_flag in ('all','mw'):
    table=pd.pivot_table(df_subset,index=["Application","Middleware Type","Middleware Version"],values=["Component"],columns=["Environment"],aggfunc=[len],fill_value=0,dropna=True).reset_index()
    sub_table = pd.DataFrame(table)
    df = process_data(sub_table)
    write_to_file(df,'MW')

### Save Excel file using file handler
wr.save()

print("Done Processing Data, Please check Output File : ", output_file)
sys.exit()
