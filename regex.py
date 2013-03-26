#!/usr/bin/python
# URL that generated this code:
# http://txt2re.com/index-python.php3?s=%20%20%20%20%20%20%20%20%20%20%3Ctd%3E%20%3Cspan%20style=%22padding-left:0%22%3Edoi%3E%3Ca%20href=%22http://dx.doi.org/10.1145/332040.332042%22%20title=%22DOI%22%3E10.1145/332040.332042%3C/a%3E%3C/span%3E%3C/td%3E&59&3

import re

# the open keyword opens a file in read-only mode by default
f = open("SIGCHI/CHI'00.html")
 
# read all the lines in the file and return them in a list
filetext = f.read()
# print filetext
f.close()


start = 'doi&gt;<a href="'
end = '" title'
print re.findall(re.escape(start)+"(.*)"+re.escape(end),filetext)


# rg = re.compile(regularExp,re.DOTALL)
# m = re.search(regularExp,filetext)
# print m
# if m:
#     word1=m.group(1)
#     httpurl1=m.group(2)
#     print "\n("+word1+")"+"("+httpurl1+")"+"\n"
# 

#-----
# Paste the code into a new python file. Then in Unix:'
# $ python x.py 
#-----
