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
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
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


# Returns a drawing object of the legend for the pie charts
def legendout(labels): # labels is a list
	drawing = Drawing(inch, 3*inch)
	legend = Legend()
	legend.alignment = 'right'
	legend.x = 0
	legend.y = 2.75*inch
	legend.columnMaximum = 13
	colorNamePairs = []
	
	# ensure legend and pie chart coloring matches (similar loop in
	#	graphout_pie method)
	for i in range(len(labels)):
		colorNamePairs.append([colorList[i],labels[i]])
	
	legend.colorNamePairs = colorNamePairs
	drawing.add(legend)
	return drawing


# Returns a drawing object of a pie graph
def graphout_pie(data, labels): # data and labels are both lists of same size
	drawing = Drawing(1.25*inch, 1.25*inch)
	pc = Pie()
	pc.x = .125*inch
	pc.y = .125*inch
	pc.width = inch
	pc.height = inch
	pc.data = data
	pc.labels = None
	pc.slices.strokeWidth = 0.5
	
	# ensure pie chart and legend coloring matches (similar loop in 
	#	legendout method)
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
	drawing.add(bar)
	return drawing

# returns a table
def tableout(data): # data is a list of tuples (each tuple is another line)
	header = [['User', 'Jobs(m)', 'Jobs(YTD)', 'CPUH(m)', 'CPUH(YTD)']]
	
	totalJobs_month = 0
	totalJobs_YTD = 0
	totalCPU_month = 0
	totalCPU_YTD = 0

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
