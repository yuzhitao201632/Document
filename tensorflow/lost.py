#/usr/bin/python
#coding=utf-8
#import pyspark
import MySQLdb
import time,datetime
import os,sys
import re
db_host='119.29.7.155'
db_port=3306
db_user='root'
db_passwd='zulong226'
mysql_db='seven_test'
#log_dir="/export/open_test/logstash/stage_6/1002"
log_dir="/export/tensorflow/1002"
#file_list=["levelup","taskflow","award","death"]
file_list=["taskflow"]
step_day=-30

#30天之前的创建的角色
create_role_dict={}
role_detail_dict={}
class last_role:
	def __init__(self,role,day,hour):
		self.roleid=role;
		#每日变更
		self.day=day
		#最后日志的时间,就是小时
		self.log_time=hour
		self.ts=0
		#一直记录
		self.taskid_sum=0
		self.inst_sum=0
		self.online_sum=0
		#每天max,求最大的,活跃度 
		self.day_act=0
		#sum
		self.killed_times=0;
		self.killer_num=0
		#钻石的复活次数
		self.diamond_revive_num=0;
		#=======================================
		#最后的礼包
		self.last_gift_id=0
		#last 
		self.local_level=0;
		self.levelup_times=0
		#-logout
		self.logout_scene=0;
		self.logout_x=0
		self.logout_y=0
		self.logout_z=0
		#更新时间戳
		self.update_last_time(day,hour)
		self.is_lost=False

	def update_last_time(self,day,hour):
		ts_last="%s %s"%(day,hour)
		ts2=int(time.mktime(time.strptime(ts_last,'%Y-%m-%d %H:%M:%S')))
		if ts2> self.ts:
			#if self.ts:
			#	print "old ts=%d:newer=%d"%(self.ts,ts2)
			self.day=day
			self.log_time=hour
			self.ts=ts2
			return True
		return False
	#系统账号
	def compare_and_swap(self, other):
		if self.roleid!=0:
			return 
		if self.taskid_sum<other.taskid_sum:
			self.taskid_sum=other.taskid_sum
		if self.inst_sum<other.inst_sum:
			self.inst_sum=other.inst_sum
		if self.online_sum<other.online_sum:
			self.online_sum=other.online_sum
		if self.day_act<other.day_act:
			self.day_act=other.day_act
		if self.killed_times<other.killed_times:
			self.killed_times=other.killed_times
		if self.killer_num<other.killer_num:
			self.killer_num=other.killer_num
		if self.diamond_revive_num<other.diamond_revive_num:
			self.diamond_revive_num=other.diamond_revive_num
		self.update_last_time(other.day,other.log_time)

	def __logout__(self,cursor):
		cursor.submit()

class role_base:
	def __init__(self,roleid,date_cr,time_cr,prof,nation):
		if roleid ==0 :
			raise  RuntimeError("rolebase error")
		self.roleid=roleid
		self.create_time=date_cr+" "+time_cr
		self.prof=int(prof)
		self.nation=int(nation)
		#self.lost_3=False


def log_init_reader():
	fl=os.listdir(log_dir)
	for a in xrange(step_day,-1,1):
		prior_d=(datetime.timedelta(days=a)+datetime.date.today()).strftime("%Y-%m-%d")
		day_file=prior_d+"_createrole"
		for fs in fl:
			if fs==day_file:
				print "get file=%s:day=%s"%(fs, prior_d)
				return log_dir+"/"+fs,a
			
	

def db_conn_init():
	conn=MySQLdb.connect(host=db_host,port=db_port,user=db_user,passwd=db_passwd,db=mysql_db)
	cursor=conn.cursor()
	return cursor,conn

def db_conn_close(cursor,conn):
	cursor.close()
	conn.close()

def read_need_file_list():
	createrole,day_step=log_init_reader()
	with open(createrole) as  fd:
		while True:
			line=fd.readline()
			if line is None:
				break
			if line =="":
				break
			#print createrole,line
			info=line.split()
			ai=role_base(info[2],info[0],info[1],info[3],info[4])
			create_role_dict[info[2]]=ai#Save
	return day_step


def log_roleloginlogout(line,prior_d):
	info=line.split()
	roleid=info[2]
	login_type=info[3]
	login_level=int(info[4])
	login_time=int(info[5])
	if login_type=="logout":
		if create_role_dict.has_key(roleid):
			if role_detail_dict.get(roleid):
				detail=role_detail_dict[roleid]
				detail.online_sum+=login_time
				#少日志了
				if login_level>detail.local_level:
					detail.level=login_level
				detail.update_last_time(info[0],info[1])
			else:
				log_day=info[0]
				log_ts=info[1]
				detail=last_role(roleid,log_day,log_ts)
				detail.online_sum+=login_time
				#少日志了
				if login_level>detail.local_level:
					detail.level=login_level
				role_detail_dict[roleid]=detail        	
	
	


