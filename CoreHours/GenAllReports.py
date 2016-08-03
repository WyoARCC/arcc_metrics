#!/usr/bin/python

from GenAllOutputFiles import GenAll
from CoreHoursByMonthReport_V8 import GenReport
import ipaShowTools
import os
from datetime import date
import argparse


# argparser and auto generate help

parser = argparse.ArgumentParser(
	description="generate a monthly usage statement as a .pdf document and"\
	+" sends an email to the group's PI with the document attached.  The"\
	+" document contains information regarding the number of jobs submitted"\
	+" by the group as well as the number of CPU hours used on Mt. Moran.")

parser.add_argument("-m", "--month", type=int, choices=[1,2,3,4,5,6,7,8,9,10,11,12],
	help="the month in which the usage report will be generated for, "\
	+"if this option is not selected the most recent month will be used")

args = parser.parse_args()

if args.month == None or args.month >= int(date.today().strftime("%m")):
	statementMonth = int(date.today().strftime("%m"))-1
else:
	statementMonth = args.month

# in the case the current month is Jan, the statement will be generated for Dec
if statementMonth == 0:
	statementMonth = 12

Months = {1:'Jan', 2:'Feb', 3:'Mar', 4:'April', 5:'May', 6:'June', 7:'July', 
			8:'Aug', 9:'Sept', 10:'Oct', 11:'Nov', 12:'Dec'}

theDateYYYYmmdd = date.today().strftime("%Y-%m-%d") #YYYY-mm-dd format

badGroups = ['bsa','taed'] # list of groups to ignore

accounts=GenAll(statementMonth)

activeGroups = ipaShowTools.activeGroups()


###############################################################################
# Debugging purposes
print 'Generating monthly statements for the month of %s' % Months[statementMonth]
# end debugging
###############################################################################


for account in accounts:
	if (activeGroups.__contains__(account) and\
		not(badGroups.__contains__(account))):

		loginName = ipaShowTools.getPI(account)
		fullName = ipaShowTools.getName(loginName)
		email = ipaShowTools.getEmail(loginName)
		GenReport(account, fullName, statementMonth)

###############################################################################
# debugging section, remove from final version

		print '\nGroup: %s' % account
		print 'PI: %s, %s' % (loginName, fullName)
		print 'Email: %s\n' % email

		# myEmail = 'jclay6@uwyo.edu'

		# bashCommand="mail -s 'Mt Moran Usage Report for "+account+"' "\
		# 	+"-a "+account+"_report_"+theDateYYYYmmdd+".pdf "\
		# 	+"-r arcc-info@uwyo.edu "\
		# 	+"-c ksodhi@uwyo.edu,ceastma2@uwyo.edu "\
		# 	+myEmail\
		# 	+" <<< 'Dear "+fullName+",\n\n\tWe at ARCC hope that our"\
		# 	+" services, including the use of Mt. Moran, have been beneficial"\
		# 	+" to you and your research team.  Attached you will find a"\
		# 	+" monthly usage statement for the group, "+account+".  As this"\
		# 	+" usage report is a work in progress, please let us know if"\
		# 	+" there is any issues with the .pdf document.  We appreciate any"\
		# 	+" feedback that you may have.  We plan on adding additional"\
		# 	+" information to the statement to include the Bighorn filesystem"\
		# 	+" usage, special job requests, and others.  You may reply to"\
		# 	+" this email with questions or comments.\n\nGeneral ARCC"\
		# 	+" questions can also be emailed to arcc-info@uwyo.edu and"\
		# 	+" service requests may be opened by emailing arcc-help@uwyo.edu."\
		# 	+"\n\nThe ARCC Team'"

		# if not(email == ''):
		# 	os.system(bashCommand)
		
# end of debugging
###############################################################################


		# Send emails to all PIs

		# bashCommand="mail -s 'Mt Moran Usage Report for "+account+"' "\
		# 	+"-a "+account+"_report_"+theDateYYYYmmdd+".pdf "\
		# 	+"-r arcc-info@uwyo.edu "\
		# 	+"-b arcc-admin@uwyo.edu,Jared.Baker@uwyo.edu "\
		# 	+email\
		# 	+" <<< 'Dear "+fullName+",\n\n\tWe at ARCC hope that our"\
		# 	+" services, including the use of Mt. Moran, have been beneficial"\
		# 	+" to you and your research team.  Attached you will find a"\
		# 	+" monthly usage statement for the group, "+account+".  As this"\
		# 	+" usage report is a work in progress, please let us know if"\
		# 	+" there is any issues with the .pdf document.  We appreciate any"\
		# 	+" feedback that you may have.  We plan on adding additional"\
		# 	+" information to the statement to include the Bighorn filesystem"\
		# 	+" usage, special job requests, and others.  You may reply to"\
		# 	+" this email with questions or comments.\n\nGeneral ARCC"\
		# 	+" questions can also be emailed to arcc-info@uwyo.edu and"\
		# 	+" service requests may be opened by emailing arcc-help@uwyo.edu."\
		# 	+"\n\nThe ARCC Team'"
		
		# if not(email == ''):
		# 	os.system(bashCommand)

for i in range(1,statementMonth+1):
	bashCommand = 'rm *'+Months[i]+'.out'
	os.system(bashCommand)

os.system('mkdir '+Months[statementMonth]+'Reports')
os.system('mv *_report_'+theDateYYYYmmdd+'.pdf '\
	+Months[statementMonth]+'Reports/')