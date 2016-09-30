###############################################################################
# ipaShowTools.py
# Jeremy Clay
# July 28, 2016
#
# 
#
#
###############################################################################


import subprocess

# function that will return a list of all active groups on Mt. Moran
def activeGroups():
	ipaCommand = "ipa group-show mountmoran --all | grep -i 'member groups'"

	try:
		ipaResults = subprocess.check_output(ipaCommand, shell=True)
		
		# from ipaResults, extract a string of all of the active groups
		# activeGroups = ipaResults.split(':')[1].strip() # this version works for Python 2.7
		activeGroups = ipaResults.decode('utf8').split(':')[1].strip() # this version works for Python 3.4

		# turn the string of comma seperated groups into a list
		listOfGroups = activeGroups.split(',')

		# strip leading and trailing whitespace from groupnames
		for i in range (len(listOfGroups)):
			listOfGroups[i] = str(listOfGroups[i].strip())

		return listOfGroups
	
	except:
		print ('The command: ('+ipaCommand+') failed.')
		exit(1)

	


# function that takes an argument of 'groupName' and returns a string of the
# login name of the principal investigator
def getPI(groupName):
	ipaCommand = "ipa group-show " + groupName + " --all | grep -i 'Description:'"

	try:
		ipaResults = subprocess.check_output(ipaCommand, shell=True)
		
		# from ipaResults, extract a string of the login name of the PI
		# loginName = ipaResults.split(':')[1].strip() # version works for Python 2.7
		loginName = ipaResults.decode('utf8').split(':')[1].strip()
		
		return str(loginName)
	
	except:
		print ('The command: ('+ipaCommand+') failed.')
		return ''
		#exit(1)

	


# function that takes an argument of 'loginName' and returns a string of the
# user's full name
def getName(loginName):
	ipaCommand = "ipa user-show " + loginName + " --all | grep -i 'Display name:'"

	try:
		ipaResults = subprocess.check_output(ipaCommand, shell=True)
		
		# from ipaResults, extract a string of the login name of the PI
		# displayName = ipaResults.split(':')[1].strip() # version works for Python 2.7
		displayName = ipaResults.decode('utf8').split(':')[1].strip()
		
		return str(displayName)

	except:
		print ('The command: ('+ipaCommand+') failed.')
		return ''
		#exit(1)

	


# function that takes an argument of 'loginName' and returns a string of the
# user's email address
def getEmail(loginName):
	ipaCommand = "ipa user-show " + loginName + " --all | grep -i 'Email address:'"

	try:
		ipaResults = subprocess.check_output(ipaCommand, shell=True)
		
		# from ipaResults, extract a string of the login name of the PI
		# email = ipaResults.split(':')[1].strip() # version works for Python 2.7
		email = ipaResults.decode('utf8').split(':')[1].strip()
		
		return str(email)
	
	except:
		print ('The command: ('+ipaCommand+') failed.')
		return ''
		#exit(1)
