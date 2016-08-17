import mysql.connector
from mysql.connector import errorcode

config = {
	'user':'jclay6',
	'password':'bottlehead',
	'host':'mmcdb.arcc.uwyo.edu',
	'database':'StorageUsage',
	'raise_on_warnings':True,
}

def kbToGb(num):
	return '%.2f' % ((num*(2**10))/float(2**30))

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
			cursor.close()
			cnx.close()
			exit(1)

		else:
			blockUsage,blockLimit,filesUsage = cursor.fetchone()
			cursor.close()
			cnx.close()
			return [blockUsage,blockLimit,filesUsage]
		
		

# method that creates a python dictionary of the form:
# {'date1': {'user1': blockUsage, 'user2': blockUsage, ...}, 'date2': {'user1': blockUsage, 'user2': blockUsage, ...}, ...}
def createDailyUsrStorageDict(theAccount,theDate):
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

		year=theDate.split('-')[0]
		month=theDate.split('-')[1]
		day=int(theDate.split('-')[2])

		storageDict = {}                                                               

		query = ("SELECT sampleDate, name, blockUsage FROM datastorage WHERE "\
			+"sampleDate=%s and quotaType='USR' and not name='root' and "\
			+"filesetName=%s")

		for i in range(1,day+1):
			day='%02d'%i
			sDate=str(year)+'-'+month+'-'+day

			try:
				cursor.execute(query,(sDate,'p_'+theAccount))
			except:
				continue
			else:
				if cursor.with_rows:
					dailyUsage=[]
					for (sampleDate,name,blockUsage) in cursor:
						if blockUsage is not None:
							if sDate not in storageDict:
								storageDict[sDate] = {name:float(kbToGb(blockUsage))}
							elif name not in storageDict[sDate]:
								storageDict[sDate][name] = float(kbToGb(blockUsage))

		# ensure there is an entry for every user for every valid date
		# this will place 0s in dates prior to initial entry for new users
		dates=[]
		for date in storageDict.keys():
			dates.append(date)
		dates.sort()
		for user in storageDict[dates[len(dates)-1]].keys():
			for i in range(len(dates)-2,-1,-1):
				if user not in storageDict[dates[i]]:
					print ("Adding 0.0 as entry to storageDict[%s][%s]"%(dates[i],user))
					storageDict[dates[i]][user] = 0.0

		cursor.close()
		cnx.close()
		return storageDict


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
		userList.sort()

		cursor.close()
		cnx.close()
		return userList


#
def getDailyData(theAccount, theDate):
	usage=[] # in the form [[user1data],[user2data],[user3data],...]
	dates=[]     

	# get current storage dictionary (see createDailyUsrStorageDict() for details)
	storageDict = createDailyUsrStorageDict(theAccount,theDate)

	# add all of the dates stored in the dictionary to list 'dates', then sort
	for date in storageDict.keys():
		dates.append(date)
	dates.sort()
	
	# add all users to a list 'users', then sort
	# this ensures that all color coding in legend remains constant throughout
	users=[]
	for user in storageDict[dates[len(dates)-1]].keys():
		users.append(user)
	users.sort()
	for userIndex in range(len(users)):
		userStorage=[]
		for i in range(len(dates)):
			userStorage.append(storageDict[dates[i]][users[userIndex]])
		usage.append(userStorage)

	return [usage,dates]


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
		grpList.sort()
				
		cursor.close()
		cnx.close()
		return grpList

# account = 'evolvingai'
# date = '2016-08-17'
# #projectData = getProjectData(account,date)
# userData = getUsrData(account,date)
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
#data=getMonthlyData('evolvingai','2016-08-17')
#print (data)
# data = getDailyData('evolvingai','2016-08-17')
# print data
