###############################################################################
# UsageReportTools.py
# Jeremy Clay
# July 14, 2016
# 
# Contains tools needed to generate a monthly usage report of Mt Moran.
# This file will need to be included in the CoreHoursByMonthReport.py file.
# The reportlab library for python will need to be installed first.
# 
# 
# 
###############################################################################


# Libraries
from reportlab.platypus import *
from reportlab.graphics.shapes import Drawing, Circle
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.textlabels import Label
from reportlab.lib.units import inch
from reportlab.lib import colors

# A list of about 40 colors.  Used for coloring charts and legends
colorList = [colors.purple, colors.yellow, colors.slategrey, colors.orange,
			colors.red, colors.skyblue, colors.plum, colors.lime,
			colors.deeppink, colors.cyan, colors.azure, colors.orangered,
			colors.mediumslateblue, colors.green, colors.blue,
			colors.blueviolet, colors.goldenrod, colors.aquamarine,
			colors.lavenderblush, colors.powderblue, colors.tomato,
			colors.salmon, colors.peachpuff, colors.tan, colors.lemonchiffon,
			colors.lightpink, colors.indianred, colors.mediumorchid,
			colors.fuchsia, colors.cadetblue, colors.cornflower, 
			colors.palevioletred, colors.hotpink, colors.silver, 
			colors.yellowgreen, colors.thistle, colors.peru, colors.gold,
			colors.rosybrown]


# Returns a drawing object of the legend for the charts
def legendout(labels, isCPUH=True): # labels is a list
	drawing = Drawing(inch, 3*inch) if isCPUH else Drawing(2.5*inch, 3*inch)
	legend = Legend()
	legend.alignment = 'right'
	legend.x = 0 if isCPUH else 0.25*inch
	legend.y = 2.75*inch
	legend.columnMaximum = 25 if isCPUH else 10
	colorNamePairs = []
	
	# ensure legend and chart color coding matches (similar loop in
	# graphout_pie, graphout_bar and graphout_stackedBar methods)
	for i in range(len(labels)):
		colorNamePairs.append([colorList[i],labels[i]])
	
	legend.colorNamePairs = colorNamePairs
	drawing.add(legend)
	return drawing


# Returns a drawing object of a pie graph
def graphout_pie(data, labels, physicalSize): # data and labels are both lists of same size
	drawing = Drawing(physicalSize*inch, physicalSize*inch)
	pc = Pie()
	pc.x = .125*inch
	pc.y = .125*inch
	pc.width = (physicalSize-0.25)*inch
	pc.height = (physicalSize-0.25)*inch
	pc.data = data
	pc.labels = None
	pc.slices.strokeWidth = 0.5
	
	# ensure pie chart and legend coloring matches
	for i in range(len(labels)):
		pc.slices[i].fillColor = colorList[i]

	drawing.add(pc)
	return drawing


# Returns a drawing object of a bar chart
def graphout_bar(CPUH_data, storage_data, labels):
	drawing = Drawing(6*inch, 1.5*inch)
	bar = VerticalBarChart()
	bar.x = 50
	bar.y = 10
	data = [CPUH_data,storage_data]
	bar.data = data
	bar.categoryAxis.labels.boxAnchor = 'ne'
	bar.categoryAxis.labels.dx = -2
	bar.categoryAxis.labels.dy = -2
	bar.categoryAxis.labels.angle = 45
	bar.categoryAxis.categoryNames = labels
	
	# ensure bar chart and legend coloring matches
	for i in range(len(data)):
		bar.bars[i].fillColor = colorList[i]

	drawing.add(bar)
	return drawing


# Returns a drawing object of a bar chart
# data should be of form [[user1data],[user2data],...,[userNdata]]
# [userdata] = [date1data,date2data,...,dateNdata]
# labels is a list of dates (or months) that correlate to the data
# labels = [date1,date2,...,dateN]
def graphout_stackedBar(data, labels, X, Y):
	drawing = Drawing(X*inch, Y*inch)
	bar = VerticalBarChart()
	bar.x = 50
	bar.y = 50
	bar.width = (X-2)*inch
	bar.height = (Y-1)*inch
	bar.data = data
	bar.categoryAxis.style='stacked'
	bar.categoryAxis.labels.boxAnchor = 'ne'
	bar.categoryAxis.labels.dx = -2
	bar.categoryAxis.labels.dy = -2
	bar.categoryAxis.labels.angle = 45
	bar.categoryAxis.categoryNames = labels

	# ensure bar chart and legend coloring matches
	for i in range(len(data)):
		bar.bars[i].fillColor = colorList[i]
	
	yLabel = Label()
	yLabel.setOrigin(0, 50)
	yLabel.boxAnchor = 'c'
	yLabel.angle = 90
	yLabel.setText('Data Storage [GB]')
	yLabel.fontSize=16
	yLabel.dy = 1.25*inch
	drawing.add(yLabel)
	drawing.add(bar)
	return drawing


# returns a table that summarizes Mt. Moran usage for the month and ytd
def computeTableout(data): # data is a list of tuples (each tuple is another line)
	header = [['User', 'Jobs(m)', 'Jobs(YTD)', 'CPUH(m)', 'CPUH(YTD)']]
	
	# variables to hold summation totals of all categories
	totalJobs_month = 0
	totalJobs_YTD = 0
	totalCPU_month = 0
	totalCPU_YTD = 0

	# loop to sum totals
	for i in range(len(data)):
		totalJobs_month += data[i][1]
		totalJobs_YTD += data[i][2]
		totalCPU_month += data[i][3]
		totalCPU_YTD += data[i][4]
	
	totals = [['Totals', totalJobs_month, totalJobs_YTD, totalCPU_month,
				totalCPU_YTD]]
	t=Table(header + data + totals)

	t.setStyle(TableStyle([('ALIGN',(1,1),(4,len(data)+1),'RIGHT'),
		('FONT',(0,len(data)+1),(4,len(data)+1),'Helvetica-Bold'),
		('LINEBELOW',(0,0),(4,0),1,colors.black),
		('LINEABOVE',(0,len(data)+1),(4,len(data)+1),1,colors.black),
		('LINEBELOW',(0,len(data)+1),(4,len(data)+1),1,colors.black),]))

	return t


def kbToGb(num):
	return '%.2f' % ((num*(2**10))/float(2**30))

	# returns a table
def storageTableout(account,projectData,userData): # 
	header = [['User', 'Usage(GB)', 'Quota(GB)', '% Used', 'File Usage']]
	percentage = '%.2f' % (100*projectData[0]/float(projectData[1]))
	
	projectTableEntry = [[account,kbToGb(projectData[0]),
		kbToGb(projectData[1]),percentage,(projectData[2]-1)]]
	
	userTableEntry = []
	for (user,blockUsage,filesUsage) in userData:
		percentage = '%.2f' % (100*blockUsage/float(projectData[1]))
		userTableEntry.append([user,kbToGb(blockUsage),0,percentage,filesUsage])

	t=Table(header + userTableEntry + projectTableEntry)

	t.setStyle(TableStyle([('ALIGN',(1,1),(4,len(userData)+1),'RIGHT'),
		('FONT',(0,len(userData)+1),(4,len(userData)+1),'Helvetica-Bold'),
		('LINEBELOW',(0,0),(4,0),1,colors.black),
		('LINEABOVE',(0,len(userData)+1),(4,len(userData)+1),1,colors.black),
		('LINEBELOW',(0,len(userData)+1),(4,len(userData)+1),1,colors.black),]))

	return t
