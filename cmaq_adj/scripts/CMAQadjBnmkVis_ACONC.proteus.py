#!/home/cl3293/anaconda3/bin/python
### Script for evaluating the ozone concentrations from CMAQ with monitor obs ##

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

# Goal: evaluate the CMAQ ozone fields against ozone observations
# - read the O3 observations into panda dataframe
# - organize by time, lat, lon, and conc
# - loop over time (consider using animate package)
# 	- plot the map of ozone concentrations from CMAQ
# 	- add scatter plot of monitor concentrations at same time


### Load ozone monitoring data
### Find these monitoring data at the following link
###    http://aqsdr1.epa.gov/aqsweb/aqstmp/airdata/hourly_44201_2007.zip
### CHANGE: specify path to file
#o3obs = pd.read_csv('/data/shannon/O3observations/hourly_44201_2007.csv',parse_dates=[[11,12]])

# sample description of the dataframe
#o3obs.head()
#o3obs.describe()

# Reshape to have all obs at a given time
#source_cols = ['State Code','Site Num']
#stc = o3obs['State Code']
#stn = o3obs['Site Num']
#newid = np.empty(len(stc),'S7')

# create new site ids that have the state, county, and site number
#    7 digit string - 'ssnnnnn'
#    left-filled with zeros for each string
#for i in range(len(stc)):
#	newid[i] = str(stc[i]).zfill(2) + str(stn[i]).zfill(5)

# assign the combined name of the site to a new column in the dataframe 
#o3obs['st_site_num'] = newid

# pivot the data to be oriented on dates at each of the different monitoring locations
#o3obssiteconc = o3obs.pivot_table(values='Sample Measurement',index='Date GMT_Time GMT',columns='st_site_num', aggfunc=np.mean)
#o3obssitelat = o3obs.pivot_table(values='Latitude',index='Date GMT_Time GMT',columns='st_site_num', aggfunc=np.mean)
#o3obssitelon = o3obs.pivot_table(values='Longitude',index='Date GMT_Time GMT',columns='st_site_num', aggfunc=np.mean)

### Plot O3 concentrations at sites only

# Select from date time index
#o3obssiteconc[:2].index



## Ingest CMAQ hourly ozone concentrations
# Specify number of days to be read
days = 11

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
    
    # For each day, open the ozone average concentration file
    # CHANGE specify location of checkpoint files
    #aconcbasename = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_full/cmaq_adj/CMAQadjBnmkData/output_full_2day.l22.hr2/ACONC.200706'+dStamp
    aconcbasename = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day.l22.hr2.bugfree/ACONC.200706'+dStamp
    #aconcbasename = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day_base/ACONC.200706'+dStamp
    #aconcbasename = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day_pert/ACONC.200706'+dStamp



    
    aconcbasefile = Dataset(aconcbasename, mode='r', open=True)
    
    # Read from output of model the ozone concentration
    
    #CHANGE SPECIES
    cohrbase = np.squeeze(aconcbasefile.variables['NH3'][:][:][:])
    
    # Combine the hourly ozone concentrations
    if dd == 9:
        cO3hrbase = cohrbase 
    else:
        cO3hrbase = np.concatenate((cO3hrbase,cohrbase),axis=0)
    
    concO3hrbase = cO3hrbase
    print(cO3hrbase.shape)
    ltime, llay, lrow, lcol = (cO3hrbase.shape)


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
#Made changes here // instead of / to avoid IndexError: IndexError: 
#only integers, slices (`:`), ellipsis (`...`), numpy.newaxis (`None`) and 
#integer or boolean arrays are valid indices
#2-1 or 2 makes little change to maps



### Plot both monitoring sites and CMAQ output for each hour
# Create the PDFPages object for writing
### CHANGE date: specify path
#with PdfPages('/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/ACONC.jun10.NH3_2day.full.pdf') as pdf:
with PdfPages('/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/ACONC.jun10.NH3_2day.NH3.bugfree.pdf') as pdf:
#with PdfPages('/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/ACONC.jun10.NH3_2day_base.pdf') as pdf:
#with PdfPages('/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/ACONC.jun10.NH3_2day_pert.pdf') as pdf:

    # Hour range is the timeframe in the ingested CMAQ values to be plotted and compared
    ## For example, only day 6 of the days ingested above (May 30, 2007)
    ## j is a separate index for the monitor dates and times
    j = 0 
    ###CHANGE range for that date
    for i in range(0,24):
        ###CHANGE date
        rng = pd.date_range('6/10/2007',periods=24,freq='H')
        
        # Put the monitoring data on top of the concentration from CMAQ
        # Establish basemap
        m = Basemap(projection='lcc', llcrnrlon=loncrn[0], llcrnrlat=latcrn[0],\
                    urcrnrlon=loncrn[1], urcrnrlat=latcrn[1], lon_0=lonmid,\
                    lat_0=latmid, resolution='l')
        
        # draw coastlines, state and country boundaries, edge of map.
        m.drawcoastlines()
        m.drawstates()
        m.drawcountries()
        
        # Try plotting hourly ozone from CMAQ
        ny = concO3hrbase.shape[2]; nx = concO3hrbase.shape[3]
        lons, lats = m.makegrid(nx, ny) # get lat/lons of ny by nx evenly space grid.
        x, y = m(lons, lats) # compute map proj coordinates.
        
        # draw filled contours.
        clevs = np.arange(np.min(concO3hrbase[0:24,:,:,:]),np.max(concO3hrbase[0:24,:,:,:])+(np.max(concO3hrbase[0:24,:,:,:])-np.min(concO3hrbase[0:24,:,:,:]))/100,(np.max(concO3hrbase[0:24,:,:,:])-np.min(concO3hrbase[0:24,:,:,:]))/100)
        print("max",np.max(concO3hrbase[0:24,:,:,:]))
        print("min",np.min(concO3hrbase[0:24,:,:,:]))
        # shift the hours by a fixed amount to the start of the CMAQ day of interest
        cs = m.contourf(x,y,concO3hrbase[i,0,:,:],clevs,cmap=cm.Spectral_r,vmin=np.min(concO3hrbase),vmax=np.max(concO3hrbase))
        
        # Make a circular marker and color by concentration
        #x = o3obssitelon[rng[j]:rng[j+1]].values
        #y = o3obssitelat[rng[j]:rng[j+1]].values
        #o3 = o3obssiteconc[rng[j]:rng[j+1]].values
        
        # Plot only the monitor location concentrations
        #mon = m.scatter(x,y, marker = 'o', c = o3, cmap=cm.Spectral_r, latlon=True,vmin=np.min(concO3hrbase),vmax=np.max(concO3hrbase))
        
        # add colorbar.
        cbar = m.colorbar(cs,location='right',pad="0.01%")
        cbar.set_label('(ppm)')
        plt.tight_layout()
       
        # add title 
        #CHANGE TITLE
        plt.title('Hourly NH3 for '+str(rng[j]))
        
        # iterate over dates
        j = j+1
        
        #plt.show()
        
        pdf.savefig()
        plt.close()
    










