#import sqlite3
import MySQLdb
from settings import *

class TemporaryStorage:

	storage = {}
		
	def create(self,id,fields=None):
		if(fields==None):
			self.storage[id]={'chat_id':str(id)}
		else:
			self.storage[id]=fields
		
	def save(self,fields):
		id = fields['id']
		fields.pop('id')
		self.storage[id]=fields

	def get(self,id):
		return self.storage[id]
	
	def update(self,id,fields):
		for key in fields:
			self.storage[id][key]=fields[key]
  
	def contains(self,id):
		if id in self.storage:
			return True
		return False
	
	
class PermanentStorage:
  
	conn=None
	name=None
	
	DEBUG = False
	
	def __init__(self):
		self.conn = MySQLdb.connect(host="localhost", user=DB_USER, passwd=DB_PSW, db=DB_NAME)
	
	def create(self,fields, name="db"):
		self.name=name
		self.conn = MySQLdb.connect(host="localhost", user=DB_USER, passwd=DB_PSW, db=DB_NAME)
		cursor = self.conn.cursor()
		#sfields="id INTEGER PRIMARY KEY AUTOINCREMENT, "
		sfields=""
		for key in fields:
			sfields+=key+" "+fields[key]+","
		sfields=sfields[:-1]
		cmd='CREATE TABLE IF NOT EXISTS '+name+' ('+sfields+')'
		if(self.DEBUG):
			print cmd
		cursor.execute(cmd)
		self.conn.commit()
		
	def save(self,fields, name="db"):
		self.conn = MySQLdb.connect(host="localhost", user=DB_USER, passwd=DB_PSW, db=DB_NAME)
		cursor = self.conn.cursor()
		sfields=""
		for key in fields:
			sfields+=key+","
		sfields=sfields[:-1]
		
		svalues = ""
		for key in fields:
			if(type(fields[key]) is str):
				value = "'"+self.conn.escape_string(str(fields[key]))+"'"
			else:
				value = self.conn.escape_string(str(fields[key]))
			svalues+=value+","
		svalues = svalues[:-1]
		cmd = "INSERT INTO "+self.name+" ("+sfields+") VALUES ("+svalues+")"
		if(self.DEBUG):
			print cmd
		cursor.execute(cmd)
		self.conn.commit()
		
	def remove(self, id, name="db",other=None):
		self.conn = MySQLdb.connect(host="localhost", user=DB_USER, passwd=DB_PSW, db=DB_NAME)
		cursor = self.conn.cursor()
		if(other==None):
			cmd = "DELETE FROM "+self.name+" WHERE chat_id="+str(id)
		else:
			cmd = "DELETE FROM "+self.name+" WHERE chat_id="+str(id)+" AND "+other[0]+"='"+other[1]+"'"
		cursor.execute(cmd)
		self.conn.commit()
		
	def update(self,id,fields,other=None):
		self.conn = MySQLdb.connect(host="localhost", user=DB_USER, passwd=DB_PSW, db=DB_NAME)
		cursor = self.conn.cursor()
		svalues=""
		for key in fields:
			value=key+"="
			if(type(fields[key]) is str):
				value += "'"+self.conn.escape_string(str(fields[key]))+"'"
			else:
				value += self.conn.escape_string(str(fields[key]))
				
			svalues+=value+","
		svalues = svalues[:-1]
		if(other==None):
			cmd = "UPDATE "+self.name+" SET "+svalues+" WHERE chat_id="+str(id)
		else:
			cmd = "UPDATE "+self.name+" SET "+svalues+" WHERE chat_id="+str(id)+" AND "+other[0]+"='"+other[1]+"'"
		cursor.execute(cmd)
		self.conn.commit()
		if(cursor.rowcount==0):
			return False
		return True
	
	
	def saveOrUpdate(self,id,fields,other=None):
		if(not self.update(id,fields,other=other)):
			self.save(fields)

	def get(self,id,field="*"):
		self.conn = MySQLdb.connect(host="localhost", user=DB_USER, passwd=DB_PSW, db=DB_NAME)
		cursor = self.conn.cursor()
		cmd = "SELECT "+field+" FROM "+self.name+" WHERE chat_id="+str(id)
		cursor.execute(cmd)
		result=cursor.fetchall()
		if(len(result)==0):
			return None
		else:
			return result[0]
	
	
	def gets(self,id,field="*"):
		self.conn = MySQLdb.connect(host="localhost", user=DB_USER, passwd=DB_PSW, db=DB_NAME)
		cursor = self.conn.cursor()
		cmd = "SELECT "+field+" FROM "+self.name+" WHERE chat_id="+str(id)
		cursor.execute(cmd)
		result=cursor.fetchall()
		if(len(result)==0):
			return None
		else:
			return result
	
	def getInRange(self,id,field,start,end):
		self.conn = MySQLdb.connect(host="localhost", user=DB_USER, passwd=DB_PSW, db=DB_NAME)
		cursor = self.conn.cursor()
		cmd = "SELECT * FROM "+self.name+" WHERE chat_id="+str(id)+" AND DATE("+field+") BETWEEN '"+start+"' AND '"+end+"' GROUP BY date("+field+") ORDER BY id ASC"
		cursor.execute(cmd)
		result=cursor.fetchall()
		return result

	
	def getAll(self):
		self.conn = MySQLdb.connect(host="localhost", user=DB_USER, passwd=DB_PSW, db=DB_NAME)
		cursor = self.conn.cursor()
		cmd = "SELECT * FROM "+self.name
		cursor.execute(cmd)
		result=cursor.fetchall()
		return result

	def contains(self,id):
		self.conn = MySQLdb.connect(host="localhost", user=DB_USER, passwd=DB_PSW, db=DB_NAME)
		cursor = self.conn.cursor()
		matches=cursor.execute("SELECT * FROM "+self.name+" WHERE chat_id="+str(id))
		match=cursor.fetchone()
		if(match == None):
			return False
		return True
	
