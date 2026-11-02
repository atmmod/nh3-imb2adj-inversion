#!/home/cl3293/anaconda3/bin/python

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
#NH3_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day.l1.hr0-9/LGRID.bwd_NH3.20070610'
NH3_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day.l1.hr0-9/EM.LGRID.bwd_NH3_new2.20070610'
     
NH3 = Dataset(NH3_file,mode='r', open=True)

adj_senshrbase_NH3 = NH3.variables['NH3'][:][:][:][:]
#adj_senshrbase_NH3 = adj_senshrbase_NH3[0:10,1:22,:,:] #LGRID
adj_senshrbase_NH3 = adj_senshrbase_NH3[0:10,0:1,:,:] #EM.LGRID
print("adj_senshrbase_NH3.shape", adj_senshrbase_NH3.shape)
print("adj_senshrbase_NH3.sum", np.nansum(adj_senshrbase_NH3))

#CHANGE2:
#full model sensitivities
#full_file = '/mnt/HA/groups/cappsGrp/mm4862/CMAQ/cmaq_adj/CMAQadjBnmkData/output_base_NH3_testTracer/LGRID.bwd_bnmk.20070610'
#full_file = '/mnt/HA/groups/cappsGrp/mm4862/CMAQ/cmaq_adj/CMAQadjBnmkData/output_base_NH3_testTracer/EM.LGRID.bwd_bnmk.20070610'
#full_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_full/cmaq_adj/CMAQadjBnmkData/output_full_2day/LGRID.bwd_full.20070610'
full_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_full/cmaq_adj/CMAQadjBnmkData/output_full_2day/EM.LGRID.bwd_full.20070610'
full = Dataset(full_file,mode='r', open=True)

adj_senshrbase_full = full.variables['NH3'][:][:][:][:]
#adj_senshrbase_full = adj_senshrbase_full[0:10,1:22,:,:] #LGRID
adj_senshrbase_full = adj_senshrbase_full[0:10,0:1,:,:] #EM.LGRID
print("adj_senshrbase_full.shape", adj_senshrbase_full.shape)
print("adj_senshrbase_full.sum", np.nansum(adj_senshrbase_full))

#diff_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2daytest_new_base/diff.mm.ncf'
#diff = Dataset(diff_file, 'r')

for variable in list_variables:
    #CHANGE3:
    #unit = r'$\mathrm{^{ppm}/_{ppm}}$' #LGRID unit
    unit = r'$\mathrm{^{ppm}/_{mol/sec}}$' #EM.LGRID unit
    
    #CHANGE4:
    #pdf_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/scatterPlot_LGRID_mm.fullModel.vs.mm.active' + variable + '.pdf'
    #pdf_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/scatterPlot_EM.LGRID_mm.fullModel.vs.mm.active' + variable + '.pdf'
    #pdf_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/scatterPlot_LGRID_mm.fullModel.vs.cl.active' + variable + '.pdf'
    #pdf_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/scatterPlot_EM.LGRID_mm.fullModel.vs.cl.active' + variable + '.pdf'
    #pdf_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/scatterPlot_LGRID_cl.fullModel.vs.cl.active' + variable + '_2-22layer.new.pdf'
    pdf_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/scatterPlot_EM.LGRID_cl.fullModel.vs.cl.active' + variable + '.new2.pdf'
    with PdfPages(pdf_file) as pdf:
        nArray = np.reshape(adj_senshrbase_NH3,[-1,])
        fArray = np.reshape(adj_senshrbase_full,[-1,])

        # Calculate Statistical Parameters
        slope, intercept, r_value, p_value, std_err = stats.linregress(nArray, fArray)
        plt.rcParams["font.size"] = 14
        #c = diff[variable][:,0,:,:]
        #cs = plt.scatter(nArray,fArray, c=c.flatten(), cmap=cm.Spectral_r)
        cs = plt.scatter(nArray,fArray, cmap=cm.Spectral_r)
        rangemin = min(np.min(nArray),np.min(fArray))
        rangemax = max(np.max(nArray),np.max(fArray))
        v = [rangemin, rangemax, rangemin, rangemax]
        plt.axis(v)

        plt.plot([rangemin, rangemax], [rangemin, rangemax])
        #plt.plot(fdarray, intercept + slope*fdarray, 'r', label='fitted line')
        ax = plt.gca()
        ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        ax.set_ylabel(r'Full Model (' + unit + ')')
        ax.set_xlabel(r'NH3-active Model (' + unit + ')')
        ax.minorticks_on()
        ax.yaxis.grid(True, which='major', color='black', linestyle='--', linewidth='0.4')
        ax.yaxis.grid(True, which='minor', color='gray', linestyle=':', linewidth='0.3',)
        ax.xaxis.grid(True, which='major', color='black', linestyle='--', linewidth='0.4')
        ax.xaxis.grid(True, which='minor', color='gray', linestyle=':', linewidth='0.3')
        #ax.set_xlabel(r'$\mathrm{\mathsf{FD: \frac{\Delta[' + species + ']|_{1hr}}{' + str(pert) + '}}}$')

        ax.annotate('R$^2$ = {:0.2F}\nSlope = {:0.2F}\nIntercept = {:0.2E}\nBlue Line = 1:1'.format(r_value**2., slope, intercept), xy=(0.05, 0.7), fontsize=14, fontweight='bold', xycoords='axes fraction',                \
                        horizontalalignment='left', verticalalignment='bottom')

        #cb = plt.colorbar()
        #cb.formatter.set_powerlimits((0, 0))
        #cb.ax.yaxis.set_offset_position('left')
        #cb.update_ticks()
        #cb.set_label(r'Difference (' + unit + ')')
        plt.tight_layout()
        
        #CHANGE5:
        # add title
        #plt.title( variable + ' in LGRID' )
        plt.title( variable + ' in EM.LGRID' )
        pdf.savefig()
        plt.close()
        
        #CHANGE6 vmax:
        plt.hist2d (nArray, fArray, bins =(10,10), vmax = 5000, cmap=plt.cm.BuPu)
        #plt.hist2d (nArray, fArray, bins =(10,10), cmap=plt.cm.BuPu)
        plt.colorbar()
        pdf.savefig()
        plt.close()
        

