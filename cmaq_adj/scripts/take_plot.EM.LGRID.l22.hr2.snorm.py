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

list_variables = ['NH3']

#Open emission files for NH3 active:
emisname_NH3 = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/emis/emis_CMAQ-NH3_Tracer_20070610.ncf'
emisfile_NH3 = Dataset(emisname_NH3, mode='r', open=True)
emisnh3hr_NH3 = np.squeeze(emisfile_NH3.variables['NH3'][:][:][:])
print("emisnh3hr_NH3.shape", emisnh3hr_NH3.shape)

#Open emission files for full:
emisname_full = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_full/cmaq_adj/CMAQadjBnmkData/emis/emis_CMAQ-BENCHMARK_20070610.ncf'
emisfile_full = Dataset(emisname_full, mode='r', open=True)
emisnh3hr_full = np.squeeze(emisfile_full.variables['NH3'][:][:][:])
print("emisnh3hr_full.shape", emisnh3hr_full.shape)

#NH3 active model sensitivities
#CHANGE1:
NH3_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day.l22.hr2/EM.LGRID.bwd_NH3.20070610'
     
NH3 = Dataset(NH3_file,mode='r', open=True)

adj_senshrbase_NH3 = NH3.variables['NH3'][:][:][:][:]
print("adj_senshrbase_NH3.shape", adj_senshrbase_NH3.shape)

#CHANGE2:
adj_senshrbase_NH3 = adj_senshrbase_NH3[1,0,:,:] * emisnh3hr_NH3[1,:,:] #EM.LGRID
print("adj_senshrbase_NH3.shape", adj_senshrbase_NH3.shape)
print("adj_senshrbase_NH3.sum", np.nansum(adj_senshrbase_NH3))

#CHANGE3:
#full model sensitivities
full_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_full/cmaq_adj/CMAQadjBnmkData/output_full_2day.l22.hr2/EM.LGRID.bwd_full.20070610'
full = Dataset(full_file,mode='r', open=True)

adj_senshrbase_full = full.variables['NH3'][:][:][:][:]
print("adj_senshrbase_full.shape", adj_senshrbase_full.shape)

#CHANGE4:
adj_senshrbase_full = adj_senshrbase_full[1,0,:,:] * emisnh3hr_full[1,:,:] #EM.LGRID
print("adj_senshrbase_full.shape", adj_senshrbase_full.shape)
print("adj_senshrbase_full.sum", np.nansum(adj_senshrbase_full))

for variable in list_variables:

    unit = 'ppm' #unit
    
    #CHANGE5:
    pdf_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/scatterPlot_EM.LGRID_full.vs.NH3-active_for_' + variable + '.l22.hr2.snorm.0723.pdf'
    with PdfPages(pdf_file) as pdf:
        nArray = np.reshape(adj_senshrbase_NH3,[-1,])
        fArray = np.reshape(adj_senshrbase_full,[-1,])

        # Calculate Statistical Parameters
        slope, intercept, r_value, p_value, std_err = stats.linregress(nArray, fArray)
        plt.rcParams["font.size"] = 14
        cs = plt.scatter(nArray,fArray, cmap=cm.Spectral_r)
        rangemin = min(np.min(nArray),np.min(fArray))
        rangemax = max(np.max(nArray),np.max(fArray))
        v = [rangemin, rangemax, rangemin, rangemax]
        plt.axis(v)

        plt.plot([rangemin, rangemax], [rangemin, rangemax])
        ax = plt.gca()
        ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        ax.set_ylabel(r'Full Model (' + unit + ')')
        ax.set_xlabel(r'${\mathsf{NH_3}}$-active Model (' + unit + ')')
        ax.minorticks_on()
        ax.yaxis.grid(True, which='major', color='black', linestyle='--', linewidth='0.4')
        ax.yaxis.grid(True, which='minor', color='gray', linestyle=':', linewidth='0.3',)
        ax.xaxis.grid(True, which='major', color='black', linestyle='--', linewidth='0.4')
        ax.xaxis.grid(True, which='minor', color='gray', linestyle=':', linewidth='0.3')

        ax.annotate('R$^2$ = {:0.2F}\nSlope = {:0.2F}\nIntercept = {:0.2E}\nBlue Line = 1:1'.format(r_value**2., slope, intercept), xy=(0.05, 0.7), fontsize=14, fontweight='bold', xycoords='axes fraction',                \
                        horizontalalignment='left', verticalalignment='bottom')
        
        #CHANGE6:
        # add title
        plt.title( r'$\mathrm{\mathsf{\frac{\delta[NH_3]|_{hr2}}{\delta Emis_{NH_3}|_{hr1}}}*Emis_{NH_3}|_{hr1}}$' ) #EM.LGRID
        
        plt.tight_layout()
        pdf.savefig()
        plt.close()
        
        plt.hist2d (nArray, fArray, bins =(10,10), vmax = 200, cmap=plt.cm.BuPu)

        plt.colorbar()
        pdf.savefig()
        plt.close()
        

