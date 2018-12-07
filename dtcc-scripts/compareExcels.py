import pandas as pd
import numpy as np

# Define the diff function to show the changes in each field
def report_diff(x):
    p = x[0]
    q = x[1]
    #print(x[0],'--------------', x[1])
    if (type(x[0]) is int) or (type(x[0]) is float):
        p = float(x[0])
        p = format(p,'.2f')
		q = float(x[1])
		q = format(q, '.2f')
    if (type(x[1]) is int) or (type(x[1]) is float):
	    q = float(x[1])
	    q = format(q, '.2f')
	    p = float(x[0])
	    p = format(p,'.2f')
    return x[0] if str(p).lower().strip() == str(q).lower().strip() else '{} ---> {}'.format(*x)

    ## I have used string lower function just to ignore case while comparing excell cell values

# We want to be able to easily tell which rows have changes
def has_change(row):
    if "--->" in row.to_string():
        return "Yes"
    else:
        return "No"

########################## Main Program ########################################
filename1 = 'EMOS-Original.xlsx'
filename2 = 'EMOS-Chayanika.xlsx'

#filename1 = 'filename1.xlsx'
#filename2 = 'filename2.xlsx'

#df1 = pd.read_excel(filename1, index_col=0)
#df2 = pd.read_excel(filename2, index_col=0)
df1 = pd.read_excel(filename1, 'Scorecard', na_values=['NA'])
df2 = pd.read_excel(filename2, 'Scorecard', na_values=['NA'])

# Make sure we order by account number so the comparisons work
#df1.sort(columns="Full name")
#df1=df1.reindex()
#df2.sort(columns="Full name")
#df2=df2.reindex()

# Create a panel of the two dataframes
diff_panel = pd.Panel(dict(df1=df1,df2=df2))


#Apply the diff function
diff_output = diff_panel.apply(report_diff, axis=0)

# Flag all the changes
diff_output['has_changed'] = diff_output.apply(has_change, axis=1)

#Save the changes to excel but only include the columns we care about
#diff_output[(diff_output.has_change == 'Y')].to_excel('my-diff-1.xlsx',index=False,columns=["account number","name","street","city","state","postal code"])

#diff_output[(diff_output.has_change == 'Y')].to_excel('my-diff-1.xlsx',index=False,columns=["Full name","Username"])
diff_output.to_excel('Differences.xlsx',index=False,columns=["has_changed","servername","Consol HOST","Consol GUEST","VMware Virt CPU Sizing","Virt CPU Count Adjust","Virt Mem Adjust (GB)","System OS","AppName","SISID","CPUs Used","CPU count (Computer)","Memory Used (GB)","GBL_MEM_PHYS (GB)","Server Designation","AppCategory","Server phys-virt","Power Rating","Power Used","CPU speed (Computer)","CPU type (Computer)","Primary Application (Asset)","Name (Device Support Team)","Device Status (Asset)","Associated Company (Asset)","Brand (Model)","Model","Server Type (Asset)","Server Function (Asset)","Environment","Network Location Name (Asset#LocationRisk)","Network Location (Asset)","Name (Location)","Location Region","Oper# System (Computer)","OS Version","Service Pack (Computer)","Business Risk (Asset)","Data Risk (Asset)","Location Risk Level (Asset#LocationRisk)","In-service date","Name (Application Support Team)","Serial # (Asset)","Owner/Support Technician","PCT_Range_CPU","PCT_Range_Mem","CPU Maxpeak","Memory Maxpeak","IOPS Maxpeak","GBL_RUN_QUEUE_MAX","RunQ_perCPU_AT_CPU_MAXPEAK","FORECAST_CPU","CPU FORECAST ADD CPUS","FORECAST_MEM_USER","FORECAST_IOPS","Peak CPU Projection Index","Peak Memory Projection Index","Peak CPU Current At-Risk Index","TeamQuest Installed","Rate Codes","Primary_Cluster","Capacity Charts (CPU, Mem, IOPS)","Forecast Capacity Charts (CPU, Mem, IOPS)","Forecast Capacity Report (CPU)","Forecast Capacity Report (Memory)","Forecast Capacity Report (IOPS)"])

#difference = df1[df1!=df2]
#print(difference)

print("Done")
