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
##      PURPOSE: This script process the Server details File stores in dictionary.
##				 Takes the Server pair as input and returns Y or N based on cpu,memory
##				 checks for those pairs
##               generates desired output for management report.
##
##      INPUT   FILES:	SNowInputFile.xls and server paris as input in Json Format
##		OUTPUT  FILES:	Json Object with results
##
##      CODE REVIEW INFO:
##         Date      	Actions
##	 	10/08/2018		Intial Version of the Script
##
##      REVISION HISTORY:
##         Date      	Author				Actions
##		10/08/2018   	Satya Karothi		Initial Version 1.0
##
################################################################################


##Calling as :  ParityCheck.py {\"compare\": {\"source1\":\"target1\", \"source2\":\"target2\"} }
##Calling as :  ParityCheck.py {\"compare\": {\"ALAPRDB04\":\"ALDEV1BAP02\", \"ALDEV1BDIR01\":\"ALDEV1BDR02\"} }
import getopt, sys, os
import json, sys
import random
import pandas as pd
import numpy as np
from pandas import ExcelWriter
import math

def usage():
	print("Script Usage:")
	print("-h OR --help					: To print Help")
	print("-i <input-file>  OR --input-file <input-file>	: To provide input file that has QA server and PROD server with comma separated")
	print("-o <output-file> OR --output-file <output-file>	: To provide output file name")
	print("-c <config-file> OR --config-file <config-file>	: To provide Configuration file that contains CPU,Memory details.")
	print("-s <snow-file> OR --snow-file <snow-file-name>	: To provide ServiceNow File that contains OS,DB,MW versions")

def readArgs():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:i:c:s:v", ["help", "output-file=", "input-file=", "config-file=", "snow-file="])
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
        elif opt in ('-c', '--config-file'):
            print('Setting config-file = ' , arg)
            global config_file
            config_file = arg
        elif opt in ('-s', '--snow-file'):
            print('Setting snow_file= ' , arg)
            global snow_file
            snow_file = arg
        elif opt in ("-h", "--help"):
            usage()
            sys.exit()
        else:
            assert False, "Un-handled option"

def isNaN(num):
	return num != num

def trimNumber(num):
	if type(num) == str:
		num = num.strip()
		num = num.replace
		('"','')
		num = num.replace(',','')
		num = num.replace(' ','')
	return(float(num))


def compareValues(sID, tID):
	rStatus = "N"
	sSRVName = df['SRVNAME'][sID].lower()
	tSRVName = df['SRVNAME'][tID].lower()

	sCPUNo = trimNumber(df['GBL_NUM_CPU'][sID])
	tCPUNo = trimNumber(df['GBL_NUM_CPU'][tID])
	sMEMNo = trimNumber(df['GBL_MEM_PHYS'][sID])
	tMEMNo = trimNumber(df['GBL_MEM_PHYS'][tID])

	if (sCPUNo == tCPUNo) and (sMEMNo == tMEMNo):
		rStatus = "Y"
	print(sSRVName, sCPUNo, sMEMNo,tSRVName, tCPUNo, tMEMNo)
	return(rStatus)

################################### MAIN #######################
##### Main Program Starts Here #####
INPUT_FileName= 'C:\\My-Scripts\\Parity_Check-Bruce\\InputFile.csv'
EMOS_File = 'MAX_PEAK_FORECAST_REPORT.xlsx'
SNOW_FileName = 'SNOW-Data-File.xlsx'
output_file = "Parity-Check-Output.xlsx"  ## This is default value and can be over written using input arguements
HWArray = []
SWArray =  []

## read arguements and overwrite default variables
readArgs()
print("")
print('Final Parameters are :')
print('Input File  : ', INPUT_FileName)
print('Output File : ', output_file)
print('Config File : ', EMOS_File)
print('ServiceNow File : ', SNOW_FileName)

if os.path.isfile(INPUT_FileName):
    print("")
else:
    print("Input File :", INPUT_FileName , "Does not exist, Please verify and re run the script")
    sys.exit(-1)
    print("")


if os.path.isfile(SNOW_FileName):
    print("")
else:
    print("SNow File :", SNOW_FileName , "Does not exist, Please verify and re run the script")
    sys.exit(-1)
    print("")

if os.path.isfile(EMOS_File):
    print("")
else:
    print("Config File :", EMOS_File , "Does not exist, Please verify and re run the script")
    sys.exit(-1)
    print("")

if os.path.isfile(output_file):
    try:
        os.remove(output_file)
    except:
        print("Unable to Delete old Output File :", output_file, ", May be it is opened by someone. please verify and close it and then re run the script")
        sys.exit(-1)


### Below one is sheet name to read data into hash
df = pd.read_excel(EMOS_File, 'MAX_PEAK_01SEP18_FORECAST_REPOR', na_values=['NA'])
dct = df.to_dict()

sdf = pd.read_excel(SNOW_FileName,sheet_name='Raw Data', na_values=['NA'])
#sdf_subset = sdf[['Component','Server Operating System','Server OS Version','Database Type','Database Version','Middleware Type','Middleware Version']]
#columns = sdf.head(0)  ## Getting top row as header


