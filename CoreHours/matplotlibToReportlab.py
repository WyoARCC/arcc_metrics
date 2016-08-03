import cStringIO
import numpy as np
from matplotlib import pyplot as plt
from reportlab.platypus import Flowable
from reportlab.lib.units import inch
from pdfrw import PdfReader, PdfDict
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl


def form_xo_reader(imgdata):
    page, = PdfReader(imgdata).pages
    return pagexobj(page)


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



def make_chart(x,y1,y2,statementMonth):
    y1a=[]
    y2a=[]
    for i in range(statementMonth+1):
        y1a.append(y1[i])
        y2a.append(y2[i])

    fig = plt.figure(figsize=(9,5))

    width=0.4

    cpu_hours_plot = plt.bar(np.arange(len(y1)), y1, align='edge', width=width,
        color='r')
    
    label1 = plt.ylabel("CPU Hours Used", fontsize =20, color='red')
    
    for i in plt.gca().get_yticklabels():
        i.set_color("red")
    
    cpu_slope, cpu_intercept = np.polyfit(np.arange(len(y1a)), y1a, 1)
    trendline_cpu = cpu_intercept + (cpu_slope * np.arange(len(y1)))
    fit_label_cpu = 'Linear fit ({0:.2f})'.format(cpu_slope)

    plt.plot(np.arange(len(y1)), trendline_cpu, color='red', linestyle='--',
        label=fit_label_cpu)
    
    plt.ylim(ymin = 0)

    plt.annotate('CPUH = (%d)(x) + %d' % (cpu_slope,cpu_intercept),
        (0.05, 1.08), xycoords='axes fraction', fontsize=15, color='r')
    
    plt.twinx()
    
    plt.xticks(np.arange(len(y1))+width, x, size='small')

    num_jobs_plot = plt.bar(np.arange(len(y2))+width, y2, align='edge',
        width=width, color='b')
    
    label2 = plt.ylabel("Number of Jobs", fontsize =20, color='blue')
    
    for i in plt.gca().get_yticklabels():
        i.set_color("blue")

    job_slope, job_intercept = np.polyfit(np.arange(len(y2a)), y2a, 1)
    trendline_job = job_intercept + (job_slope * np.arange(len(y2)))
    fit_label_job = 'Linear fit ({0:.2f})'.format(job_slope)

    plt.plot(np.arange(len(y2)), trendline_job, color='blue', linestyle='--',
        label=fit_label_job)
    
    plt.ylim(ymin = 0)

    plt.annotate('NumJobs = (%d)(x) + %d' % (job_slope,job_intercept),
        (0.05, 1.03), xycoords='axes fraction', fontsize=15, color='b')

    plt.legend([cpu_hours_plot, num_jobs_plot], ['CPU Hours', 'Number of Jobs'])

    imgdata = cStringIO.StringIO()
    fig.savefig(imgdata, format='pdf')
    imgdata.seek(0)
    reader = form_xo_reader
    image = reader(imgdata)
    img = PdfImage(image, width=6.15*inch, height=3.05*inch)
    
    return img