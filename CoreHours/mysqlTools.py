###############################################################################
# mysqlTools.py
# Jeremy Clay
# Aug 20, 2016
# 
# Contains tools needed to query the 'StorageUsage' mysql database stored on 
# mmcdb.arcc.uwyo.edu
# 
# Dependencies:	
###############################################################################


import mysql.connector
from mysql.connector import errorcode
from datetime import date

Months = {1:'Jan', 2:'Feb', 3:'Mar', 4:'April', 5:'May', 6:'June', 7:'July', 
			8:'Aug', 9:'Sept', 10:'Oct', 11:'Nov', 12:'Dec'}

MonthNumber = {'Jan':1, 'Feb':2, 'Mar':3, 'April':4, 'May':5, 'June':6,
				'July':7, 'Aug':8, 'Sept':9, 'Oct':10, 'Nov':11, 'Dec':12}

# dictionary used to store database login information
# will be used in multiple methods to establish a connection to the database
config = {
	'user':'jclay6',
	'password':'bottlehead',
	'host':'mmcdb.arcc.uwyo.edu',
	'database':'StorageUsage',
	'raise_on_warnings':True,
	}


# method that returns a string of a date in YYYY-mm-dd format.  The date
# returned will be the last day of the month given the parameters
# statementMonth and statementYear.
# e.g. statementMonth = 4 and statementYear = 2016, the date that will be
# retruned is 2016-04-30
def getQueryDate(statementMonth,statementYear):
	# statementMonth is an integer that correlates to the calendar month of the
	# year.  e.g. 1 = Jan, 2 = Feb, ..., 12 = Dec
	if statementMonth == 2:
		dayToQuery = '28'
	elif statementMonth == 4 or statementMonth == 6 or statementMonth == 9\
		or statementMonth == 11:
		dayToQuery = '30'
	else:
		dayToQuery = '31'

	yearToQuery = str(statementYear)
	monthToQuery = '%02d'%statementMonth

	dateToQuery = yearToQuery+'-'+monthToQuery+'-'+dayToQuery
	return dateToQuery


# takes a number in KB and returns the number in GB
def kbToGb(num):
	return '%.2f' % ((num*(2**10))/float(2**30))


# method that takes a dictionary (see createUsrStorageDict() method) as an argument
# and 'zero-pads' newly added users prior to their add date
def zeroPadNewUsers(storageDict,statementMonth,statementYear):
	# variable to hold all users of a project as of the last day of database
	# query (the dictionary contains data collected from database)
	currentUsers=[]

	# loop through all users as of the last day of the statement month
	# see getQueryDate() method
	# for user in storageDict[Months[statementMonth]][getQueryDate(statementMonth,statementYear)].keys():
	for user in storageDict[Months[statementMonth]]['2016-08-24'].keys(): # this is temporary, delete this line on or after 2016-09-01 and uncomment line above
		currentUsers.append(user)
	currentUsers.sort() # alphabetize list of users

	# these nested loops will check to ensure that every user in the list of
	# current users has an entry in every date stored in the dictionary (see
	# createUsrStorageDict() method for clarification), if there is not an
	# entry, one will be created and will store the value 0.0.  This will
	# ensure that the size of each sub-dictionary is the same size
	for i in range(1,statementMonth+1):
		dates=[]
		if Months[i] in storageDict:
			for date in storageDict[Months[i]].keys():
	 			dates.append(date)
				dates.sort()
			for user in currentUsers:
				for j in range(len(dates)):
					if user not in storageDict[Months[i]][dates[j]]:
						storageDict[Months[i]][dates[j]][user] = 0.0
	return storageDict


# method to remove users from the dicitionary (see createUsrStorageDict() method)
# if they are not found in the most recent date (i.e. they were removed prior to
# the end of the query dates)
def removeDeletedUsers(storageDict,statementMonth,statementYear):
	# loop through every user for every date for every month of data stored in
	# the dictionary (see createUsrStorageDict() method for details), and
	# checks to see if that user can be found in the most recent date of the
	# dictionary, if not then the user has been removed from the group and
	# all previous data entries for that user will be removed from the
	# dictionary.  This will ensure that the size of each sub-dictionary is the
	# same size.
	for i in range(1,statementMonth+1):
		if Months[i] in storageDict:
			for day in storageDict[Months[i]].keys():
				for userInQuestion in storageDict[Months[i]][day].keys():
					# if userInQuestion not in storageDict[Months[statementMonth]][getQueryDate(statementMonth,statementYear)].keys():
					if userInQuestion not in storageDict[Months[statementMonth]][date.today().strftime('%Y-%m-%d')].keys(): # this is temporary, delete this line on or after 2016-09-01 and uncomment line above
						del storageDict[Months[i]][day][userInQuestion]
	return storageDict


