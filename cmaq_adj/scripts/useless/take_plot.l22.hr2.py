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
#CHANGE1.0:
#NH3_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day.l22.hr2.bugfree/LGRID.bwd_NH3.20070610'
#NH3_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day.l22.hr2.bugfree/EM.LGRID.bwd_NH3.20070610'
NH3_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day.l22.hr2.bugfree.vf/LGRID.bwd_NH3.20070610'
#NH3_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day.l22.hr2.bugfree.vf/EM.LGRID.bwd_NH3.20070610'
     
NH3 = Dataset(NH3_file,mode='r', open=True)

adj_senshrbase_NH3 = NH3.variables['NH3'][:][:][:][:]
print("adj_senshrbase_NH3.shape", adj_senshrbase_NH3.shape)
#CHANGE1.1:
adj_senshrbase_NH3 = adj_senshrbase_NH3[1:2,0:22,:,:] #LGRID
#adj_senshrbase_NH3 = adj_senshrbase_NH3[1:2,:,:] #EM.LGRID
print("adj_senshrbase_NH3.shape", adj_senshrbase_NH3.shape)
print("adj_senshrbase_NH3.sum", np.nansum(adj_senshrbase_NH3))

#CHANGE1.2:
#LGRID only, comment out if EM.LGRID, starts
ltime, llayer, lrow, lcol = adj_senshrbase_NH3.shape
layers = np.zeros([ltime, llayer, lrow, lcol])
for ll in range(0,22):
    layers[:,ll,:,:] = ll
#LGRID only, comment out if EM.LGRID, ends

#CHANGE2.0:
#full model sensitivities
#full_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_full/cmaq_adj/CMAQadjBnmkData/output_full_2day.l22.hr2/LGRID.bwd_full.20070610'
#full_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_full/cmaq_adj/CMAQadjBnmkData/output_full_2day.l22.hr2/EM.LGRID.bwd_full.20070610'
full_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_full/cmaq_adj/CMAQadjBnmkData/output_full_2day.l22.hr2.vf/LGRID.bwd_full_vf.20070610'
#full_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_full/cmaq_adj/CMAQadjBnmkData/output_full_2day.l22.hr2.vf/EM.LGRID.bwd_full_vf.20070610'
full = Dataset(full_file,mode='r', open=True)

adj_senshrbase_full = full.variables['NH3'][:][:][:][:]
print("adj_senshrbase_full.shape", adj_senshrbase_full.shape)
#CHANGE2.1:
adj_senshrbase_full = adj_senshrbase_full[1:2,0:22,:,:] #LGRID
#adj_senshrbase_full = adj_senshrbase_full[1:2,:,:] #EM.LGRID
print("adj_senshrbase_full.shape", adj_senshrbase_full.shape)
print("adj_senshrbase_full.sum", np.nansum(adj_senshrbase_full))

#diff_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2daytest_new_base/diff.mm.ncf'
#diff = Dataset(diff_file, 'r')

for variable in list_variables:
    #CHANGE3:
    unit = r'$\mathrm{^{ppm}/_{ppm}}$' #LGRID unit
    #unit = r'$\mathrm{^{ppm}/_{mol/sec}}$' #EM.LGRID unit
    
    #CHANGE4.0:
    #pdf_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/scatterPlot_LGRID_fullModel.vs.active' + variable + '.l22.hr2.bugfree.pdf'
    #pdf_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/scatterPlot_EM.LGRID_fullModel.vs.active' + variable + '.l22.hr2.bugfree.pdf'
    pdf_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/scatterPlot_LGRID_fullModel.vs.active' + variable + '.l22.hr2.bugfree.vf.new.pdf'
    #pdf_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/scatterPlot_EM.LGRID_fullModel.vs.active' + variable + '.l22.hr2.bugfree.vf.pdf'
    with PdfPages(pdf_file) as pdf:
        nArray = np.reshape(adj_senshrbase_NH3,[-1,])
        fArray = np.reshape(adj_senshrbase_full,[-1,])

        # Calculate Statistical Parameters
        slope, intercept, r_value, p_value, std_err = stats.linregress(nArray, fArray)
        plt.rcParams["font.size"] = 14
        
        #CHANGE4.1:
        #added layer color, LGRID only, comment out if EM.LGRID, starts
        grid_layer=np.reshape(layers,[-1,])
        #added layer color, LGRID only, comment out if EM.LGRID, ends
        
        #c = diff[variable][:,0,:,:]
        #CHANGE4.2:
        cs = plt.scatter(nArray,fArray, c=grid_layer, cmap=cm.Spectral_r) #LGRID
        #cs = plt.scatter(nArray,fArray, cmap=cm.Spectral_r) #EM.LGRID
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

        #CHANGE4.3 comment out if EM.LGRID
        cb = plt.colorbar()
        cb.formatter.set_powerlimits((0, 0))
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
        #plt.hist2d (nArray, fArray, bins =(10,10), vmax = 200, cmap=plt.cm.BuPu)
        plt.hist2d (nArray, fArray, bins =(10,10), cmap=plt.cm.BuPu)
        plt.colorbar()
        pdf.savefig()
        plt.close()
        

