from datetime import date
import UsageReportTools_V8 as Tools
import matplotlibToReportlab as mtr
from GenAllOutputFiles import GenAll

from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Frame, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT

from mysqlTools import *


def GenReport(theAccount,PI,statementMonth):
	Months = {1:'Jan', 2:'Feb', 3:'Mar', 4:'April', 5:'May', 6:'June', 7:'July', 
				8:'Aug', 9:'Sept', 10:'Oct', 11:'Nov', 12:'Dec'}

	theDate01 = date.today().strftime("%B %d, %Y") #'month day, year' format
	theDate02 = date.today().strftime("%Y-%m-%d") #'YYYY-MM-DD' format
	account = theAccount
	PrncplInvst = PI


	CPUHUsageDict = {}
	NumJobsDict = {}

	for i in range(1,statementMonth+1):
		fileToOpen=account+'_'+Months[i]+'.out'

		try:
			jobfile=open(fileToOpen,'r')
		except:
			continue

		jobs=jobfile.read().strip().split('\n')

		jobfile.close()


		for job in jobs:
			group=job.split('|')[2]
			coreSec=float(job.split('|')[3])
			coreHrs=coreSec/3600.0
			month=Months[i]
			if not(group == ''):
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
		monthlyCPUHTotal=0
		monthlyJobTotal=0
		for group in CPUHUsageDict[month].keys():
			if group not in YTD:
				YTD[group] = [NumJobsDict[month][group], CPUHUsageDict[month][group]]
				try:
					if CPUHUsageDict[Months[statementMonth]].get(group):
						monthly[group] = [NumJobsDict[Months[statementMonth]][group],CPUHUsageDict[Months[statementMonth]][group]]
				except:
					monthly[group] = [0,0]
			else:
				YTD[group][0] += NumJobsDict[month][group]
				YTD[group][1] += CPUHUsageDict[month][group]
			monthlyCPUHTotal += CPUHUsageDict[month][group]
			monthlyJobTotal += NumJobsDict[month][group]
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


	c = Canvas(account+'_report_'+theDate02+'.pdf', letter)

	styles = getSampleStyleSheet()
	styleN = styles['Normal']
	styleI = styles['Italic']
	styleH1 = styles['Heading1']
	styleH2 = styles['Heading2']
	styleH2.alignment = TA_RIGHT
	styleH3 = styles['Heading3']
	styleH3.fontName='Helvetica-Bold'
	styleH3.fontSize=12

	HeaderFrame = Frame(inch, 9*inch, 6.5*inch, 1.5*inch, showBoundary=0)
	ComputeSummaryFrame = Frame(inch, 5.5*inch, 4*inch, 3.5*inch, showBoundary=0)
	CPUHFrame1 = Frame(5*inch, 7.25*inch, 1.5*inch, 1.75*inch, showBoundary=0)
	CPUHFrame2 = Frame(5*inch, 5.5*inch, 1.5*inch, 1.75*inch, showBoundary=0)
	LegendFrame = Frame(6.5*inch, 5.5*inch, inch, 3.5*inch, showBoundary=0)
	ComputeTrendFrame = Frame(inch, inch, 6.5*inch, 4.5*inch, showBoundary=0)


	Title = "ARCC Mt Moran Usage Statement"
	head_info = []
	head_info.append(Paragraph(theDate01, styleH2))
	head_info.append(Paragraph(Title, styleH1))
	head_info.append(Paragraph("Project: " + account, styleN))
	head_info.append(Paragraph("Principal Investigator: " + PrncplInvst, styleN))
	HeaderFrame.addFromList(head_info, c)

	computeSummary_info = []
	computeSummary_info.append(Paragraph("Compute Summary (%s, %s)" 
		% (Months[statementMonth],'2016'), styleH3))
	computeSummary_table = Tools.computeTableout(computeSummaryData)
	computeSummary_info.append(computeSummary_table)
	ComputeSummaryFrame.addFromList(computeSummary_info, c)

	monthlyCPUH_info = []
	mtMoranUsagePieChart = Tools.graphout_pie(finalMonthlyusage, finalUsers, 1.25)
	monthlyCPUH_info.append(Paragraph("CPUH (month)", styleN))
	monthlyCPUH_info.append(mtMoranUsagePieChart)
	CPUHFrame1.addFromList(monthlyCPUH_info, c)

	ytdCPUH_info = []
	mtMoranYtdUsagePieChart = Tools.graphout_pie(finalYTDUsage, finalUsers, 1.25)
	ytdCPUH_info.append(Paragraph("CPUH (ytd)", styleN))
	ytdCPUH_info.append(mtMoranYtdUsagePieChart)
	CPUHFrame2.addFromList(ytdCPUH_info, c)

	legend_info = []
	pieChartLegend = Tools.legendout(finalUsers)
	legend_info.append(pieChartLegend)
	LegendFrame.addFromList(legend_info, c)

	computeTrend_info = []
	chart = mtr.make_chart(computeSummaryLabels,CPUH_data,NumJob_data,statementMonth)
	computeTrend_info.append(chart)
	ComputeTrendFrame.addFromList(computeTrend_info, c)

	c.save() # This marks the end of the first page of the .pdf document

	# Starting the second page

	
	HeaderFrame = Frame(inch, 9*inch, 6.5*inch, 1.5*inch, showBoundary=0)
	StorageSummaryFrame = Frame(inch, 2.5*inch, 4.5*inch, 6.5*inch, showBoundary=0)
	PieChartFrame = Frame(5.5*inch, 6*inch, 2.5*inch, 3*inch, showBoundary=0)
	LegendFrame = Frame(5.5*inch, 2.5*inch, 2.5*inch, 3.5*inch, showBoundary=0)

	Title = "ARCC Bighorn Storage Statement"
	head_info = []
	head_info.append(Paragraph(theDate01, styleH2))
	head_info.append(Paragraph(Title, styleH1))
	head_info.append(Paragraph("Project: " + account, styleN))
	head_info.append(Paragraph("Principal Investigator: " + PrncplInvst, styleN))
	HeaderFrame.addFromList(head_info, c)

	projectData = getProjectData(theAccount,theDate02)
	userData = getUsrData(theAccount,theDate02)

	storageSummary_info = []
	storageSummary_info.append(Paragraph("Storage Summary (%s)" 
		% theDate01, styleH3))
	storageSummary_table = Tools.storageTableout(theAccount,projectData,userData)
	storageSummary_info.append(storageSummary_table)
	StorageSummaryFrame.addFromList(storageSummary_info, c)

	userList=[]
	usageList=[]

	for (user,blockUsage,filesUsage) in userData:
		userList.append(user)
		usageList.append(blockUsage)

	usage_info = []
	bighornStoragePieChart = Tools.graphout_pie(usageList, userList, 2.5)
	usage_info.append(Paragraph("Storage Usage", styleH3))
	usage_info.append(bighornStoragePieChart)
	PieChartFrame.addFromList(usage_info, c)

	legend_info = []
	pieChartLegend = Tools.legendout(userList, isCPUH=False)
	legend_info.append(pieChartLegend)
	LegendFrame.addFromList(legend_info, c)

	c.save() # This marks the end of the second page of the .pdf document

	# Starting the third page

	HeaderFrame = Frame(inch, 9*inch, 6.5*inch, 1.5*inch, showBoundary=0)
	MonthlyStorageChartFrame = Frame(inch, 5*inch, 5.5*inch, 4*inch, showBoundary=0)
	YtdStorageChartFrame = Frame(inch, inch, 5.5*inch, 4*inch, showBoundary=0)
	LegendFrame = Frame(6.5*inch, inch, inch, 8*inch, showBoundary=0)

	Title = "ARCC Bighorn Storage Statement (cont)"
	head_info = []
	head_info.append(Paragraph(theDate01, styleH2))
	head_info.append(Paragraph(Title, styleH1))
	head_info.append(Paragraph("Project: " + account, styleN))
	head_info.append(Paragraph("Principal Investigator: " + PrncplInvst, styleN))
	HeaderFrame.addFromList(head_info, c)

	monthlyStorageChart_info=[]
	# collect daily stats from the database
	dailyData=getDailyData(theAccount,'2016-08-17')
	bighornStorageBarChart=Tools.graphout_stackedBar(dailyData[0], dailyData[1])
	monthlyStorageChart_info.append(Paragraph("Daily Storage Summary for the "\
		+"month of %s" % Months[statementMonth], styleN))
	monthlyStorageChart_info.append(bighornStorageBarChart)
	MonthlyStorageChartFrame.addFromList(monthlyStorageChart_info, c)

#	ytdCPUH_info = []
#	ytdUsage_chart = Tools.graphout_pie(finalYTDUsage, finalUsers, 1.25)
#	ytdCPUH_info.append(Paragraph("CPUH (ytd)", styleN))
#	ytdCPUH_info.append(ytdUsage_chart)
#	CPUHFrame2.addFromList(ytdCPUH_info, c)
	
	storageLegend_info = []
	storageLegend = Tools.legendout(userList)
	legend_info.append(storageLegend)
	LegendFrame.addFromList(legend_info, c)
	



	c.save() # This marks the end of the third page of the .pdf document