# method that queries the database and returns statistics for the project in
# the form of a list: [blockUsage, blockLimit, filesUsage].  This data will
# reflect storage usage as of the last day of the statementMonth for the
# entire project
def getProjectData(theAccount, statementMonth, statementYear):
	# the try, except, else statement establishes a connection with the database
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

		# call method to return the date of the last day of the month in 
		# YYYY-mm-dd format
		dateToQuery = getQueryDate(statementMonth,statementYear)

		#######################################################################
		# Until September 1, 2016 the date to query has to be the current day
		# This section can be removed on 2016-09-01
		dateToQuery = date.today().strftime("%Y-%m-%d") #'YYYY-MM-DD' format
		#######################################################################

		# mysql query statement
		query = ("SELECT DISTINCT blockUsage,blockLimit,filesUsage FROM datastorage "\
			+"WHERE sampleDate=%s and quotaType='FILESET' and name=%s")

		cursor.execute(query,(dateToQuery,'p_'+theAccount))

		blockUsage,blockLimit,filesUsage = cursor.fetchone()
		cursor.close()
		cnx.close()
		return [blockUsage,blockLimit,filesUsage]
		
		
# method that queries the database and returns statistics for all users for a
# specific project in the form of a list of tuples: 
# [(user1, blockUsage, filesUsage), (user2, blockUsage, filesUsage), ...]
# This information is only concerned with the last day of the statementMonth.
# The summation of the blockUsage and filesUsage should agree with numbers
# collected using getProjectData() method when the same parameters are passed
def getUsrData(theAccount, statementMonth, statementYear):
	# the try, except, else statement establishes a connection with the database
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

		# call method to return the date of the last day of the month in 
		# YYYY-mm-dd format
		dateToQuery = getQueryDate(statementMonth,statementYear)

		#######################################################################
		# Until September 1, 2016 the date to query has to be the current day
		# This section can be removed on 2016-09-01
		dateToQuery = date.today().strftime("%Y-%m-%d") #'YYYY-MM-DD' format
		#######################################################################

		# mysql query
		query = ("SELECT DISTINCT name, blockUsage,filesUsage "\
			+"FROM datastorage WHERE sampleDate=%s AND quotaType='USR' "\
			+"AND NOT name='root' AND filesetName=%s")

		try:
			cursor.execute(query,(dateToQuery,'p_'+theAccount))
		except:
			print("Database query was unsuccessful in getUsrData() method call!")
			exit(1)
		else:
			userList=[]
			for (name, blockUsage, filesUsage) in cursor:
				userList.append((name, blockUsage, filesUsage))
			# sorting the lists will alphabetize based on user's name
			# this sorting is critical for color coding charts
			userList.sort()

			cursor.close()
			cnx.close()
			return userList

# method that queries the database and returns statistics for all groups for a
# specific project in the form of a list of tuples: 
# [(group1, blockUsage, filesUsage), (group2, blockUsage, filesUsage), ...]
# This information is only concerned with the last day of the statementMonth.
# The summation of the blockUsage and filesUsage should agree with numbers
# collected using getProjectData() method when the same parameters are passed
def getGrpData(theAccount, statementMonth, statementYear):
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

		dateToQuery = getQueryDate(statementMonth,statementYear)

		query = ("SELECT DISTINCT name, blockUsage,filesUsage "\
			+"FROM datastorage WHERE sampleDate=%s AND quotaType='GRP' "\
			+"AND NOT name='root' AND filesetName=%s")

		cursor.execute(query,(dateToQuery,'p_'+theAccount))

		grpList=[]
		for (name, blockUsage, filesUsage) in cursor:
			grpList.append((name, blockUsage, filesUsage))
		grpList.sort()
				
		cursor.close()
		cnx.close()
		return grpList


# method that creates a python dictionary of the form:
# {'Jan': {'YYYY-01-01': {'user1': blockUsage, 'user2': blockUsage, ...}, 
#		   'YYYY-01-02': {'user1': blockUsage, 'user2': blockUsage, ...}, ...},
# ...
# ...
# {'Dec': {'YYYY-12-01': {'user1': blockUsage, 'user2': blockUsage, ...}, 
#		   'YYYY-12-02': {'user1': blockUsage, 'user2': blockUsage, ...}, ...},}
def createUsrStorageDict(theAccount,statementMonth,statementYear):
	# the try, except, else statement establishes a connection with the database
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

		# python dictionary object
		storageDict = {}                                                               

		# mysql query
		query = ("SELECT DISTINCT name, blockUsage "\
			+"FROM datastorage WHERE sampleDate=%s AND quotaType='USR' "\
			+"AND NOT name='root' AND filesetName=%s")

		# query database for every day of the year through the end of the
		# statementMonth only the user's name and the amount of data stored
		# will be collected and used to build the python dictionary
		for i in range(1,statementMonth+1):
			for j in range(1,32):
				month = '%02d'%i
				day='%02d'%j
				sDate=str(statementYear)+'-'+month+'-'+day
				
				# try to query the database, if no entry is found meeting the
				# query specifics(mostly concerned with the date), move on to
				# the next date
				try:
					cursor.execute(query,(sDate,'p_'+theAccount))
				except:
					continue
				else:
					if cursor.with_rows: # mysql query successfully returned something
						# build dictionary
						for (name,blockUsage) in cursor:
							if blockUsage is not None:
								if Months[i] not in storageDict:
									storageDict[Months[i]] = {sDate:{name:float(kbToGb(blockUsage))}}
								elif sDate not in storageDict[Months[i]]:
									storageDict[Months[i]][sDate] = {name:float(kbToGb(blockUsage))}
								elif name not in storageDict[Months[i]][sDate]:
									storageDict[Months[i]][sDate][name] = float(kbToGb(blockUsage))
		
		# ensure there is an entry for every current user for every valid date
		# this will place 0s in dates prior to initial entry for new users
		storageDict = zeroPadNewUsers(storageDict,statementMonth,statementYear)

		# remove users from the dicitionary if they are not found in the most
		# recent date (i.e. they were removed prior to the end of the query dates)
		storageDict = removeDeletedUsers(storageDict,statementMonth,statementYear)
		
		cursor.close()
		cnx.close()
		return storageDict



