#!/home/cl3293/anaconda3/bin/python

### Script for plotting and evaluating the adjoint sensitivities w.r.t emissions##

### CHANGE above: specify local python installation

import matplotlib as mpl
mpl.use('Agg')
from netCDF4 import Dataset
import pandas as pd
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from math import fsum, exp
from random import uniform
from matplotlib import cm
from mpl_toolkits.basemap import Basemap
import matplotlib.ticker

## Ingest the adjoint sensitivities w.r.t emissions
# Specify number of days to be read
days = 10

# iterate over this period of time
for dd in range(9, days):
    day = 1 + dd     
    # Ensure that the string for day will match the CMAQ file
    if (day < 10):
        # Add zero before 
        small = str('0')
        dStamp = small+str(day)
    else:
        dStamp = str(day)
    dStamp
    
    #CHANGE DIRECTORY:
    # For each day, open the adjoint sensitivities w.r.t emissions file
    EMLGRIDbasename_full = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_full/cmaq_adj/CMAQadjBnmkData/output_full_2day.l22.hr2/EM.LGRID.bwd_full.200706'+dStamp
    EMLGRIDbasename_NH3 = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day.l22.hr2/EM.LGRID.bwd_NH3.200706'+dStamp
    EMLGRIDbasefile_full = Dataset(EMLGRIDbasename_full, mode='r', open=True)
    EMLGRIDbasefile_NH3 = Dataset(EMLGRIDbasename_NH3, mode='r', open=True)
    
    #Read from output of model the adjoint sensitivities
    
    #Create adj_senshrbase for every species
    adj_senshrbase_NH3_full = EMLGRIDbasefile_full.variables['NH3'][:][:][:][:]
    adj_senshrbase_NH3_NH3 = EMLGRIDbasefile_NH3.variables['NH3'][:][:][:][:]

    # Combine the hourly sensitivities
    if dd == 9:
        ADJ_SENShrbase_NH3_full = adj_senshrbase_NH3_full
        ADJ_SENShrbase_NH3_NH3 = adj_senshrbase_NH3_NH3
    else:
        ADJ_SENShrbase_NH3_full  = np.concatenate((ADJ_SENShrbase_NH3_full ,adj_senshrbase_NH3_full ),axis=0)
        ADJ_SENShrbase_NH3_NH3  = np.concatenate((ADJ_SENShrbase_NH3_NH3 ,adj_senshrbase_NH3_NH3 ),axis=0)
    
    grdADJ_SENShrbase_NH3_full = np.squeeze(ADJ_SENShrbase_NH3_full)
    grdADJ_SENShrbase_NH3_NH3  = np.squeeze(ADJ_SENShrbase_NH3_NH3)

     
    ltime, lrow, lcol = (grdADJ_SENShrbase_NH3_full.shape)
    print(ltime)

# Get coordinates for map projection
### CHANGE: specify path
latlonfilename = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/other/latlon.bnmk'
latlonfile = Dataset(latlonfilename, mode='r', open=True)

gridLat =  np.squeeze(latlonfile.variables['LAT'][:][:][:][:])
gridLon =  np.squeeze(latlonfile.variables['LON'][:][:][:][:])

last1ind,last2ind = gridLon.shape

loncrn = [gridLon[0,0],gridLon[last1ind-1,last2ind-1]]
latcrn = [gridLat[0,0],gridLat[last1ind-1,last2ind-1]]
lonmid = gridLon[last1ind//2,last2ind//2]
latmid = gridLat[last1ind//2-1,last2ind//2-1]

#only take hour 1 sensitivities
adj_senshrbase_full = grdADJ_SENShrbase_NH3_full[1:2,:,:] 
adj_senshrbase_NH3 = grdADJ_SENShrbase_NH3_NH3[1:2,:,:] 

#Calc the diff
adj_senshrbase_diff = adj_senshrbase_full - adj_senshrbase_NH3
adj_senshrbase_diff  = np.squeeze(adj_senshrbase_diff)

### Plot
#Set font size
font_size = 14

#set ticks format: 2 digits after decimal point, scientific notations
class FormatScalarFormatter(matplotlib.ticker.ScalarFormatter):
    def __init__(self, fformat="%1.1f", offset=True, mathText=True):
        self.fformat = fformat
        matplotlib.ticker.ScalarFormatter.__init__(self,useOffset=offset,
                                                        useMathText=mathText)
    def _set_format(self, vmin, vmax):
        self.format = self.fformat
        if self._useMathText:
            self.format = '$%s$' % matplotlib.ticker._mathdefault(self.format)
fmt = FormatScalarFormatter("%.2f")

# Create the PDFPages object for writing
with PdfPages('/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/EM.LGRID.diff.full.vs.NH3_2day.l22.hr2.0723.pdf') as pdf:
    
    #CHANGE RANGE TO PLOT SPECIFIC SPECIES: NH3
	# Establish basemap
	m = Basemap(projection='lcc', llcrnrlon=loncrn[0], llcrnrlat=latcrn[0],\
				urcrnrlon=loncrn[1], urcrnrlat=latcrn[1], lon_0=lonmid,\
				lat_0=latmid, resolution='l')
	
	# draw coastlines, state and country boundaries, edge of map.
	m.drawcoastlines()
	m.drawstates()
	m.drawcountries()
	
	ny = adj_senshrbase_diff.shape[0]; nx = adj_senshrbase_diff.shape[1]
	lons, lats = m.makegrid(nx, ny) # get lat/lons of ny by nx evenly space grid.
	x, y = m(lons, lats) # compute map proj coordinates.
	
	# draw filled contours.
	upperbound = max(np.abs(np.nanmax(adj_senshrbase_diff[:,:])), np.abs(np.nanmin(adj_senshrbase_diff[:,:])))
	print("upperbound", upperbound)
	lowerbound = -upperbound
	clevs = np.arange(lowerbound,upperbound+(upperbound - lowerbound)/20,(upperbound - lowerbound)/20)                   
	cmap=cm.seismic

		   
   
	# shift the hours by a fixed amount to the start of the CMAQ day of interest
	cs = m.contourf(x,y,adj_senshrbase_diff[:,:],clevs,cmap=cmap,extend='both')        # add colorbar.
	cbar = m.colorbar(cs,format=fmt,location='right',pad="0.00%")
	#scientific notation
	cbar.formatter.set_powerlimits((0, 0))
	cbar.update_ticks()
	# change tick font size
	cbar.ax.tick_params(labelsize=font_size)
	# add label
	cbar.set_label('(ppm)/(mol/s)', fontsize=font_size)

	
	# add title
	plt.title('EM.LGRID NH3 full - NH3-active')
   
	plt.tight_layout()
	pdf.savefig()
	plt.close()

