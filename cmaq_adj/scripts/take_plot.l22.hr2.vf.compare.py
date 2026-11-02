#!/home/cl3293/anaconda3/bin/python

#Script for scatter plot of LGRID comparison before and after vertical performance fix.

from netCDF4 import Dataset
#import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
from math import fsum, exp
#from random import uniform
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.backends.backend_pdf import PdfPages
from scipy import stats

#list_variables = ['NH3', 'ASO4I', 'ASO4J', 'ANO3I', 'ANO3J', 'ANH4I', 'ANH4J']
list_variables = ['NH3']

#NH3 active model sensitivities
#CHANGE1:
#NH3_file = '/mnt/HA/groups/cappsGrp/mm4862/CMAQ/CMAQ_adj_NH3/CMAQadjBnmkData/output_fd_base_NH3/LGRID.bwd_NH3.20070610'
#NH3_file = '/mnt/HA/groups/cappsGrp/mm4862/CMAQ/CMAQ_adj_NH3/CMAQadjBnmkData/output_fd_base_NH3/EM.LGRID.bwd_NH3.20070610'
#NH3_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day.l22.hr2/LGRID.bwd_NH3_new.20070610'
NH3_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day.l22.hr2.bugfree/LGRID.bwd_NH3.20070610'
     
NH3 = Dataset(NH3_file,mode='r', open=True)

adj_senshrbase_NH3 = NH3.variables['NH3'][:][:][:][:]
print("adj_senshrbase_NH3.shape", adj_senshrbase_NH3.shape)
adj_senshrbase_NH3 = adj_senshrbase_NH3[1:2,0:22,:,:] 
print("adj_senshrbase_NH3.shape", adj_senshrbase_NH3.shape)
print("adj_senshrbase_NH3.sum", np.nansum(adj_senshrbase_NH3))
ltime, llayer, lrow, lcol = adj_senshrbase_NH3.shape
layers = np.zeros([ltime, llayer, lrow, lcol])
for ll in range(0,22):
    layers[:,ll,:,:] = ll

#CHANGE2:
#NH3 model sensitivities
#NH3_file_vf = '/mnt/HA/groups/cappsGrp/mm4862/CMAQ/cmaq_adj/CMAQadjBnmkData/output_base_NH3_testTracer/LGRID.bwd_bnmk.20070610'
#NH3_file_vf = '/mnt/HA/groups/cappsGrp/mm4862/CMAQ/cmaq_adj/CMAQadjBnmkData/output_base_NH3_testTracer/EM.LGRID.bwd_bnmk.20070610'
#NH3_file_vf = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day.l22.hr2/LGRID.bwd_NH3.20070610'
NH3_file_vf = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day.l22.hr2.bugfree.vf/LGRID.bwd_NH3.20070610'
NH3_vf = Dataset(NH3_file_vf,mode='r', open=True)

adj_senshrbase_NH3_vf = NH3_vf.variables['NH3'][:][:][:][:]
print("adj_senshrbase_NH3_vf.shape", adj_senshrbase_NH3_vf.shape)
adj_senshrbase_NH3_vf = adj_senshrbase_NH3_vf[1:2,0:22,:,:]
print("adj_senshrbase_NH3_vf.shape", adj_senshrbase_NH3_vf.shape)
print("adj_senshrbase_NH3_vf.sum", np.nansum(adj_senshrbase_NH3_vf))

#diff_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2daytest_new_base/diff.mm.ncf'
#diff = Dataset(diff_file, 'r')

for variable in list_variables:
    #CHANGE3:
    unit = r'$\mathrm{^{ppm}/_{ppm}}$' #LGRID unit
    #unit = r'$\mathrm{^{ppm}/_{mol/sec}}$' #EM.LGRID unit
    
    #CHANGE4:
    #pdf_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/scatterPlot_LGRID_mm.NH3Model.vs.mm.active' + variable + '.pdf'
    #pdf_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/scatterPlot_EM.LGRID_mm.NH3Model.vs.mm.active' + variable + '.pdf'
    #pdf_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/scatterPlot_LGRID_mm.NH3Model.vs.cl.active' + variable + '.pdf'
    #pdf_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/scatterPlot_EM.LGRID_mm.NH3Model.vs.cl.active' + variable + '.pdf'
    #pdf_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/scatterPlot_LGRID_NH3Model.vs.active' + variable + '.l22.hr2.pdf'
    pdf_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/scatterPlot_LGRID_NH3.vs.NH3.vf.l22.hr2.pdf'
    with PdfPages(pdf_file) as pdf:
        nArray = np.reshape(adj_senshrbase_NH3,[-1,])
        fArray = np.reshape(adj_senshrbase_NH3_vf,[-1,])

        # Calculate Statistical Parameters
        slope, intercept, r_value, p_value, std_err = stats.linregress(nArray, fArray)
        plt.rcParams["font.size"] = 14

        #added layer color
        grid_layer=np.reshape(layers,[-1,])
        #added layer color end
        
        #c = diff[variable][:,0,:,:]
        cs = plt.scatter(nArray,fArray, c=grid_layer, cmap=cm.Spectral_r)
        #cs = plt.scatter(nArray,fArray, cmap=cm.Spectral_r)
        rangemin = min(np.min(nArray),np.min(fArray))
        rangemax = max(np.max(nArray),np.max(fArray))
        v = [rangemin, rangemax, rangemin, rangemax]
        plt.axis(v)

        plt.plot([rangemin, rangemax], [rangemin, rangemax])
        #plt.plot(fdarray, intercept + slope*fdarray, 'r', label='fitted line')
        ax = plt.gca()
        ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        ax.set_ylabel(r'NH3 Model (' + unit + ')')
        ax.set_xlabel(r'NH3 Model vf(' + unit + ')')
        ax.minorticks_on()
        ax.yaxis.grid(True, which='major', color='black', linestyle='--', linewidth='0.4')
        ax.yaxis.grid(True, which='minor', color='gray', linestyle=':', linewidth='0.3',)
        ax.xaxis.grid(True, which='major', color='black', linestyle='--', linewidth='0.4')
        ax.xaxis.grid(True, which='minor', color='gray', linestyle=':', linewidth='0.3')
        #ax.set_xlabel(r'$\mathrm{\mathsf{FD: \frac{\Delta[' + species + ']|_{1hr}}{' + str(pert) + '}}}$')

        ax.annotate('R$^2$ = {:0.2F}\nSlope = {:0.2F}\nIntercept = {:0.2E}\nBlue Line = 1:1'.format(r_value**2., slope, intercept), xy=(0.05, 0.7), fontsize=14, fontweight='bold', xycoords='axes fraction',                \
                        horizontalalignment='left', verticalalignment='bottom')

        cb = plt.colorbar()
        #cb.formatter.set_powerlimits((0, 0))
        cb.ax.yaxis.set_offset_position('left')
        cb.update_ticks()
        cb.set_label(r'Layers')
        plt.tight_layout()
        
        #CHANGE5:
        # add title
        plt.title( variable + ' in LGRID' )
        #plt.title( variable + ' in EM.LGRID' )
        pdf.savefig()
        plt.close()
        
        #CHANGE6 vmax:
        plt.hist2d (nArray, fArray, bins =(10,10), vmax = 200, cmap=plt.cm.BuPu)
        plt.hist2d (nArray, fArray, bins =(10,10), cmap=plt.cm.BuPu)
        plt.colorbar()
        pdf.savefig()
        plt.close()
        

