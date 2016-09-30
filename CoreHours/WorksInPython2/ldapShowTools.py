###############################################################################
# ldapShowTools.py
# Jeremy Clay
# July 28, 2016
#
# 
#
#
###############################################################################


import subprocess
import os
import base64



# function that will return a list of all active groups on Mt. Moran
def activeGroups():
	ldapCommand = 'ldapsearch -LLL -H ldaps://arccidm1.arcc.uwyo.edu -x'\
		+' -b "cn=accounts,dc=arcc,dc=uwyo,dc=edu" "cn=mountmoran" |'\
		+' grep -i member:'

	activeGroups = []
	try:
		ldapResults = subprocess.check_output(ldapCommand, shell=True).strip()
		
		# from ldapResults, extract a string of all of the active groups
		members = ldapResults.split('\n')
		for i in range(len(members)):
			members[i] = members[i].split(':')[1].strip()
			members[i] = members[i].split(',')[0].strip()
			if members[i].split('=')[0] == 'cn':
				activeGroups.append(members[i].split('=')[1])

		return activeGroups
	
	except:
		print ('The command: ('+ldapCommand+') failed.')
		exit(1)



# function that takes an argument of 'groupName' and returns a string of the
# login name of the principal investigator
def getPI(groupName):
	ldapCommand = 'ldapsearch -LLL -H ldaps://arccidm1.arcc.uwyo.edu -x'\
		+' -b "cn=accounts,dc=arcc,dc=uwyo,dc=edu" "cn='+groupName+'" |'\
		+' grep -i description'

	try:
		ldapResults = subprocess.check_output(ldapCommand, shell=True).strip()
		
		# from ldapResults, extract a string of the login name of the PI
		loginName = ldapResults.split(':')[1].strip()
		if loginName == '':
			loginName = convertBase64(ldapResults)
		
		return loginName
	
	except:
		print ('The command: ('+ldapCommand+') failed.')
		return ''
		#exit(1)



# function that takes an argument of 'loginName' and returns a string of the
# user's gidNumber
def getUidNumber(uid):
	ldapCommand = 'ldapsearch -LLL -H ldaps://arccidm1.arcc.uwyo.edu -x'\
		+' -b "cn=accounts,dc=arcc,dc=uwyo,dc=edu" "uid='+uid+'"'\
		+' | grep -i gidNumber'

	try:
		ldapResults = subprocess.check_output(ldapCommand, shell=True)

		# from ldapResults, extract a string of the gidNumber of the PI
		uidNumber = ldapResults.split(':')[1].strip()
		
		return uidNumber

	except:
		print ('The command: ('+ldapCommand+') failed.')
		return ''



# function that takes an argument of 'gidNumber' and returns a string of the
# user's full name
def getName(uid):
	# gidNumber=str(gidNumber)
	ldapCommand = 'ldapsearch -LLL -H ldaps://arccidm1.arcc.uwyo.edu -x'\
		+' -b "cn=accounts,dc=arcc,dc=uwyo,dc=edu" "uid='+uid+'"'\
		+' | grep -i displayName'

	try:
		ldapResults = subprocess.check_output(ldapCommand, shell=True)
		
		# from ipaResults, extract a string of the login name of the PI
		displayName = ldapResults.split(':')[1].strip()
		
		return displayName

	except:
		print ('The command: ('+ldapCommand+') failed.')
		return ''
		#exit(1)

	

# function that takes an argument of 'gidNumber' and returns a string of the
# user's email address
def getEmail(uid):
	ldapCommand = 'ldapsearch -LLL -H ldaps://arccidm1.arcc.uwyo.edu -x'\
		+' -b "cn=accounts,dc=arcc,dc=uwyo,dc=edu" "uid='+uid+'" | grep -i mail'

	try:
		ldapResults = subprocess.check_output(ldapCommand, shell=True)
		
		# from ipaResults, extract a string of the login name of the PI
		email = ldapResults.split(':')[1].strip()
		
		return email

	except:
		print ('The command: ('+ldapCommand+') failed.')
		return ''



# function that returns the uid of the PI of a group.  This function deals with
# the fact that some ldap searches return data in the description field that is
# encoded with base64 and needs to be decoded.
def convertBase64(ldapResults):
	giberish=ldapResults.split(':')[2].strip()
	description=base64.b64decode(giberish)
	loginName=description.split(':')[0].strip()
	return loginName