# this method will make a call to the createUsrStorageDict() method and then
# extract the relevent information from the python dictionary created.
# getDailyData() will return a list of 2 lists: [usage, dates]
# usage is a list of lists.  Each individual list represents the amount of data
# stored on Bighorn for an individual user.  Each individual floating point
# value in the list is the amount of data (in GB) that was stored by that user
# on a specific day.
# dates is a list of dates.  Each entry in the individual user's storage list
# directly correlates to the date in the same position in the dates list.
def getDailyData(theAccount, statementMonth, statementYear):
	usage=[] # in the form [[user1data],[user2data],[user3data],...]
	dates=[]     

	# get current storage dictionary (see createUsrStorageDict() for details)
	# storageDict = createUsrStorageDict(theAccount,statementMonth,statementYear)
	storageDict = createUsrStorageDict(theAccount,8,statementYear) # this is temporary, delete this line on or after 2016-09-01 and uncomment line above

	# add all of the dates stored in the dictionary to list 'dates', then sort
	# for date in storageDict[Months[statementMonth]].keys():
	for date in storageDict['Aug'].keys(): # this is temporary, delete this line on or after 2016-09-01 and uncomment line above
		dates.append(date)
	dates.sort()
	# add all users to a list 'users', then sort
	# this ensures that all color coding in legend remains constant throughout
	users=[]
	# for user in storageDict[Months[statementMonth]][dates[len(dates)-1]].keys():
	for user in storageDict['Aug'][dates[len(dates)-1]].keys(): # this is temporary, delete this line on or after 2016-09-01 and uncomment line above
		users.append(user)
	users.sort()
	for userIndex in range(len(users)):
		userStorage=[]
		for i in range(len(dates)):
			# userStorage.append(storageDict[Months[statementMonth]][dates[i]][users[userIndex]])
			userStorage.append(storageDict['Aug'][dates[i]][users[userIndex]]) # this is temporary, delete this line on or after 2016-09-01 and uncomment line above
		usage.append(userStorage)

	return [usage,dates]



# this method will make a call to the createUsrStorageDict() method and then
# extract the relevent information from the python dictionary created.
# getMonthlyData() will return a list of 2 lists: [usage, months]
# usage is a list of lists.  Each individual list represents the amount of data
# stored on Bighorn for an individual user.  Each individual floating point
# value in the list is the amount of data (in GB) that was stored by that user
# on a specific day.
# dates is a list of dates.  Each entry in the individual user's storage list
# directly correlates to the date in the same position in the dates list.
def getMonthlyData(theAccount, statementMonth, statementYear):
	usage=[]
	months=[]

	# get current storage dictionary (see createUsrStorageDict() for details)
	# storageDict = createUsrStorageDict(theAccount,statementMonth,statementYear)
	storageDict = createUsrStorageDict(theAccount,8,statementYear) # this is temporary, delete this line on or after 2016-09-01 and uncomment line above

	# fill 'months' list with valid months (remember, database was created in
	# August 2016, so no data is available before then)
	for i in range(1,13):
		monthlyUsage=[]
		if Months[i] in storageDict:
			months.append(Months[i])
			
	# add all users to a list 'users', then sort
	# this ensures that all color coding in legend remains constant throughout
	users=[]
	# for user in storageDict[Months[statementMonth]][getQueryDate(statementMonth,statementYear)]].keys():
	for user in storageDict['Aug'][date.today().strftime("%Y-%m-%d")].keys(): # this is temporary, delete this line on or after 2016-09-01 and uncomment line above
		users.append(user)
	users.sort()

	for user in users:
		# variable to hold a list of data for a single user.
		usageData = []
		for month in months:
			# usageData.append(storageDict[month][getQueryDate(MonthNumber[month],statementYear)][user])
			usageData.append(storageDict[month][date.today().strftime('%Y-%m-%d')][user]) # this is temporary, delete this line on or after 2016-09-01 and uncomment line above
		usage.append(usageData)

	return [usage,months]
