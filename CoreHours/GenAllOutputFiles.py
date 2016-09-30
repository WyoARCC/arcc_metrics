###############################################################################
# mysqlTools.py
# Jeremy Clay
# Aug 20, 2016
# 
# The GenAll() method will open a file (all_Jan_T.out for example) which was
# generated on Mt. Moran and contains cpu time used for every job ran by every
# project, and distributes the data across new files, one for each project.
# When finished there will be multiple files for every project, one for each
# month.  Each file will contain cpu time usage data for every job ran by that
# project in that month.  The data in these files will used by the GenReport()
# method in CoreHoursByMonthReport.py to generate monthly .pdf usage reports.
#
# The GenAll() method also produces a list of all of the projects(accounts)
# that produced any data when sacct command was ran on Mt. Moran to collect the
# cpu usage data.  This list is returned my the method.
# 
# Dependencies:	
###############################################################################

try:
    from sets import Set
except ImportError:
    Set = set
import os

Months = {1:'Jan', 2:'Feb', 3:'Mar', 4:'April', 5:'May', 6:'June', 7:'July',
	8:'Aug', 9:'Sept', 10:'Oct', 11:'Nov', 12:'Dec'}

def GenAll(statementMonth):
	# variable to hold a collection of all of the project names
	accounts = Set()

	# loop through all of the 'all_<month>_T.out' files.  The data in these
	# files appears in multiple lines like the following:
	#
	#	mtmoran|taed|rhermans|41472000
	#	mtmoran|evolvingai|hmengist|27358
	#
	# each line represents a seperate job ran on Mt. Moran in that month
	# The four seperate field seperated by '|' are Cluster, Account, User, and
	# CPU time (in seconds)
	for i in range(1,statementMonth+1):
		fileToOpen='all_'+Months[i]+'_T.out'
		jobfile=open(fileToOpen,'r')
		# parse the file by each line and store them in a list - 'jobs'
		jobs=jobfile.read().strip().split('\n')
		jobfile.close()

		# loop through the new list - 'jobs', and append the job 
		# information to seperate account files (evolvingai_Jan.out for
		# example).  Also add the account name to the collection of account
		# names.  We are not worried about duplicate entries in the collection,
		# this will be addressed later by casting the collection as a list.   
		for job in jobs:
			account=job.split('|')[1]
			accounts.add(account)
			f=open(account+'_'+Months[i]+'.out','a')
			f.write(job+'\n')
			f.close()

	return list(accounts)
	