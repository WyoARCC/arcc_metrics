from sets import Set
import os

Months = {1:'Jan', 2:'Feb', 3:'Mar', 4:'April', 5:'May', 6:'June', 7:'July',
	8:'Aug', 9:'Sept', 10:'Oct', 11:'Nov', 12:'Dec'}

def GenAll(statementMonth):
	accounts = Set()
	for i in range(1,statementMonth+1):
		fileToOpen='all_'+Months[i]+'_T.out'
		jobfile=open(fileToOpen,'r')
		jobs=jobfile.read().strip().split('\n')
		jobfile.close()

		for job in jobs:
			account=job.split('|')[1]
			accounts.add(account)
			f=open(account+'_'+Months[i]+'.out','a')
			f.write(job+'\n')
			f.close()
	
	return list(accounts)