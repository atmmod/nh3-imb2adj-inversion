#!/home/cl3293/anaconda3/bin/python

#Script for scatter plot of ACONC comparison between NH3-active model and the full model, both have vertical performance fix applied.

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

#NH3 active model ACONC
NH3_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day.l22.hr2/ACONC.20070610' 
NH3 = Dataset(NH3_file,mode='r', open=True)

adj_aconchrbase_NH3_ANH4J = NH3.variables['ACLJ'][:][:][:][:]
adj_aconchrbase_NH3_ANH4I = NH3.variables['ACLI'][:][:][:][:]
adj_aconchrbase_NH3_ANH4J = adj_aconchrbase_NH3_ANH4J[2:3,0:22,:,:]
adj_aconchrbase_NH3_ANH4I = adj_aconchrbase_NH3_ANH4I[2:3,0:22,:,:]
adj_aconchrbase_NH3_ANH4_sum = adj_aconchrbase_NH3_ANH4J + adj_aconchrbase_NH3_ANH4I

ltime, llayer, lrow, lcol = adj_aconchrbase_NH3_ANH4_sum.shape
layers = np.zeros([ltime, llayer, lrow, lcol])
for ll in range(0,22):
	layers[:,ll,:,:] = ll

#full model ACONC
full_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_full/cmaq_adj/CMAQadjBnmkData/output_full_2day.l22.hr2/ACONC.20070610'
full = Dataset(full_file,mode='r', open=True)

adj_aconchrbase_full_ANH4J = full.variables['ACLJ'][:][:][:][:]
adj_aconchrbase_full_ANH4I = full.variables['ACLI'][:][:][:][:]
adj_aconchrbase_full_ANH4J = adj_aconchrbase_full_ANH4J[2:3,0:22,:,:]
adj_aconchrbase_full_ANH4I = adj_aconchrbase_full_ANH4I[2:3,0:22,:,:]
adj_aconchrbase_full_ANH4_sum = adj_aconchrbase_full_ANH4J + adj_aconchrbase_full_ANH4I

unit = r'$\mathrm{^{ppm}}$'

pdf_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/scatterPlot_ACONC_full.vs.NH3-active_for_ACL_sum.l22.hr2.0723.pdf'
with PdfPages(pdf_file) as pdf:
	nArray = np.reshape(adj_aconchrbase_NH3_ANH4_sum,[-1,])
	fArray = np.reshape(adj_aconchrbase_full_ANH4_sum,[-1,])

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
	ax.set_xlabel(r'NH3-active Model (' + unit + ')')
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
	plt.title( 'ACL_sum in ACONC' )
	pdf.savefig()
	plt.close()
	
	plt.hist2d (nArray, fArray, bins =(10,10), cmap=plt.cm.BuPu)
	plt.colorbar()
	pdf.savefig()
	plt.close()
	