"""	
class PermanentStorage:
  
	conn=None
	name=None
	
	def __init__(self):
		self.conn = sqlite3.connect(DB_NAME,check_same_thread=False)
	
	def create(self,fields, name="db"):
		self.name=name
		self.conn = sqlite3.connect(DB_NAME,check_same_thread=False)
		sfields="id INTEGER PRIMARY KEY AUTOINCREMENT, "
		for key in fields:
			sfields+=key+" "+fields[key]+","
		sfields=sfields[:-1]
		cmd='CREATE TABLE IF NOT EXISTS '+name+' ('+sfields+')'
		cursor.execute(cmd)
		
	def save(self,fields, name="db"):
		print fields
		self.conn = sqlite3.connect(DB_NAME,check_same_thread=False)
		sfields=""
		for key in fields:
			sfields+=key+","
		sfields=sfields[:-1]
		
		svalues = ""
		for key in fields:
			if(type(fields[key]) is str):
				value = "'"+str(fields[key])+"'"
			else:
				value = str(fields[key])
			svalues+=value+","
		svalues = svalues[:-1]
		cmd = "INSERT INTO "+self.name+" ("+sfields+") VALUES ("+svalues+")"
		print cmd
		cursor.execute(cmd)
		self.conn.commit()
		self.conn.close()
		
	def remove(self, id, name="db"):
		self.conn = sqlite3.connect(DB_NAME,check_same_thread=False)
		cmd = "DELETE FROM "+self.name+" WHERE chat_id="+str(id)
		cursor.execute(cmd)
		self.conn.commit()
		self.conn.close()		
		
	def update(self,id,fields):
		self.conn = sqlite3.connect(DB_NAME ,check_same_thread=False)
		svalues=""
		for key in fields:
			value=key+"="
			if(type(fields[key]) is str):
				value += "'"+str(fields[key])+"'"
			else:
				value += str(fields[key])
			svalues+=value+","
		svalues = svalues[:-1]
		cmd = "UPDATE "+self.name+" SET "+svalues+" WHERE chat_id="+str(id)
		cursor=cursor.execute(cmd)
		self.conn.commit()
		self.conn.close()
		if(cursor.rowcount==0):
			return False
		return True
	
	
	def saveOrUpdate(self,id,fields):
		if(not self.update(id,fields)):
			self.save(fields)

	def get(self,id,field="*"):
		self.conn = sqlite3.connect(DB_NAME,check_same_thread=False)
		cmd = "SELECT "+field+" FROM "+self.name+" WHERE chat_id="+str(id)+" ORDER BY id DESC"
		result=cursor.execute(cmd).fetchone()
		cursor.execute(cmd)
		return result
	
	def getInRange(self,id,field,start,end):
		self.conn = sqlite3.connect(DB_NAME,check_same_thread=False)
		cmd = "SELECT * FROM "+self.name+" WHERE chat_id="+str(id)+" AND DATE("+field+") BETWEEN '"+start+"' AND '"+end+"' GROUP BY date("+field+") ORDER BY id ASC"
		result=cursor.execute(cmd).fetchall()
		cursor.execute(cmd)
		return result

	
	def getAll(self):
		self.conn = sqlite3.connect(DB_NAME,check_same_thread=False)
		cmd = "SELECT * FROM "+self.name
		result=cursor.execute(cmd).fetchall()
		cursor.execute(cmd)
		return result

	def contains(self,id):
		self.conn = sqlite3.connect(DB_NAME,check_same_thread=False)
		matches=cursor.execute("SELECT * FROM "+self.name+" WHERE chat_id="+str(id))
		match=matches.fetchone()
		self.conn.close()
		if(match == None):
			return False
		return True
"""
	