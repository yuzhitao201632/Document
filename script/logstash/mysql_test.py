#!/usr/bin/env python
#coding=utf-8
import MySQLdb

mysql_host_ip = '119.29.36.204'
mysql_user = 'root'
mysql_pass = 'zulong204'
mysql_db = 'logstash'
mysql_table = 'taskflow'

conn= MySQLdb.connect(
	host = mysql_host_ip,
        port = 3306,
        user = mysql_user,
        passwd = mysql_pass,
        db = mysql_db,
        )
cur = conn.cursor()

#2016-11-10 00:00:00 635962346 37 20091 accomplished

#创建数据表
#sqli = "create table if not exists %s (id int ,name varchar(20),class varchar(30),age varchar(10))" % (mysql_table)
#cur.execute(sqli)
#cur.execute(sqli, (mysql_table))
#cur.execute("create table if not exists taskflow(id int ,name varchar(20),class varchar(30),age varchar(10))")

#插入一条数据
#sqli = "insert into %s values('2','Tom','3 year 2 class','9')" % (mysql_table)
#cur.execute(sqli)
#cur.execute(sqli, (mysql_table))
#cur.execute("insert into taskflow values('2','Tom','3 year 2 class','9')")

file_object = open("2016-11-10_taskflow")
for line in file_object:
	fields = line.split(' ')
	date = fields[0] + fields[1]
	roleid = fields[2]
	level = fields[3]
	taskid = fields[4]
	flow_type = fields[5]
	sqli = "insert into %s values(NULL,'%s',%s,%s,%s,'%s')" % (mysql_table, date, roleid, level, taskid, flow_type)
	cur.execute(sqli)

#修改查询条件的数据
#sqli = "update student set class = '3 year 1 class' where name = 'Tom'"
#cur.execute(sqli)

#删除查询条件的数据
#cur.execute("delete from student where age='9'")

#sqli = "insert into student values(%s,%s,%s,%s)"
#cur.execute(sqli,('3','Huhu','2 year 1 class','7'))
#
#cur.executemany(sqli,[
	    #('4','Tom','1 year 1 class','6'), 
	    #('5','Jack','2 year 1 class','7'), 
	    #('6','Yaheng','2 year 2 class','7'), 
	    #])

#sqli = "select * from %s" % (mysql_table)
#aa = cur.execute("select * from taskflow")
#aa = cur.execute(sqli)
print cur.fetchone()

#info = cur.fetchmany(aa)
#for ii in info:
#	print ii

cur.close()
conn.commit()
conn.close()
