import mysql.connector
from mysql.connector import errorcode

config = {
	'user':'jclay6',
	'password':'bottlehead',
	'host':'mmcdb.arcc.uwyo.edu',
	'database':'StorageUsage',
	'raise_on_warnings':True,
}


# method that queries the database and returns statistics for the project in
# the form of a list: [blockUsage, blockLimit, filesUsage]
def getProjectData(theAccount, theDate):
	try:
		cnx = mysql.connector.connect(**config)

	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("Something is wrong with your user name or password")

		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			print("Database does not exist")

		else:
			print(err)

	else:
		cursor = cnx.cursor()

		query = ("SELECT blockUsage,blockLimit,filesUsage FROM datastorage "\
			+"WHERE sampleDate=%s and name=%s")

		cursor.execute(query,(theDate,'p_'+theAccount))

		if cursor.rowcount>1:
			print('More than one entry found')
			exit(1)

		else:
			blockUsage,blockLimit,filesUsage = cursor.fetchone()
			return [blockUsage,blockLimit,filesUsage]
		
		cursor.close()
		cnx.close()


# method that queries the database and returns statistics for all users for a
# specific project in the form of a list of tuples: 
# [(user1, blockUsage, filesUsage), (user2, blockUsage, filesUsage), ...]
def getUsrData(theAccount, theDate):
	try:
		cnx = mysql.connector.connect(**config)

	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("Something is wrong with your user name or password")

		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			print("Database does not exist")

		else:
			print(err)

	else:
		cursor = cnx.cursor()

		query = ("SELECT name, blockUsage,filesUsage FROM datastorage WHERE "\
			+"sampleDate=%s and quotaType='USR' and not name='root' and "\
			+"filesetName=%s")

		cursor.execute(query,(theDate,'p_'+theAccount))

		userList=[]
		for (name, blockUsage, filesUsage) in cursor:
			userList.append((name, blockUsage, filesUsage))
		
		return userList
		
		cursor.close()
		cnx.close()


# method that queries the database and returns statistics for all groups for a
# specific project in the form of a list of tuples: 
# [(grp1, blockUsage, filesUsage), (grp2, blockUsage, filesUsage), ...]
def getGrpData(theAccount, theDate):
	try:
		cnx = mysql.connector.connect(**config)

	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("Something is wrong with your user name or password")

		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			print("Database does not exist")

		else:
			print(err)

	else:
		cursor = cnx.cursor()

		query = ("SELECT name, blockUsage,filesUsage FROM datastorage WHERE "\
			+"sampleDate=%s and quotaType='GRP' and not name='root' and "\
			+"filesetName=%s")

		cursor.execute(query,(theDate,'p_'+theAccount))

		grpList=[]
		for (name, blockUsage, filesUsage) in cursor:
			grpList.append((name, blockUsage, filesUsage))
		
		return grpList
		
		cursor.close()
		cnx.close()

#account = 'evolvingai'
#date = '2016-08-16'
#projectData = getProjectData(account,date)
#userData = getUsrData(account,date)
#groupData = getGrpData(account,date)
#print "%s:"%account,projectData
#
#print("User Data")
#for (name, blockUsage, filesUsage) in userData:
#	print "%s, %d, %d"%(name,blockUsage,filesUsage)
#
#print("Group Data")
#for (name, blockUsage, filesUsage) in groupData:
#	print "%s, %d, %d"%(name,blockUsage,filesUsage)