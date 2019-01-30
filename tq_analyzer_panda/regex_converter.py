import re
inputfile = open('config.ini','w+',encoding="utf8")

inputfile.write(re.sub(r'\^\[\*','',inputfile.read()))

file.close()
outputfile.close()