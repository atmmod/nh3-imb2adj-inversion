#!/home/cl3293/anaconda3/bin/python

#Script for scatter plot of LGRID comparison between NH3-active model and the full model, both have vertical performance fix applied.

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

list_variables = ['NH3', 'ANH4I', 'ANH4J']

#loop over all the selected species
for variable in list_variables:

    #Open conc files for NH3 active:
    concname_NH3 = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day.l22.hr2/CONC.20070610'
    concfile_NH3 = Dataset(concname_NH3, mode='r', open=True)
    concnh3hr_NH3 = np.squeeze(concfile_NH3.variables[variable][:][:][:])
    print("concnh3hr_NH3.shape", concnh3hr_NH3.shape)

    #Open conc files for full:
    concname_full = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_full/cmaq_adj/CMAQadjBnmkData/output_full_2day.l22.hr2/CONC.20070610'
    concfile_full = Dataset(concname_full, mode='r', open=True)
    concnh3hr_full = np.squeeze(concfile_full.variables[variable][:][:][:])
    print("concnh3hr_full.shape", concnh3hr_full.shape)

    #NH3 active model sensitivities
    NH3_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day.l22.hr2/LGRID.bwd_NH3.20070610'
    NH3 = Dataset(NH3_file,mode='r', open=True)

    adj_senshrbase_NH3 = NH3.variables[variable][:][:][:][:]
    print("adj_senshrbase_NH3.shape", adj_senshrbase_NH3.shape)

    adj_senshrbase_NH3 = adj_senshrbase_NH3[1:2,0:22,:,:] * concnh3hr_NH3[1:2,0:22,:,:]
    print("adj_senshrbase_NH3.shape", adj_senshrbase_NH3.shape)
    print("adj_senshrbase_NH3.sum", np.nansum(adj_senshrbase_NH3))

    ltime, llayer, lrow, lcol = adj_senshrbase_NH3.shape
    layers = np.zeros([ltime, llayer, lrow, lcol])
    for ll in range(0,22):
        layers[:,ll,:,:] = ll

    #full model sensitivities
    full_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_full/cmaq_adj/CMAQadjBnmkData/output_full_2day.l22.hr2/LGRID.bwd_full.20070610'
    full = Dataset(full_file,mode='r', open=True)

    adj_senshrbase_full = full.variables[variable][:][:][:][:]
    print("adj_senshrbase_full.shape", adj_senshrbase_full.shape)

    adj_senshrbase_full = adj_senshrbase_full[1:2,0:22,:,:] * concnh3hr_full[1:2,0:22,:,:]
    print("adj_senshrbase_full.shape", adj_senshrbase_full.shape)
    print("adj_senshrbase_full.sum", np.nansum(adj_senshrbase_full))

    unit = 'ppm' #unit

    pdf_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/scatterPlot_LGRID_full.vs.NH3-active_for_' + variable + '.l22.hr2.snorm.0723.pdf'
    with PdfPages(pdf_file) as pdf:
        nArray = np.reshape(adj_senshrbase_NH3,[-1,])
        fArray = np.reshape(adj_senshrbase_full,[-1,])

        # Calculate Statistical Parameters
        slope, intercept, r_value, p_value, std_err = stats.linregress(nArray, fArray)
        plt.rcParams["font.size"] = 14
        
        grid_layer=np.reshape(layers,[-1,])
        
        cs = plt.scatter(nArray,fArray, c=grid_layer, cmap=cm.Spectral_r)
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

        cb = plt.colorbar()
        #cb.formatter.set_powerlimits((0, 0))
        cb.ax.yaxis.set_offset_position('left')
        cb.update_ticks()
        cb.set_label(r'Layers')
        
        plt.tight_layout()
        
        # add title
        plt.title( r'$\mathrm{\mathsf{\frac{\delta[NH_3]|_{hr2}}{\delta['+ variable + ']|_{hr1}}}*['+ variable +']|_{hr1}}$')
        plt.tight_layout()
        pdf.savefig()
        plt.close()
    
        plt.hist2d (nArray, fArray, bins =(10,10), cmap=plt.cm.BuPu)
        plt.colorbar()
        pdf.savefig()
        plt.close()
        

