#!/bin/env python
import os
import sys

valid_zone_list = ("1002", "1004", "1005")
if sys.argv[1] in valid_zone_list:
	print "valid"

sStr1 = 'abcdefg'
sStr2 = 'cdk'
print sStr1.find(sStr2)

logfile_list = {}
logfile_list = ["2016-11-08_taskflow", "2016-11-07_taskflow"]
logfile_list.sort()

process_data = {'zone':"1002", 'type':"task_flow", 'file_list':["2016-11-08_taskflow", "2016-11-09_taskflow", "2016-11-10_taskflow"]}
print process_data

print logfile_list
for logfile_name in logfile_list:
	pos = logfile_name.find("_")
	if (pos >= 0):
		date = logfile_name[:pos]
		type = logfile_name[pos + 1:]
		logfile_list
		print date, type