def log_taskflow(line,prior_d):
	info=line.split()
	roleid=info[2]
	task_id=info[4]	
	task_type=info[5]
	#if task_type!="accomplished":
	if create_role_dict.has_key(roleid):
		if role_detail_dict.get(roleid):
			detail=role_detail_dict[roleid]
			detail.taskid_sum+=1
			#print "roleid=%s task_sum=%d"%(detail.roleid,detail.taskid_sum)
			detail.update_last_time(info[0],info[1])
		else:
			log_day=info[0]
			log_ts=info[1]
			detail=last_role(roleid,log_day,log_ts)
			detail.taskid_sum+=1
			role_detail_dict[roleid]=detail        	


		
def log_death(line,prior_d):
	info=line.split()
	roleid_1=info[2]
	roleid_2=info[4]
	scene=int(info[6])
	pos=info[7]
	detail=None
	if create_role_dict.has_key(roleid_1):
		if role_detail_dict.get(roleid_1):
			detail=role_detail_dict[roleid_1]
			detail.update_last_time(info[0],info[1])
		else:
			log_day=info[0]
			log_ts=info[1]
			detail=last_role(roleid_1,log_day,log_ts)
			role_detail_dict[roleid_1]=detail        
		if detail is not None: 
			detail.killed_times+=1
			pos=filter(lambda x : x!="", re.split(',|\(|\)',pos))
			detail.logout_scene=scene
			detail.logout_x=int(float(pos[0]))
			detail.logout_y=int(float(pos[1]))
			detail.logout_z=int(float(pos[2]))

	if create_role_dict.has_key(roleid_2):
		if role_detail_dict.get(roleid_2):
			detail=role_detail_dict[roleid_2]
			detail.update_last_time(info[0],info[1])
		else:
			log_day=info[0]
			log_ts=info[1]
			detail=last_role(roleid_2,log_day,log_ts)
			role_detail_dict[roleid_2]=detail       
		detail.killer_num+=1
			
def log_award(line,prior_d):
	info=line.split()
	roleid=info[2]
	level=int(info[3])
	award_id=int(info[4])
	log_day=info[0]
	log_ts=info[1]
	detail =None
 	if create_role_dict.has_key(roleid):
		if role_detail_dict.get(roleid):
			detail=role_detail_dict[roleid]
		else:
			detail=last_role(roleid,log_day,log_ts)
			role_detail_dict[roleid]=detail
	if detail is not None:
		if detail.update_last_time(log_day,log_ts):
			detail.last_gift_id=int(award_id)
		if detail.local_level>level:
			detail.local_level=level
			



def log_levelup(line,prior_d):
	info=line.split()
	roleid=info[2]
	level=int(info[4])
	uplevel_timeused=int(info[5])
	if create_role_dict.has_key(roleid):
		if role_detail_dict.get(roleid):
			detail=role_detail_dict[roleid]
			if level>detail.local_level:
				detail.local_level=level
				detail.levelup_times=uplevel_timeused
				detail.update_last_time(info[0],info[1])
		else:
			log_day=info[0]
			log_ts=info[1]
			detail=last_role(roleid,log_day,log_ts)
			detail.local_level=level
			detail.levelup_times=uplevel_timeused
			role_detail_dict[roleid]=detail

