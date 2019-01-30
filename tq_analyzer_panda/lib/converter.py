import sys
import fileinput
import re

# replace all occurrences of '=' with ',' and insert a line after the 5th
with open('config.csv', 'w') as f:

	#for i, line in enumerate(fileinput.input('configurations.ini', inplace = True)):
	for i, line in enumerate(fileinput.input('config.ini')):
    
		line=re.sub('^\[(.*)\n', '', line)
		line=re.sub('=', ',', line)
		#print(line)
		f.write(line)
		f.close
