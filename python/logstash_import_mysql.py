#!/bin/env python
# -*- coding:utf-8 -*- 

import os
import MySQLdb


valid_zone_list = ("1002", "1004", "1005")
process_list = []

def AppendFile(zone, logtype, filepath):
	for l in process_list:
		if l['zone'] == zone and l['type'] == logtype:
			l['file_list'].append(filepath)
			l['file_list'].sort()
			return
	tmp = {}
	tmp['zone'] = zone
	tmp['type'] = logtype
	tmp['file_list'] = [filepath]
	process_list.append(tmp)


for p_zone in valid_zone_list:
	dir_path = os.getcwd() + os.sep + p_zone
	L = os.listdir(dir_path)

	for p_file in L:
		pos = p_file.find("_")
		if pos < 0:
			continue
		log_type = p_file[pos + 1:]
		AppendFile(p_zone, log_type, dir_path + os.sep + p_file)

def ProcessFile(zone, logtype, logfile):
	print "Process", zone, logtype, logfile

	file_object = open(logfile)

	if logtype == "taskflow":
		logtype = "task"

	mysql_host_ip = '119.29.7.155'
	mysql_user = 'root'
	mysql_pass = 'zulong226'

	#连接数据库
	conn = MySQLdb.connect(
			host = mysql_host_ip,
			port = 3306,
			user = mysql_user,
			passwd = mysql_pass,
			)

	cur = conn.cursor()

	mysql_db = 'server_' + zone
	mysql_table = 'flow_' + logtype
	cur.execute('create database if not exists %s' % mysql_db)
	conn.select_db(mysql_db)

	table_create_sql = ""
	table_insert_sql = ""

	if logtype == "createrole":
		table_create_sql = """CREATE TABLE if not exists `flow_createrole` (
					  `sn` int(11) NOT NULL AUTO_INCREMENT,
					  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
					  `roleid` bigint(20) NOT NULL,
					  `profession` tinyint(4) NOT NULL,
					  `nation` tinyint(4) NOT NULL,
					  PRIMARY KEY (`sn`)
					) ENGINE=MyISAM DEFAULT CHARSET=utf8;"""

		table_insert_sql = "insert into flow_createrole values(NULL,'%s',%s, %s, %s)"
	elif logtype == "death":
		table_create_sql = """CREATE TABLE if not exists `flow_death` (
					  `sn` int(11) NOT NULL AUTO_INCREMENT,
					  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
					  `roleid` bigint(20) NOT NULL,
					  `level` int(11) NOT NULL,
					  `killer` bigint(20) NOT NULL,
					  `killer_level` int(11) NOT NULL,
					  `scene` int(11) NOT NULL,
					  `pos` varchar(30) NOT NULL,
					  PRIMARY KEY (`sn`)
					) ENGINE=MyISAM DEFAULT CHARSET=utf8;"""
		table_insert_sql = "insert into flow_death values(NULL,'%s', %s, %s, %s, %s, %s, '%s')"
	elif logtype == "task":
		table_create_sql = """CREATE TABLE if not exists `flow_task` (
			  `sn` int(11) NOT NULL AUTO_INCREMENT,
			  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
			  `roleid` bigint(20) NOT NULL,
			  `level` int(11) NOT NULL,
			  `task_id` int(11) NOT NULL,
			  `action` varchar(15) NOT NULL,
			  PRIMARY KEY (`sn`),
			  KEY `action_index` (`action`)
			) ENGINE=MyISAM AUTO_INCREMENT=4498777 DEFAULT CHARSET=utf8;"""
		table_insert_sql = "insert into flow_task values(NULL,'%s',%s,%s,%s,'%s')"
	elif logtype == "levelup":
		table_create_sql = """CREATE TABLE if not exists `flow_levelup` (
			  `sn` int(11) NOT NULL AUTO_INCREMENT,
			  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
			  `roleid` bigint(20) NOT NULL,
			  `profession` tinyint(4) NOT NULL,
			  `level` int(11) NOT NULL,
			  `usetime` int(11) NOT NULL,
			  PRIMARY KEY (`sn`)
			) ENGINE=MyISAM AUTO_INCREMENT=4498777 DEFAULT CHARSET=utf8;"""
		table_insert_sql = "insert into flow_levelup values(NULL,'%s', %s, %s, %s, %s)"
	elif logtype == "award":
		table_create_sql = """CREATE TABLE if not exists `flow_award` (
			  `sn` int(11) NOT NULL AUTO_INCREMENT,
			  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
			  `roleid` bigint(20) NOT NULL,
			  `level` int(11) NOT NULL,
			  `award` int(11) NOT NULL,
			  PRIMARY KEY (`sn`)
			) ENGINE=MyISAM AUTO_INCREMENT=4498777 DEFAULT CHARSET=utf8;"""
		table_insert_sql = "insert into flow_award values(NULL,'%s', %s, %s, %s)"
	elif logtype == "instance":
		table_create_sql = """CREATE TABLE if not exists `flow_instance` (
			  `sn` int(11) NOT NULL AUTO_INCREMENT,
			  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
			  `roleid` bigint(20) NOT NULL,
			  `level` int(11) NOT NULL,
			  `instance_tid` int(11) NOT NULL,
			  `status` int(11) NOT NULL,
			  PRIMARY KEY (`sn`)
			) ENGINE=MyISAM AUTO_INCREMENT=4498777 DEFAULT CHARSET=utf8;"""
		table_insert_sql = "insert into flow_instance values(NULL,'%s', %s, %s, %s, %s)"
	elif logtype == "roleloginlogout":
		table_create_sql = """CREATE TABLE if not exists `flow_roleloginlogout` (
			  `sn` int(11) NOT NULL AUTO_INCREMENT,
			  `log_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
			  `roleid` bigint(20) NOT NULL,
			  `action` varchar(15) NOT NULL,
			  `level` int(11) NOT NULL,
			  `online_time` int(11) NOT NULL,
			  PRIMARY KEY (`sn`)
			) ENGINE=MyISAM AUTO_INCREMENT=4498777 DEFAULT CHARSET=utf8;"""
		table_insert_sql = "insert into flow_roleloginlogout values(NULL,'%s', %s, '%s', %s, %s)"
		
	cur.execute(table_create_sql)

	for line in file_object:
		line = line.strip('\n')
		fields = line.split(' ')
		fields[0] = fields[0] + ' ' + fields[1]
		del fields[1]
		#print table_insert_sql
		#print fields
		sqli = table_insert_sql % tuple(fields)
		cur.execute(sqli)


print process_list

for l in process_list:
	zone = l['zone']
	type = l['type']
	file_list = l['file_list']
	for f in file_list:
		ProcessFile(zone, type, f)


