#!/home/cl3293/anaconda3/bin/python

### Script for plotting and evaluating the adjoint sensitivities w.r.t concentrations##

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

## Ingest the adjoint sensitivities w.r.t concentrations
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
    # For each day, open the adjoint sensitivities w.r.t concentrations file
    LGRIDbasename = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adjoint8/cmaq_adj/CMAQadjBnmkData/output_bnmk_Hadvdiff_off/LGRID.bwd_bnmk_Hadvdiff_off.200706'+dStamp
    LGRIDbasefile = Dataset(LGRIDbasename, mode='r', open=True)
    
    #Read from output of model the adjoint sensitivities
    #for each day, LGRID file gives information in a 4-D data "cube", 25*34*25*25, (ltime, llayer, lrow, lcol) 
    #We only want the ground-level information, that is layer 0
    #So select from the original data, the information in layer 0.
    
    LGRID_ETH_OG = LGRIDbasefile.variables['ETH'][:][:][:][:]
    LGRID_ETH_0 = LGRID_ETH_OG[:,0,:,:]
    
    LGRID_NO_OG = LGRIDbasefile.variables['NO'][:][:][:][:]
    LGRID_NO_0 = LGRID_NO_OG[:,0,:,:]
    
    LGRID_NO2_OG = LGRIDbasefile.variables['NO2'][:][:][:][:]
    LGRID_NO2_0 = LGRID_NO2_OG[:,0,:,:]
    
    #Calculate LGRID_NOx_0
    #LGRID_NOx_0 = LGRID_NO_0 * frac1 +  LGRID_NO2_0 * frac2
    #The fraction should be calculated by concentrations, ACONC instead of emissions
    aconcname = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adjoint8/cmaq_adj/CMAQadjBnmkData/output_bnmk_Hadvdiff_off/ACONC.200706'+dStamp
    aconcfile = Dataset(aconcname, mode='r', open=True)
    aconcnohr = np.squeeze(aconcfile.variables['NO'][:][:][:])
    aconcno2hr = np.squeeze(aconcfile.variables['NO2'][:][:][:])
    aconcnoxhr = aconcnohr + aconcno2hr 
    
    #Since ACONC has only 24 in 0 axis, add 1 25*25 zero array at the end
    zerolayer  = np.zeros([1, 25, 25])
    aconcnohr = np.concatenate((aconcnohr, zerolayer), axis=0)
    aconcno2hr = np.concatenate((aconcno2hr, zerolayer), axis=0)
    aconcnoxhr = np.concatenate((aconcnoxhr, zerolayer), axis=0)
    
    #If aconcnoxhr value equals to 0, make it NaN
    aconcnoxhr[aconcnoxhr==0] = np.nan
    
    LGRID_NOx_0 =  np.multiply(np.multiply(LGRID_NO2_0, aconcno2hr) +  np.multiply(LGRID_NO_0, aconcnohr), np.reciprocal(aconcnoxhr))

    adj_senshrbase_ETH = np.squeeze( LGRID_ETH_0[:][:][:])
    adj_senshrbase_NO = np.squeeze(LGRID_NO_0[:][:][:])
    adj_senshrbase_NO2 = np.squeeze(LGRID_NO2_0[:][:][:])
    adj_senshrbase_NOx = np.squeeze(LGRID_NOx_0[:][:][:])
    
    # Combine the hourly sensitivities
    if dd == 9:
        ADJ_SENShrbase_ETH = adj_senshrbase_ETH
        ADJ_SENShrbase_NO = adj_senshrbase_NO 
        ADJ_SENShrbase_NO2 = adj_senshrbase_NO2 
        ADJ_SENShrbase_NOx = adj_senshrbase_NOx  
    else:
        ADJ_SENShrbase_ETH  = np.concatenate((ADJ_SENShrbase_ETH ,adj_senshrbase_ETH ),axis=0)
        ADJ_SENShrbase_NO  = np.concatenate((ADJ_SENShrbase_NO ,adj_senshrbase_NO ),axis=0)
        ADJ_SENShrbase_NO2  = np.concatenate((ADJ_SENShrbase_NO2 ,adj_senshrbase_NO2 ),axis=0)
        ADJ_SENShrbase_NOx  = np.concatenate((ADJ_SENShrbase_NOx ,adj_senshrbase_NOx ),axis=0)
    
    grdADJ_SENShrbase_ETH  = ADJ_SENShrbase_ETH
    grdADJ_SENShrbase_NO  = ADJ_SENShrbase_NO
    grdADJ_SENShrbase_NO2  = ADJ_SENShrbase_NO2
    grdADJ_SENShrbase_NOx  = ADJ_SENShrbase_NOx
     
    ltime, lrow, lcol = (ADJ_SENShrbase_ETH .shape)

