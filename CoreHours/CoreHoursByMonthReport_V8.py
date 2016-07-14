#!/usr/bin/python/

import UsageReportTools_V8 as Tools
import matplotlibToReportlab as mtr

from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Frame, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet

account = 'evolvingai' # needs to be automatically set
PrncplInvst = 'jclune' # needs to be automatically set

Months = {1:'Jan', 2:'Feb', 3:'Mar', 4:'April', 5:'May', 6:'June', 7:'July', 
			8:'Aug', 9:'Sept', 10:'Oct', 11:'Nov', 12:'Dec'}

CPUHUsageDict = {}
NumJobsDict = {}

for i in range(1,7):
	fileToOpen=account+'_'+Months[i]+'.out'

	jobfile=open(fileToOpen,'r')

	jobs=jobfile.read().strip().split('\n')

	jobfile.close()


	for job in jobs:
		group=job.split('|')[2]
		coreSec=float(job.split('|')[3])
		coreHrs=coreSec/3600.0
		month=Months[i]
		if group != '':
			if month not in CPUHUsageDict:
				CPUHUsageDict[month] = {group:coreHrs}
				NumJobsDict[month] = {group:1}
			elif group not in CPUHUsageDict[month]:
				CPUHUsageDict[month][group] = coreHrs
				NumJobsDict[month][group] = 1
			else:
				CPUHUsageDict[month][group] += coreHrs
				NumJobsDict[month][group] += 1


monthly = {}
YTD = {}
ComputeSummary = {'Jan':0, 'Feb':0, 'Mar':0, 'April':0, 'May':0, 'June':0, 
					'July':0, 'Aug':0, 'Sept':0, 'Oct':0, 'Nov':0, 'Dec':0}

NumJobSummary = {'Jan':0, 'Feb':0, 'Mar':0, 'April':0, 'May':0, 'June':0, 
					'July':0, 'Aug':0, 'Sept':0, 'Oct':0, 'Nov':0, 'Dec':0}

for month in CPUHUsageDict.keys():
#	print '\t\t',month
	monthlyCPUHTotal=0
	monthlyJobTotal=0
	for group in CPUHUsageDict[month].keys():
		if group not in YTD:
			YTD[group] = [NumJobsDict[month][group], CPUHUsageDict[month][group]]
			if CPUHUsageDict['June'].get(group):
				monthly[group] = [NumJobsDict['June'][group], CPUHUsageDict['June'][group]]
		else:
			YTD[group][0] += NumJobsDict[month][group]
			YTD[group][1] += CPUHUsageDict[month][group]
#		print '\t\t\t%s: %f' % (group,UsageDict[cluster][account][month][group])
		monthlyCPUHTotal += CPUHUsageDict[month][group]
		monthlyJobTotal += NumJobsDict[month][group]
#	print '\t\t%s Total: %f\n' % (month,monthlyCPUHTotal)
	ComputeSummary[month] = int(monthlyCPUHTotal)
	NumJobSummary[month] = monthlyJobTotal


width, height = 5, len(YTD)
computeSummaryData = [[0 for x in range(width)]for y in range(height)]

i = 0
for user in YTD.keys():
	computeSummaryData[i][0] = user
	computeSummaryData[i][2] = YTD[user][0]
	computeSummaryData[i][4] = int(YTD[user][1])
	if monthly.get(user):
		computeSummaryData[i][1] = monthly[user][0]
		computeSummaryData[i][3] = int(monthly[user][1])
	i += 1


computeSummaryLabels = []
NumJob_data = []
CPUH_data = []

for i in range(1,13):
	computeSummaryLabels.append(Months[i])
	CPUH_data.append(ComputeSummary[Months[i]])
	NumJob_data.append(NumJobSummary[Months[i]])


finalUsers = []
finalMonthlyusage = []
finalYTDUsage = []
for i in range(len(computeSummaryData)):
	finalUsers.append(computeSummaryData[i][0])
	finalMonthlyusage.append(computeSummaryData[i][3])
	finalYTDUsage.append(computeSummaryData[i][4])


c = Canvas('report.pdf', letter)

styles = getSampleStyleSheet()
styleN = styles['Normal']
styleH = styles['Heading1']

HeaderFrame = Frame(inch, 9*inch, 6.5*inch, inch, showBoundary=0)
ComputeSummaryFrame = Frame(inch, 5.5*inch, 4*inch, 3.5*inch, showBoundary=0)
CPUHFrame1 = Frame(5*inch, 7.25*inch, 1.5*inch, 1.75*inch, showBoundary=0)
CPUHFrame2 = Frame(5*inch, 5.5*inch, 1.5*inch, 1.75*inch, showBoundary=0)
LegendFrame = Frame(6.5*inch, 5.5*inch, inch, 3.5*inch, showBoundary=0)
ComputeTrendFrame = Frame(inch, 2.25*inch, 6.5*inch, 3.25*inch, showBoundary=0)
StorageSummaryFrame = Frame(inch, 1*inch, 6.5*inch, 1.25*inch, showBoundary=0)


Title = "ARCC Mt Moran Usage Statement"
head_info = []
head_info.append(Paragraph(Title, styleH))
head_info.append(Paragraph("Project: " + account, styleN))
head_info.append(Paragraph("Principle Investigator: " + PrncplInvst, styleN))
HeaderFrame.addFromList(head_info, c)

computeSummary_info = []
computeSummary_info.append(Paragraph("Compute Summary (%s, %s)" 
	% ('June','2016'), styleN))
computeSummary_table = Tools.tableout(computeSummaryData)
computeSummary_info.append(computeSummary_table)
ComputeSummaryFrame.addFromList(computeSummary_info, c)

monthlyCPUH_info = []
#usage_chart = Tools.graphout_pie(data, labels)
usage_chart = Tools.graphout_pie(finalMonthlyusage, finalUsers)
monthlyCPUH_info.append(Paragraph("CPUH (month)", styleN))
monthlyCPUH_info.append(usage_chart)
CPUHFrame1.addFromList(monthlyCPUH_info, c)

ytdCPUH_info = []
#ytdUsage_chart = Tools.graphout_pie(dataYTD, labelsYTD)
ytdUsage_chart = Tools.graphout_pie(finalYTDUsage, finalUsers)
ytdCPUH_info.append(Paragraph("CPUH (ytd)", styleN))
ytdCPUH_info.append(ytdUsage_chart)
CPUHFrame2.addFromList(ytdCPUH_info, c)

legend_info = []
pieChartLegend = Tools.legendout(finalUsers)
#legend_info.append(Paragraph('Legend', styleN))
legend_info.append(pieChartLegend)
LegendFrame.addFromList(legend_info, c)

computeTrend_info = []
#computeTrend_chart = Tools.graphout_bar(CPUH_data, NumJob_data, computeSummaryLabels)
chart = mtr.make_chart(computeSummaryLabels,CPUH_data,NumJob_data)
computeTrend_info.append(Paragraph('Compute Summary Trends (CPUH)', styleN))
#computeTrend_info.append(computeTrend_chart)
computeTrend_info.append(chart)
ComputeTrendFrame.addFromList(computeTrend_info, c)

storageSummary_info = []
storageSummary_info.append(Paragraph('Storage Summary', styleN))
StorageSummaryFrame.addFromList(storageSummary_info, c)

c.save()