"""
+------------------+------------+------+-----+------------+----------------+
| Field            | Type       | Null | Key | Default    | Extra          |
+------------------+------------+------+-----+------------+----------------+
| day              | date       | NO   | MUL | 0000-00-00 |                |
| log_time         | time       | NO   |     | 00:00:00   |                |
| task_sum         | int(11)    | YES  |     | 0          |                |
| inst_sum         | int(11)    | YES  |     | 0          |                |
| day_act          | int(11)    | YES  |     | NULL       |                |
| killed_times     | int(11)    | YES  |     | NULL       |                |
| diamond_revive   | int(11)    | YES  |     | NULL       |                |
| last_gift_id     | int(11)    | YES  |     | 0          |                |
| online_time      | int(11)    | YES  |     | 0          |                |
| logout_scene     | int(11)    | YES  |     | NULL       |                |
| levelup_lasttime | int(11)    | YES  |     | NULL       |                |
| logout_pos_x     | int(11)    | YES  | MUL | NULL       |                |
| logout_pos_y     | int(11)    | YES  |     | NULL       |                |
| logout_pos_z     | int(11)    | YES  |     | NULL       |                |
| id               | bigint(20) | NO   | PRI | NULL       | auto_increment |
| roleid           | bigint(20) | NO   | MUL | NULL       |                |
| killer_sum       | int(11)    | YES  |     | 0          |                |
| init30_level     | int(11)    | YES  |     | NULL       |                |
+------------------+------------+------+-----+------------+----------------+
16 rows in set (0.00 sec)
"""
def save_role_detail(cursor,conn):
	for role in role_detail_dict.values():
		#command="replace into role_act_flow(day,log_time,task_sum,inst_sum,day_act,killed_times,diamond_revive,last_gift_id,online_time,logout_scene,levelup_lasttime,logout_pos_x,logout_pos_y,logout_pos_z,roleid,killer_sum,init30_level) values(\"%s\",\"%s\",%d,%d,%d,%d,%d,%d,%d, %d,%d, %d,%d,%d,%s,%d,%d)"%(role.day,role.log_time,role.taskid_sum,role.inst_sum, role.day_act,role.killed_times,role.diamond_revive_num,role.last_gift_id,role.online_sum,role.logout_scene,role.levelup_times,role.logout_x,role.logout_y,role.logout_z,role.roleid,role.killer_num,self.local_level)
		command="replace into role_act_flow(day,log_time,task_sum,inst_sum,day_act,killed_times,diamond_revive,online_time,roleid,killer_sum) values(\"%s\",\"%s\",%d,%d,%d,%d,%d,%d,%s,%d)"%(role.day,role.log_time,role.taskid_sum,role.inst_sum, role.day_act,role.killed_times,role.diamond_revive_num,role.online_sum,role.roleid,role.killer_num)
		#print "save_role_detail comm=%s:capacity=%d"%(command,role_detail_dict.__len__())
		cursor.execute(command)
		conn.commit()

#不变的数据
def save_role_base(cursor,conn):
	for rolebase in create_role_dict.values():
		command="replace into role_base values(%s,%d,%d,\"%s\")"%(rolebase.roleid,rolebase.prof,rolebase.nation, rolebase.create_time)
		#print "save_role_base command=%s:capacity=%d"%(command,create_role_dict.__len__())
		cursor.execute(command)
		conn.commit()

def build_role_act(day_step):
	for a in xrange(day_step,-1,1):
		prior_d=(datetime.timedelta(days=a)+datetime.date.today()).strftime("%Y-%m-%d")
		#按照日期倒序解析
		for fs in file_list:
			fp="%s/%s_%s"%(log_dir,prior_d,fs)
			if not os.path.exists(fp):
				#print "file %s not exists!"%fp
				continue
			with open(fp) as  fd:
				while True:
					line=fd.readline()
					if line is None:
						break
					if line =="":
						break;
					command=fp.split('_')[1]
					#print "build role detail act line=%s:command=%s"%(line,command)
					prog_func="log_"+command
					eval(prog_func)(line,prior_d)
	for role in role_detail_dict.values():
		normalize_detail(role)
	print "build role act OK rolelist=%d, just Save" %role_detail_dict.__len__()

#账号存储全局信息
def init_system_info(day_offset):
	prior_d=(datetime.timedelta(days=day_offset)+datetime.date.today()).strftime("%Y-%m-%d")
	log_day=prior_d
	log_ts="00:00:00"
	init_role_id=0;
	system_detail=last_role(init_role_id,log_day,log_ts)
	role_detail_dict[0]=system_detail

def normalize_detail(other):
	if other.day is None:	
		return
	if other.roleid==0:
		return ;

	init_zero=role_detail_dict[0]
	init_zero.compare_and_swap(other)

def get_lost_list():
	role_init=role_detail_dict[0]
	for role in role_detail_dict.values():
		if role.roleid==0:
			continue
		time_diff=role_init.ts-role.ts
		if time_diff<0:
			print "get_lost_list roleid=%d:ts=%s:day=%s:log_ts=%s:max_ts=%s:max_day=%s:max_hour=%s"\
				%(role.roleid,role.ts,role.day,role.log_time,role_init.ts, role_init.day,role_init.log_time)
		if time_diff>60*60*24:
			print "LOST:roleid=%s:ts=%s:day=%s:log_ts=%s:max_ts=%s:max_day=%s:max_hour=%s"\
				%(role.roleid,role.ts,role.day,role.log_time,role_init.ts, role_init.day,role_init.log_time)
			#lost_dist[role.roleid]=True
			role.is_lost=True
		else:
			#lost_dist[role.roleid]=False
			role.is_lost=False

#from pyspark import SparkContext
def txt_save():
	cursor,conn=db_conn_init()
	day_offset=read_need_file_list()

	init_system_info(day_offset)

	build_role_act(day_offset)
	get_lost_list()

	#save_role_base(cursor,conn)
	#save_role_detail(cursor,conn)
	print "save all ok ,just close db conn,day_offset=%d"%day_offset
	db_conn_close(cursor,conn)

if __name__=='__main__':
	txt_save()
