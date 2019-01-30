import pandas as pd
import xlsxwriter
path='C:\project\TQClient\TQFiles\TQ_DATA_1537792295157\Report.csv'
outpath='C:\project\TQClient\TQFiles\TQ_DATA_1537792295157\Infra_Analysis_Result.xlsx'
report_path = path
output_path = outpath
data = pd.read_csv(report_path)
writer = pd.ExcelWriter(outpath, engine='xlsxwriter')
data.to_excel(writer, sheet_name='Infra_Analysis_Result', index=False)


#Threshold Data

d = {'Metrics': ["CPU_Util and CPU Queue", "CPU_Util and CPU Queue", "Disk_Util and Disk_Queue", 
				"Disk_Util and Disk_Queue", "Disk_Response", "Disk_Response", "Memory_Util", "Memory_Util", "Swap", "Swap"], 
	'Criteria': ["CRITICAL", "WARN", "CRITICAL", "WARN", "CRITICAL", "WARN", "CRITICAL", "WARN", "CRITICAL", "WARN"]}
data2 = pd.DataFrame(data=d)
data2.to_excel(writer, sheet_name='Threshold_Detailed_Definition', index=False)

#Get the xlsxwriter workbook and worksheet1 objects.

workbook = writer.book

worksheet1 = writer.sheets['Infra_Analysis_Result']
#worksheet2 = writer.sheets['Threshold_Detailed_Definition']



# Format the workbook

format1 = workbook.add_format({'bg_color': '#00e600',
                               'font_color': '#000000'})
format2 = workbook.add_format({'bg_color': '#ff0000',
                               'font_color': '#000000'})
format3 = workbook.add_format({'bg_color': '#e6ac00',
                               'font_color': '#000000'})

							   
worksheet1.conditional_format('A1:Z50', {'type': 'cell',
										'criteria': 'equal to',
										'value': '"OK"',
										'format': format1})
worksheet1.conditional_format('A1:Z50', {'type': 'cell',
										'criteria': 'equal to',
										'value': '"CRITICAL"',
										'format': format2})										

worksheet1.conditional_format('A1:Z50', {'type': 'cell',
										'criteria': 'equal to',
										'value': '"WARN"',
										'format': format3})	
writer.save()