### Reading Input File  Here
inputFile = open(INPUT_FileName)
for line in inputFile:
	line = line.strip('\n')
	fields = line.split(',')
	Source_Server = fields[0]
	Targer_Server = fields[1]

	tHWArray = tSWArray = []
	############# Checking HW parity here
	sourceIndex = -1
	targetIndex = -1
	HWmatchStatus = "N"
	sCPUNo = sMEMNo = tCPUNo =  tMEMNo = 'N/A'

	for indx in df.index:
		if df['SRVNAME'][indx].lower() == Source_Server.lower():
			sourceIndex = indx
		if df['SRVNAME'][indx].lower() == Targer_Server.lower():
			targetIndex = indx
	### Comparing values here
	if (sourceIndex != -1):
		sCPUNo = trimNumber(df['GBL_NUM_CPU'][sourceIndex])
		sMEMNo = trimNumber(df['GBL_MEM_PHYS'][sourceIndex])
		if isNaN(sCPUNo):
			sCPUNo = ''
		if isNaN(sMEMNo):
				sMEMNo = ''

	if (targetIndex != -1):
		tCPUNo = trimNumber(df['GBL_NUM_CPU'][targetIndex])
		tMEMNo = trimNumber(df['GBL_MEM_PHYS'][targetIndex])
		if isNaN(tCPUNo):
			tCPUNo = ''
		if isNaN(tMEMNo):
				tMEMNo = ''

	if (sourceIndex == -1) or (targetIndex == -1):
		HWmatchStatus = "N/A"
	else:
		if (sCPUNo == tCPUNo) and (sMEMNo == tMEMNo):
			HWmatchStatus = "Y"

	#print(Source_Server.lower(), sCPUNo, sMEMNo, Targer_Server.lower(), tCPUNo, tMEMNo, matchStatus)
	tHWArray= [Source_Server.lower(), sCPUNo, sMEMNo, Targer_Server.lower(), tCPUNo, tMEMNo, HWmatchStatus]
	HWArray.append(tHWArray)

	############ Checking SW Parity Here
	sourceIndex = -1
	targetIndex = -1
	SWmatchStatus = "N"
	SOSName = SOSVer = SDBName =  SDBVer = SMWName = SMWVer = TOSName = TOSVer = TDBName =  TDBVer = TMWName = TMWVer = ''

	for indx in sdf.index:
		if sdf['Component'][indx].lower() == Source_Server.lower():
			sourceIndex = indx
		if sdf['Component'][indx].lower() == Targer_Server.lower():
			targetIndex = indx

	if (sourceIndex != -1):
		SOSName = sdf['Server Operating System'][sourceIndex]
		SOSVer = sdf['Server OS Version'][sourceIndex]
		SDBName = sdf['Database Type'][sourceIndex]
		SDBVer = sdf['Database Version'][sourceIndex]
		SMWName = sdf['Middleware Type'][sourceIndex]
		SMWVer = sdf['Middleware Version'][sourceIndex]

		## taking care of Nan Values
		if isNaN(SOSName):
			SOSName = ''
		if isNaN(SOSVer):
			SOSVer = ''
		if isNaN(SDBName):
			SDBName = ''
		if isNaN(SDBVer):
			SDBVer = ''
		if isNaN(SMWName):
			SMWName = ''
		if isNaN(SMWVer):
			SMWVer = ''

	if (targetIndex != -1):
		TOSName = sdf['Server Operating System'][targetIndex]
		TOSVer = sdf['Server OS Version'][targetIndex]
		TDBName = sdf['Database Type'][targetIndex]
		TDBVer = sdf['Database Version'][targetIndex]
		TMWName = sdf['Middleware Type'][targetIndex]
		TMWVer = sdf['Middleware Version'][targetIndex]

		## taking care of Nan Values
		if isNaN(TOSName):
			TOSName = ''
		if isNaN(TOSVer):
			TOSVer = ''
		if isNaN(TDBName):
			TDBName = ''
		if isNaN(TDBVer):
			TDBVer = ''
		if isNaN(TMWName):
			TMWName = ''
		if isNaN(TMWVer):
			TMWVer = ''

	if (sourceIndex == -1) or (targetIndex == -1):
		SWmatchStatus = "N/A"
	else:
		#if (SOSName == TOSName) and (SOSVer == TOSVer) and  (SDBName == TDBName) and (SDBVer == TDBVer) and  (SMWName == TMWName) and (SMWVer == TMWVer):
		if (SOSName == TOSName) and (SOSVer == TOSVer) and  (SDBName == TDBName) and (SDBVer == TDBVer) and  (SMWName == TMWName) and (SMWVer == TMWVer):
			SWmatchStatus = "Y"

	tSWArray= [Source_Server.lower(), SOSName, SOSVer, SDBName,   SDBVer, SMWName, SMWVer, Targer_Server.lower(), TOSName, TOSVer, TDBName, TDBVer, TMWName, TMWVer, SWmatchStatus]
	SWArray.append(tSWArray)


### Wrriting Output filename

### Open an Excel file for writing
wr = ExcelWriter(output_file)
HWData = pd.DataFrame(HWArray, columns=['QA Server Name', '#CPUs', '#Memory(GB)', 'Prod Server Name', '#CPUs', '#Memory(GB)', 'Parity'])
HWData.to_excel(wr,'HW Parity Data', index = False)

SWData = pd.DataFrame(SWArray, columns=['QA Server Name', 'Server Operating System','Server OS Version','Database Type','Database Version','Middleware Type','Middleware Version', 'Prod Server Name', 'Server Operating System','Server OS Version','Database Type','Database Version','Middleware Type','Middleware Version', 'Parity'])
SWData.to_excel(wr,'SW Parity Data', index = False)

### Save Excel file using file handler
wr.save()

## Returning Json Object with results
sys.exit(0)
################################### Done #######################
