###############################################################################
# GenAllReports.py
# Jeremy Clay
# Aug 20, 2016
# 
# 
# The main function of this file is to supply some tools to be able to create
# a graph using the matplotlib library, and insert it into a repotlab .pdf
# document.  
#
#
# The majority of this file was copied from:
# http://stackoverflow.com/questions/31712386/loading-matplotlib-object-into-reportlab
# the PdfImage() class definition as well as the form_xo_reader() method were
# copied directly from the website.  Credit to: Patrick Maupin who shared his
# solution.
#
#
# The make_chart() method is original code created by Jeremy Clay.  This method
# defines the matplotlib graph
# 
# Dependencies: 
###############################################################################

import cStringIO
import numpy as np
from matplotlib import pyplot as plt
from reportlab.platypus import Flowable
from reportlab.lib.units import inch
from pdfrw import PdfReader, PdfDict
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

# method copied from web.  See header for details
def form_xo_reader(imgdata):
    page, = PdfReader(imgdata).pages
    return pagexobj(page)

# class definition copied from web.  See header for details
class PdfImage(Flowable):
    def __init__(self, img_data, width=400, height=200):
        self.img_width = width
        self.img_height = height
        self.img_data = img_data

    def wrap(self, width, height):
        return self.img_width, self.img_height

    def drawOn(self, canv, x, y, _sW=0):
        if _sW > 0 and hasattr(self, 'hAlign'):
            a = self.hAlign
            if a in ('CENTER', 'CENTRE', TA_CENTER):
                x += 0.5*_sW
            elif a in ('RIGHT', TA_RIGHT):
                x += _sW
            elif a not in ('LEFT', TA_LEFT):
                raise ValueError("Bad hAlign value " + str(a))
        canv.saveState()
        img = self.img_data
        if isinstance(img, PdfDict):
            xscale = self.img_width / img.BBox[2]
            yscale = self.img_height / img.BBox[3]
            canv.translate(x, y)
            canv.scale(xscale, yscale)
            canv.doForm(makerl(canv, img))
        else:
            canv.drawImage(img, x, y, self.img_width, self.img_height)
        canv.restoreState()


# This method is the main method call of this file, it creates a matplotlib
# pyplot figure (fig = plt.figure()) and uses it along with the above method
# and class to create chart that can be used in a reportlab .pdf document.
# The chart will include two distinct sets of data on the same plot.  One set
# of data will be the number of CPU hours used on Mt. Moran and will use the
# left y-axis.  The second set of data will be the number of jobs ran on Mt.
# Moran, this data will use the right-hand y-axis.
def make_chart(xLabels,y1,y2,statementMonth):
    # y1a and y2a are lists that are only used to calculate the trendlines for
    # the two different sets of data.  These two lists will not include months
    # of the year beyond the statementMonth.  This prevents the zeros stored
    # for these months from being included in the calculations, creating a more
    # accurate trendline for the given data.
    y1a=[]
    y2a=[]
    for i in range(statementMonth+1):
        y1a.append(y1[i])
        y2a.append(y2[i])

    # create a matplotlib plot figure
    fig = plt.figure(figsize=(9,5))

    width=0.4

    ###########################################################################
    # Plot the CPU hours data onto the figure
    cpu_hours_plot = plt.bar(np.arange(len(y1)), y1, align='edge', width=width,
        color='r')
    
    label1 = plt.ylabel("CPU Hours Used", fontsize =20, color='red')
    
    for i in plt.gca().get_yticklabels():
        i.set_color("red")
    ###########################################################################

    ###########################################################################
    # Create and plot the trendline for the CPU hour data.  Include the 
    # equation of the line on the plot
    cpu_slope, cpu_intercept = np.polyfit(np.arange(len(y1a)), y1a, 1)
    trendline_cpu = cpu_intercept + (cpu_slope * np.arange(len(y1)))
    fit_label_cpu = 'Linear fit ({0:.2f})'.format(cpu_slope)

    plt.plot(np.arange(len(y1)), trendline_cpu, color='red', linestyle='--',
        label=fit_label_cpu)
    
    plt.ylim(ymin = 0)

    plt.annotate('CPUH_Trend = (%d)(x) + %d' % (cpu_slope,cpu_intercept),
        (0.05, 1.08), xycoords='axes fraction', fontsize=15, color='r')
    ###########################################################################
    
    # twinx() establishes side-by-side plots of the two different sets of data
    plt.twinx()
    
    # label the x-axis
    plt.xticks(np.arange(len(y1))+width, xLabels, size='small')

    ###########################################################################
    # Plot the number of jobs data onto the figure
    num_jobs_plot = plt.bar(np.arange(len(y2))+width, y2, align='edge',
        width=width, color='b')
    
    label2 = plt.ylabel("Number of Jobs", fontsize =20, color='blue')
    
    for i in plt.gca().get_yticklabels():
        i.set_color("blue")
    ###########################################################################

    ###########################################################################
    # Create and plot the trendline for the number of jobs data.  Include the 
    # equation of the line on the plot
    job_slope, job_intercept = np.polyfit(np.arange(len(y2a)), y2a, 1)
    trendline_job = job_intercept + (job_slope * np.arange(len(y2)))
    fit_label_job = 'Linear fit ({0:.2f})'.format(job_slope)

    plt.plot(np.arange(len(y2)), trendline_job, color='blue', linestyle='--',
        label=fit_label_job)
    
    plt.ylim(ymin = 0)

    plt.annotate('NumJobs_Trend = (%d)(x) + %d' % (job_slope,job_intercept),
        (0.05, 1.03), xycoords='axes fraction', fontsize=15, color='b')
    ###########################################################################

    # create a plot legend
    plt.legend([cpu_hours_plot, num_jobs_plot], ['CPU Hours', 'Number of Jobs'])

    # next 6 lines copied from a stackoverflow webpage.  See header for details
    imgdata = cStringIO.StringIO()
    fig.savefig(imgdata, format='pdf')
    imgdata.seek(0)
    reader = form_xo_reader
    image = reader(imgdata)
    img = PdfImage(image, width=6.15*inch, height=3.05*inch)
    
    return img