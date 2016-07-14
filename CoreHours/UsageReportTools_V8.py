###############################!/usr/bin/python

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
#import matplotlib
#import matplotlib.pyplot as plt
#import numpy as np

#import cStringIO

#from pdfrw import PdfReader
#from pdfrw.buildxobj import pagexobj
#from pdfrw.toreportlab import makerl

from reportlab.pdfgen.canvas import Canvas

from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend

from reportlab.platypus import *

#from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors

#from reportlab.rl_config import defaultPageSize

# A list of about 40 colors.  Used for coloring charts
colorList = [colors.purple, colors.yellow, colors.slategrey, colors.orange,
			colors.red, colors.skyblue, colors.plum, colors.lime,
			colors.deeppink, colors.cyan, colors.azure, colors.orangered,
			colors.mediumslateblue, colors.green, colors.blue,
			colors.blueviolet, colors.goldenrod, colors.crimson,
			colors.lavenderblush, colors.powderblue, colors.tomato,
			colors.salmon, colors.peachpuff, colors.tan, colors.lemonchiffon,
			colors.lightpink, colors.indianred, colors.mediumorchid,
			colors.fuchsia, colors.cadetblue, colors.cornflower, 
			colors.palevioletred, colors.hotpink, colors.silver, 
			colors.yellowgreen, colors.thistle, colors.peru, colors.gold,
			colors.aquamarine, colors.rosybrown]

# PAGE_HEIGHT=defaultPageSize[1]
# styles = getSampleStyleSheet()

# HeaderStyle = styles["Heading1"]
# ParaStyle = styles["Normal"]
# PreStyle = styles["Code"]

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
	pc.slices.popout = 2
	
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
	# right justify all of the table cells containing numbers
	t.setStyle(TableStyle([('ALIGN',(1,1),(4,len(data)+1),'RIGHT')]))
	return t

# def matplotGraph(x,y1,y2):
# 	width=0.4

# 	cpu_hours_plot = plt.bar(np.arange(len(y1)), y1, align='edge', width=width, color='r')
	
# 	label1 = plt.ylabel("CPU Hours Used", color='red')
	
# 	for i in plt.gca().get_yticklabels():
# 		i.set_color("red")
	
# 	cpu_slope, cpu_intercept = np.polyfit(np.arange(len(y1)), y1, 1)
# 	trendline_cpu = cpu_intercept + (cpu_slope * np.arange(len(y1)))
# 	fit_label_cpu = 'Linear fit ({0:.2f})'.format(cpu_slope)

# 	plt.plot(np.arange(len(y1)), trendline_cpu, color='red', linestyle='--', label=fit_label_cpu)
	
# 	plt.ylim(ymin = 0)

# 	plt.annotate('CPUH = (%d)(x) + %d' % (cpu_slope,cpu_intercept), (0.05, 0.98), xycoords='axes fraction', color='red')
	
# 	plt.twinx()
	
# 	plt.xticks(np.arange(len(y1))+width, x, size='small')

# 	num_jobs_plot = plt.bar(np.arange(len(y2))+width, y2, align='edge', width=width, color='b')
	
# 	label2 = plt.ylabel("Number of Jobs", color='blue')
	
# 	for i in plt.gca().get_yticklabels():
# 		i.set_color("blue")

# 	job_slope, job_intercept = np.polyfit(np.arange(len(y2)), y2, 1)
# 	trendline_job = job_intercept + (job_slope * np.arange(len(y2)))
# 	fit_label_job = 'Linear fit ({0:.2f})'.format(job_slope)

# 	plt.plot(np.arange(len(y2)), trendline_job, color='blue', linestyle='--', label=fit_label_job)
	
# 	plt.ylim(ymin = 0)

# 	plt.annotate('NumJobs = (%d)(x) + %d' % (job_slope,job_intercept), (0.05, 0.93), xycoords='axes fraction', color='blue')

# 	plt.legend([cpu_hours_plot, num_jobs_plot], ['CPU Hours', 'Number of Jobs'])
# 	plt.show()

	#imgdata = cStringIO.StringIO()

	#plt.savefig(imgdata, format='PDF')

	#pi = matplotlibInReportlab.PdfImage(imgdata)

