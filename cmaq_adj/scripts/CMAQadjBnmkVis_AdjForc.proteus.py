#!/home/cl3293/anaconda3/bin/python
### Script for plotting and evaluating Adjoint Foring files ##

### CHANGE: specify local python installation
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

## Ingest Adjoint Forcing values
# Specify number of days to be read
days = 10

# iterate over this period of time
for dd in range(9, days):
    day = 1 + dd     
    # Ensure that the string for day will match the Adjoint forcing file
    if (day < 10):
        # Add zero before 
        small = str('0')
        dStamp = small+str(day)
    else:
        dStamp = str(day)
    dStamp
    
    # For each day, open the Adjoint forcing file
    ###CHANGE specify location of checkpoint files
    AdjForcbasename = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day/ADJ_FORCE.200706'+dStamp
    #AdjForcbasename = '/mnt/HA/groups/cappsGrp/mm4862/CMAQ/CMAQ_adj_NH3/CMAQadjBnmkData/output_fd_base_NH3/ADJ_FORCE.200706'+dStamp  
    #AdjForcbasename = '/mnt/HA/groups/cappsGrp/mm4862/CMAQ/cmaq_adj/CMAQadjBnmkData/output_base_NH3_testTracer/ADJ_FORCE.200706'+dStamp  

     
    AdjForcbasefile = Dataset(AdjForcbasename, mode='r', open=True)
    #print("AdjForcbasefile.shape", AdjForcbasefile.shape)
    # Read from output of model the ozone Adjoint forcing
    AdjForchrbase = np.squeeze(AdjForcbasefile.variables['NH3'][:][:][:])
    #AdjForchrbase = AdjForcbasefile.variables['NH3'][:][:][:][:] #25,1,25,25
    print("AdjForchrbase.shape", AdjForchrbase.shape) #25,25,25
    
    # Combine the hourly ozone Adjoint forcing values
    if dd == 9:
        AdjForc_hrbase = AdjForchrbase 
    else:
        AdjForc_hrbase = np.concatenate((AdjForc_hrbase,AdjForchrbase),axis=0)
    
    AdjForc_O3hrbase = AdjForc_hrbase
    ltime, lrow, lcol = (AdjForc_hrbase.shape)
    print('ltime',ltime)


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
latmid = gridLat[last1ind//2,last2ind//2]
#Made changes here // instead of / to avoid IndexError: IndexError: 
#only integers, slices (`:`), ellipsis (`...`), numpy.newaxis (`None`) and 
#integer or boolean arrays are valid indices
#2-1 or 2 makes little change to maps


### Plot Adjoint Forcing output for each hour
# Create the PDFPages object for writing
### CHANGE: specify path
with PdfPages('/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/AdjForc_NH3.jun10.NH3active.pdf') as pdf:
#with PdfPages('/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/AdjForc_NH3.jun10.NH3active.mm.pdf') as pdf:
#with PdfPages('/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/AdjForc_NH3.jun10.full.mm.pdf') as pdf:

    # Hour range is the timeframe in the ingested Adjoint Forcing values to be plotted and evaluated
    ## j is a separate index for the monitor dates and times
    j = 0 
    for i in range(0,ltime):
        rng = pd.date_range('6/10/2007',periods=25,freq='H')
        
        # Establish basemap
        m = Basemap(projection='lcc', llcrnrlon=loncrn[0], llcrnrlat=latcrn[0],\
                    urcrnrlon=loncrn[1], urcrnrlat=latcrn[1], lon_0=lonmid,\
                    lat_0=latmid, resolution='l')
        
        # draw coastlines, state and country boundaries, edge of map.
        m.drawcoastlines()
        m.drawstates()
        m.drawcountries()
        
        # Try plotting hourly ozone Adjoint forcing 
        ny = AdjForc_O3hrbase.shape[1]; nx = AdjForc_O3hrbase.shape[2]
        lons, lats = m.makegrid(nx, ny) # get lat/lons of ny by nx evenly space grid.
        x, y = m(lons, lats) # compute map proj coordinates.
        
        # draw filled contours.
        clevs = np.arange(np.min(AdjForc_O3hrbase),np.max(AdjForc_O3hrbase)+0.1,0.1)
        # shift the hours by a fixed amount to the start of the CMAQ day of interest
        cs = m.contourf(x,y,AdjForc_O3hrbase[i,:,:],clevs,cmap=cm.Spectral_r,vmin=np.min(AdjForc_O3hrbase),vmax=np.max(AdjForc_O3hrbase))
        
        # add colorbar.
        cbar = m.colorbar(cs,location='right',pad="5%")
        #cbar.set_label('(ppm)')
        
        # add title
        plt.title('Adjoint Forcing for '+str(rng[j]))
        
        # iterate over dates
        j = j+1
        
        #plt.show()
        
        pdf.savefig()
        plt.close()
    