# Get coordinates for map projection
### CHANGE: specify path
latlonfilename = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adjoint8/cmaq_adj/CMAQadjBnmkData/other/latlon.bnmk'
latlonfile = Dataset(latlonfilename, mode='r', open=True)

gridLat =  np.squeeze(latlonfile.variables['LAT'][:][:][:][:])
gridLon =  np.squeeze(latlonfile.variables['LON'][:][:][:][:])

last1ind,last2ind = gridLon.shape

loncrn = [gridLon[0,0],gridLon[last1ind-1,last2ind-1]]
latcrn = [gridLat[0,0],gridLat[last1ind-1,last2ind-1]]
lonmid = gridLon[last1ind//2,last2ind//2]
latmid = gridLat[last1ind//2-1,last2ind//2-1]

#Calculate avg of 1 days, over 25*25 grid cells
sum3days_ave_sens_ETH = np.nansum(grdADJ_SENShrbase_ETH, axis = 0)/(1)
sum3days_ave_sens_NO = np.nansum(grdADJ_SENShrbase_NO, axis = 0)/(1)
sum3days_ave_sens_NO2 = np.nansum(grdADJ_SENShrbase_NO2, axis = 0)/(1)
sum3days_ave_sens_NOx = np.nansum(grdADJ_SENShrbase_NOx, axis = 0)/(1)

#Add axis -lday to the summed arrays
ave_sum_sens_ETH = sum3days_ave_sens_ETH[np.newaxis, :, :]
ave_sum_sens_NO = sum3days_ave_sens_NO[np.newaxis, :, :]
ave_sum_sens_NO2 = sum3days_ave_sens_NO2[np.newaxis, :, :]
ave_sum_sens_NOx = sum3days_ave_sens_NOx[np.newaxis, :, :]

#combine the 4 arrays
comb_days = np.concatenate((ave_sum_sens_ETH,ave_sum_sens_NO,ave_sum_sens_NO2,ave_sum_sens_NOx), axis=0)

### Plot
# Create the PDFPages object for writing
with PdfPages('/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adjoint8/cmaq_adj/CMAQadjBnmkData/output_bnmk_Hadvdiff_off/2007bnmkeval_LGRID.1day_avg.CDDC.pdf') as pdf: 
    
    #CHANGE RANGE TO PLOT SPECIFIC SPECIES: ETH
    for i in range(0,1):

        # Establish basemap
        m = Basemap(projection='lcc', llcrnrlon=loncrn[0], llcrnrlat=latcrn[0],\
                    urcrnrlon=loncrn[1], urcrnrlat=latcrn[1], lon_0=lonmid,\
                    lat_0=latmid, resolution='l')
        
        # draw coastlines, state and country boundaries, edge of map.
        m.drawcoastlines()
        m.drawstates()
        m.drawcountries()
        
        ny = comb_days.shape[1]; nx = comb_days.shape[2]
        lons, lats = m.makegrid(nx, ny) # get lat/lons of ny by nx evenly space grid.
        x, y = m(lons, lats) # compute map proj coordinates.
        
        # draw filled contours.
        upperbound = max(abs(np.min(comb_days[i,:,:])),abs(np.max(comb_days[i,:,:])))
        lowerbound = -upperbound
        clevs = np.arange(lowerbound,upperbound+(upperbound - lowerbound)/20,(upperbound - lowerbound)/20)
        #clevs = np.arange(np.min(comb_days),np.max(comb_days)+(np.max(comb_days)-np.min(comb_days))/10,(np.max(comb_days)-np.min(comb_days))/10)
        #clevs = np.arange(np.min(comb_days[i,:,:]),np.max(comb_days[i,:,:])+(np.max(comb_days[i,:,:])-np.min(comb_days[i,:,:]))/10,(np.max(comb_days[i,:,:])-np.min(comb_days[i,:,:]))/10)
        
        
        # shift the hours by a fixed amount to the start of the CMAQ day of interest
        #cs = m.contourf(x,y,comb_days[i,:,:],clevs,cmap=cm.Spectral_r,vmin=np.min(comb_days[i,:,:]),vmax=np.max(comb_days[i,:,:]))
        cs = m.contourf(x,y,comb_days[i,:,:],clevs,cmap=cm.Spectral_r)
        # add colorbar.
        cbar = m.colorbar(cs,location='right',pad="0.00%")
        # add label
        cbar.set_label(r'$\frac{ppb\:\mathrm{O_3}}{ppb\:Ethylene}$')
        
        # add title
        plt.title('Avg. Adj-sens of MDA1 [$\mathrm{O_3}$] wrt [ETH] for Jun 10')
       
        plt.tight_layout()
        pdf.savefig()
        plt.close()

     #CHANGE RANGE TO PLOT SPECIFIC SPECIES: NO
    for i in range(1,2):

        # Establish basemap
        m = Basemap(projection='lcc', llcrnrlon=loncrn[0], llcrnrlat=latcrn[0],\
                    urcrnrlon=loncrn[1], urcrnrlat=latcrn[1], lon_0=lonmid,\
                    lat_0=latmid, resolution='l')
        
        # draw coastlines, state and country boundaries, edge of map.
        m.drawcoastlines()
        m.drawstates()
        m.drawcountries()
        
        ny = comb_days.shape[1]; nx = comb_days.shape[2]
        lons, lats = m.makegrid(nx, ny) # get lat/lons of ny by nx evenly space grid.
        x, y = m(lons, lats) # compute map proj coordinates.
        
        # draw filled contours.
        upperbound = max(abs(np.min(comb_days[i,:,:])),abs(np.max(comb_days[i,:,:])))
        lowerbound = -upperbound
        clevs = np.arange(lowerbound,upperbound+(upperbound - lowerbound)/20,(upperbound - lowerbound)/20)        
        #clevs = np.arange(np.min(comb_days),np.max(comb_days)+(np.max(comb_days)-np.min(comb_days))/10,(np.max(comb_days)-np.min(comb_days))/10)
        #clevs = np.arange(np.min(comb_days[i,:,:]),np.max(comb_days[i,:,:])+(np.max(comb_days[i,:,:])-np.min(comb_days[i,:,:]))/10,(np.max(comb_days[i,:,:])-np.min(comb_days[i,:,:]))/10)
        
        # shift the hours by a fixed amount to the start of the CMAQ day of interest
        cs = m.contourf(x,y,comb_days[i,:,:],clevs,cmap=cm.Spectral_r)
        # add colorbar.
        cbar = m.colorbar(cs,location='right',pad="0.00%")
        # add label
        #cbar.set_label('CF/ppbV')
        cbar.set_label(r'$\frac{ppb\:\mathrm{O_3}}{ppb\:NO}$')
        
        # add title
        plt.title('Avg. Adj-sens of MDA1 [$\mathrm{O_3}$] wrt [NO] for Jun 10')
       
        plt.tight_layout()
        pdf.savefig()
        plt.close()  
          
     #CHANGE RANGE TO PLOT SPECIFIC SPECIES: NO2
    for i in range(2,3):

        # Establish basemap
        m = Basemap(projection='lcc', llcrnrlon=loncrn[0], llcrnrlat=latcrn[0],\
                    urcrnrlon=loncrn[1], urcrnrlat=latcrn[1], lon_0=lonmid,\
                    lat_0=latmid, resolution='l')
        
        # draw coastlines, state and country boundaries, edge of map.
        m.drawcoastlines()
        m.drawstates()
        m.drawcountries()
        
        ny = comb_days.shape[1]; nx = comb_days.shape[2]
        lons, lats = m.makegrid(nx, ny) # get lat/lons of ny by nx evenly space grid.
        x, y = m(lons, lats) # compute map proj coordinates.
        
        # draw filled contours.
        upperbound = max(abs(np.min(comb_days[i,:,:])),abs(np.max(comb_days[i,:,:])))
        lowerbound = -upperbound
        clevs = np.arange(lowerbound,upperbound+(upperbound - lowerbound)/20,(upperbound - lowerbound)/20)        
        #clevs = np.arange(np.min(comb_days),np.max(comb_days)+(np.max(comb_days)-np.min(comb_days))/10,(np.max(comb_days)-np.min(comb_days))/10)
        #clevs = np.arange(np.min(comb_days[i,:,:]),np.max(comb_days[i,:,:])+(np.max(comb_days[i,:,:])-np.min(comb_days[i,:,:]))/10,(np.max(comb_days[i,:,:])-np.min(comb_days[i,:,:]))/10)
        
        # shift the hours by a fixed amount to the start of the CMAQ day of interest
        cs = m.contourf(x,y,comb_days[i,:,:],clevs,cmap=cm.Spectral_r)
        # add colorbar.
        cbar = m.colorbar(cs,location='right',pad="0.00%")
        # add label
        #cbar.set_label('CF/ppbV')
        cbar.set_label(r'$\frac{ppb\:\mathrm{O_3}}{ppb\:\mathrm{NO_2}}$')
        
        # add title
        plt.title('Avg. Adj-sens of MDA1 [$\mathrm{O_3}$] wrt [$\mathrm{NO_2}$] for Jun 10')
        
        plt.tight_layout()
        pdf.savefig() 
        plt.close()  
         
     #CHANGE RANGE TO PLOT SPECIFIC SPECIES: NOx
    for i in range(3,4):

        # Establish basemap
        m = Basemap(projection='lcc', llcrnrlon=loncrn[0], llcrnrlat=latcrn[0],\
                    urcrnrlon=loncrn[1], urcrnrlat=latcrn[1], lon_0=lonmid,\
                    lat_0=latmid, resolution='l')
        
        # draw coastlines, state and country boundaries, edge of map.
        m.drawcoastlines()
        m.drawstates()
        m.drawcountries()
        
        ny = comb_days.shape[1]; nx = comb_days.shape[2]
        lons, lats = m.makegrid(nx, ny) # get lat/lons of ny by nx evenly space grid.
        x, y = m(lons, lats) # compute map proj coordinates.
        
        # draw filled contours.
        upperbound = max(abs(np.min(comb_days[i,:,:])),abs(np.max(comb_days[i,:,:])))
        lowerbound = -upperbound
        clevs = np.arange(lowerbound,upperbound+(upperbound - lowerbound)/20,(upperbound - lowerbound)/20)        
        #clevs = np.arange(np.min(comb_days),np.max(comb_days)+(np.max(comb_days)-np.min(comb_days))/10,(np.max(comb_days)-np.min(comb_days))/10)
        #clevs = np.arange(np.min(comb_days[i,:,:]),np.max(comb_days[i,:,:])+(np.max(comb_days[i,:,:])-np.min(comb_days[i,:,:]))/10,(np.max(comb_days[i,:,:])-np.min(comb_days[i,:,:]))/10)
        
        # shift the hours by a fixed amount to the start of the CMAQ day of interest
        cs = m.contourf(x,y,comb_days[i,:,:],clevs,cmap=cm.Spectral_r)
        # add colorbar.
        cbar = m.colorbar(cs,location='right',pad="0.00%")
        # add label
        #cbar.set_label('CF/ppbV')
        cbar.set_label(r'$\frac{ppb\:\mathrm{O_3}}{ppb\:\mathrm{NO_x}}$')
        
        # add title
        plt.title('Avg. Adj-sens of MDA1 [$\mathrm{O_3}$] wrt [$\mathrm{NO_x}$] for Jun 10')
        
        plt.tight_layout()
        pdf.savefig()   
        plt.close()
