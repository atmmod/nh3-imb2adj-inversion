#!/home/cl3293/anaconda3/bin/python
### Script for evaluating the adjoint sensitivities against the finite difference ##

### CHANGE: specify local python installation on first line

import matplotlib as mpl
# apply so that no X window is necessary
mpl.use('Agg')
from netCDF4 import Dataset
import pandas as pd
from math import fsum, exp
from random import uniform
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.basemap import Basemap

# Goal: evaluate the CMAQ adjoint with concentration-based sensitivities
# - read the NH3 concentrations from CMAQ
# - plot the map of NH3 concentrations from CMAQ
# - plot the map of NH3 concentrations from perturbed forward run
# - read the NH3 sensitivities from adjoint
# - plot the sensitivities with respect to initial concentration from finite difference
# - plot the sensitivities with respect to initial concentration from adjoint
# - compare the sensitivities of adjoint against finite difference

forc_hr = 2
pert_hr = forc_hr - 1
pert = 0.2

## Ingest CMAQ hourly NH3 concentrations
days = 1

# iterate over this period of time
for dd in range(0, days):
    day = 10 + dd     
    # Ensure that the string for day will match the CMAQ file
    if (day < 10):
        # Add zero before 
        small = str('0')
        dStamp = small+str(day)
    else:
        dStamp = str(day)
    
    dStamp
    
    # For each day, open the NH3 average concentration file
    # CHANGE: specify location of base run files
    aconcbasename = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day.l22.hr2.base/ACONC.200706'+dStamp
    aconcbasefile = Dataset(aconcbasename, mode='r', open=True)
    # CHANGE: specify location of perturbation run files
    aconcpertname = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day.l22.hr2.base/ACONC.200706'+dStamp
    aconcpertfile = Dataset(aconcpertname, mode='r', open=True)
        
    # Read from output of model the NH3 concentration
    nh3hrbase = np.squeeze(aconcbasefile.variables['NH3'][:][:][:][:])
    nh3hrpert = np.squeeze(aconcpertfile.variables['NH3'][:][:][:][:])
    print("nh3hrpert.shape", nh3hrpert.shape) #(24, 34, 25, 25)
    lall = np.shape(nh3hrbase)
    if np.size(lall) == 4:
       nh3hrbase = nh3hrbase[:,0:22,:,:]
       nh3hrpert = nh3hrpert[:,0:22,:,:]
    
    # Combine the hourly NH3 concentrations
    if dd == 0:
        cnh3hrbase = nh3hrbase 
        cnh3hrpert = nh3hrpert
    else:
        cnh3hrbase = np.concatenate((cnh3hrbase,nh3hrbase),axis=0)
        cnh3hrpert = np.concatenate((cnh3hrpert,nh3hrpert),axis=0)
    
    concnh3hrbase = cnh3hrbase
    concnh3hrpert = cnh3hrpert
    
    concnh3hrbase = np.nansum(concnh3hrbase,axis=1)
    concnh3hrpert = np.nansum(concnh3hrpert,axis=1)
    
    ltime, lrow, lcol = (concnh3hrbase.shape)

# Calculate the difference between the perturbation and base case 
concnh3hrdiff = concnh3hrpert - concnh3hrbase
print("concnh3hrdiff.shape", concnh3hrdiff.shape) #(24, 25, 25)

# Load the adjoint sensitivity data

# Only the first day of information matters for the sensitivities, which are accumulated over time
days = 11
# iterate over this period of time
for dd in range(10, days):
    day = dd     
    # Ensure that the string for day will match the CMAQ file
    if (day < 10):
        # Add zero before 
        small = str('0')
        dStamp = small+str(day)
    else:
        dStamp = str(day)
    
    dStamp
    
    emisname = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/emis/emis_CMAQ-NH3_Tracer_200706'+dStamp+'.ncf'
    emisfile = Dataset(emisname, mode='r', open=True)
    emisnh3hr = np.squeeze(emisfile.variables['NH3'][:][:][:])
    #print("emisnh3hr.shape", emisnh3hr.shape) #(25, 25, 25)
    
    emissensname = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day.l22.hr2.base/EM.LGRID.bwd_NH3.200706'+dStamp
    emissensfile = Dataset(emissensname, mode='r', open=True)
    emisnh3hrsens = np.squeeze(emissensfile.variables['NH3'][:][:][:][:])
    #print("emisnh3hrsens.shape", emisnh3hrsens.shape) #(25, 25, 25)
    emisnh3hrsenssurf = emisnh3hrsens[pert_hr,:,:] * emisnh3hr[pert_hr,:,:]
    #print("emisnh3hrsenssurf.shape", emisnh3hrsenssurf.shape) #(25, 25)
    

    
    frcname = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day.l22.hr2.base/ADJ_FORCE.200706'+dStamp
    frcfile = Dataset(frcname, mode='r', open=True)
    nh3frc = np.squeeze(frcfile.variables['NH3'][:][:][:][:])
    nh3frc = np.nansum(nh3frc,axis=1)
    
    #np.sum(nh3frc)

# Get coordinates for map projection
latlonfilename = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/other/latlon.bnmk'
latlonfile = Dataset(latlonfilename, mode='r', open=True)

gridLat =  np.squeeze(latlonfile.variables['LAT'][:][:][:][:])
gridLon =  np.squeeze(latlonfile.variables['LON'][:][:][:][:])

last1ind,last2ind = gridLon.shape

loncrn = [gridLon[0,0],gridLon[last1ind-1,last2ind-1]]
latcrn = [gridLat[0,0],gridLat[last1ind-1,last2ind-1]]
lonmid = gridLon[last1ind//2,last2ind//2]
latmid = gridLat[last1ind//2-1,last2ind//2-1]

# Calculate the sensitivity with respect to emissions from finite difference
#    for only one synchronization time step perturbed
emfdsens = concnh3hrdiff[forc_hr,:,:]/(pert*emisnh3hr[pert_hr,:,:]) * emisnh3hr[pert_hr,:,:]


### Plot both monitoring sites and CMAQ output for each hour
# Create the PDFPages object for writing
#    CHANGE: specify location of file
with PdfPages('/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/plots/fdadj.NH3.jun10.0723.pdf') as pdf:
    
    # Hour range is the timeframe in the ingested CMAQ values to be plotted and compared
    ## For example, only day 1 of the days ingested above (May 30, 2007)
    # CHANGE: specify the CMAQ index that matches the time in the date range specified below

    # CHANGE: specify date range of interest (example is 24 hours beginning on May 30, 2007)
    rng = pd.date_range('6/10/2007',periods=3,freq='H')
    
    # Establish basemap
    m = Basemap(projection='lcc', llcrnrlon=loncrn[0], llcrnrlat=latcrn[0], urcrnrlon=loncrn[1], urcrnrlat=latcrn[1], lon_0=lonmid, lat_0=latmid, resolution='l')
    
    # draw coastlines, state and country boundaries, edge of map.
    m.drawcoastlines()
    m.drawstates()
    m.drawcountries()
    
    # Try plotting hourly NH3 from CMAQ
    ny = concnh3hrbase.shape[1]; nx = concnh3hrbase.shape[2]
    lons, lats = m.makegrid(nx, ny) # get lat/lons of ny by nx evenly space grid.
    x, y = m(lons, lats) # compute map proj coordinates.
    
    # draw filled contours.
    clevs = np.arange(np.min(concnh3hrbase),np.max(concnh3hrbase)*1.1,np.max(concnh3hrbase)*0.1)
    # shift the hours by a fixed amount to the start of the CMAQ day of interest
    cs = m.contourf(gridLon,gridLat,concnh3hrbase[forc_hr,:,:],clevs,cmap=cm.Spectral_r,vmin=np.min(concnh3hrbase),vmax=(np.max(concnh3hrbase)*1.10),latlon='true')
    
   # add colorbar.
    cbar = m.colorbar(cs,location='right',pad="5%")
    cbar.set_label('(ppm)')
    plt.tight_layout()
    
    # add title
    plt.title(r'Hourly $\mathrm{NH_3}$ for '+str(rng[forc_hr]))
    pdf.savefig()
    plt.close()
    
    # Establish basemap
    m = Basemap(projection='lcc', llcrnrlon=loncrn[0], llcrnrlat=latcrn[0], urcrnrlon=loncrn[1], urcrnrlat=latcrn[1], lon_0=lonmid, lat_0=latmid, resolution='l')
    
    # draw coastlines, state and country boundaries, edge of map.
    m.drawcoastlines()
    m.drawstates()
    m.drawcountries()
    
    # Plot perturbed hourly NH3 from CMAQ
    ny = concnh3hrpert.shape[1]; nx = concnh3hrpert.shape[2]
    lons, lats = m.makegrid(nx, ny) # get lat/lons of ny by nx evenly space grid.
    x, y = m(lons, lats) # compute map proj coordinates.
    
    # draw filled contours.
    clevs = np.arange(np.min(concnh3hrpert),np.max(concnh3hrpert)*1.10,np.max(concnh3hrpert)*.10)
    # shift the hours by a fixed amount to the start of the CMAQ day of interest
    cs = m.contourf(gridLon,gridLat,concnh3hrpert[forc_hr,:,:],clevs,cmap=cm.Spectral_r,vmin=np.min(concnh3hrpert),vmax=(np.max(concnh3hrpert)*1.10),latlon='true')
    
   # add colorbar.
    cbar = m.colorbar(cs,location='right',pad="5%")
    cbar.set_label('(ppm)')
    plt.tight_layout()
    
    # add title
    plt.title(r'Perturbed hourly $\mathrm{NH_3}$ for '+str(rng[forc_hr]))
    pdf.savefig()
    plt.close()
    
    # Establish basemap
    m = Basemap(projection='lcc', llcrnrlon=loncrn[0], llcrnrlat=latcrn[0], urcrnrlon=loncrn[1], urcrnrlat=latcrn[1], lon_0=lonmid, lat_0=latmid, resolution='l')
    
    # draw coastlines, state and country boundaries, edge of map.
    m.drawcoastlines()
    m.drawstates()
    m.drawcountries()
    
    # Try plotting hourly NH3 from CMAQ
    ny = concnh3hrdiff.shape[1]; nx = concnh3hrdiff.shape[2]
    lons, lats = m.makegrid(nx, ny) # get lat/lons of ny by nx evenly space grid.
    x, y = m(lons, lats) # compute map proj coordinates.
    
    # draw filled contours.
    clevs = np.arange(np.min(concnh3hrdiff),np.max(concnh3hrdiff)*1.1,np.max(concnh3hrdiff)*0.1)
    # shift the hours by a fixed amount to the start of the CMAQ day of interest
    cs = m.contourf(gridLon,gridLat,concnh3hrdiff[forc_hr,:,:],clevs,cmap=cm.Spectral_r,vmin=np.min(concnh3hrdiff),vmax=(np.max(concnh3hrdiff)*1.1),latlon='true')
    
    # add colorbar.
    cbar = m.colorbar(cs,location='right',pad="5%")
    cbar.set_label('(ppm)')
    plt.tight_layout()
    
    # add title
    plt.title(r'$\mathrm{\Delta NH_3}$|hr2 w/20% $\mathrm{NH_3}$ emis pert at hr1')
    pdf.savefig()
    plt.close()
    
    # Plot perturbed hourly NH3 from CMAQ
    ny = nh3frc.shape[1]; nx = nh3frc.shape[2]
    lons, lats = m.makegrid(nx, ny) # get lat/lons of ny by nx evenly space grid.
    x, y = m(lons, lats) # compute map proj coordinates.
    
    # draw filled contours.
    clevs = np.arange(np.min(nh3frc),np.max(nh3frc)*1.1,np.max(nh3frc)*.10)
    # shift the hours by a fixed amount to the start of the CMAQ day of interest
    cs = m.contourf(gridLon,gridLat,nh3frc[forc_hr,:,:],clevs,cmap=cm.Spectral_r,vmin=np.min(nh3frc),vmax=(np.max(nh3frc)*1.10),latlon='true')
    
   # add colorbar.
    cbar = m.colorbar(cs,location='right',pad="5%")
    cbar.set_label('')
    plt.tight_layout()
    
    # add title
    plt.title(r'Adjoint forcing of $\mathrm{NH_3}$ for '+str(rng[forc_hr]))
    pdf.savefig()
    plt.close()
    
    # Establish basemap
    m = Basemap(projection='lcc', llcrnrlon=loncrn[0], llcrnrlat=latcrn[0], urcrnrlon=loncrn[1], urcrnrlat=latcrn[1], lon_0=lonmid, lat_0=latmid, resolution='l')
    
    # draw coastlines, state and country boundaries, edge of map.
    m.drawcoastlines()
    m.drawstates()
    m.drawcountries()
    
    # iterate over dates
    forc_hr = forc_hr+1

    # Establish basemap
    m = Basemap(projection='lcc', llcrnrlon=loncrn[0], llcrnrlat=latcrn[0], urcrnrlon=loncrn[1], urcrnrlat=latcrn[1], lon_0=lonmid, lat_0=latmid, resolution='l')

    # draw coastlines, state and country boundaries, edge of map.
    m.drawcoastlines()
    m.drawstates()
    m.drawcountries()

    # Try plotting hourly NH3 from CMAQ
    ny = emfdsens.shape[0]; nx = emfdsens.shape[1]
    lons, lats = m.makegrid(nx, ny) # get lat/lons of ny by nx evenly space grid.
    x, y = m(lons, lats) # compute map proj coordinates.

    # draw filled contours.
    clevs = np.arange(np.min(emfdsens),np.max(emfdsens)*1.1,np.max(emfdsens)*0.1)
    # shift the hours by a fixed amount to the start of the CMAQ day of interest
    cs = m.contourf(gridLon,gridLat,emfdsens[:,:],clevs,cmap=cm.Spectral_r,vmin=np.min(emfdsens),vmax=(np.max(emfdsens)*1.1),latlon='true')

    # add colorbar.
    cbar = m.colorbar(cs,location='right',pad="5%")
    cbar.set_label('ppm/(mol/s)')
    plt.tight_layout()

    # add title
    plt.title(r'$\mathrm{\mathsf{FD: \frac{\Delta[NH_3]|_{hr2}}{20\%Emis_{NH_3}|hr1}}*Emis_{NH_3}|hr1}$')
    pdf.savefig()
    plt.close()

    # Establish basemap
    m = Basemap(projection='lcc', llcrnrlon=loncrn[0], llcrnrlat=latcrn[0], urcrnrlon=loncrn[1], urcrnrlat=latcrn[1], lon_0=lonmid, lat_0=latmid, resolution='l')

    # draw coastlines, state and country boundaries, edge of map.
    m.drawcoastlines()
    m.drawstates()
    m.drawcountries()

    # Try plotting hourly NH3 from CMAQ
    ny = emisnh3hrsenssurf.shape[0]; nx = emisnh3hrsenssurf.shape[1]
    lons, lats = m.makegrid(nx, ny) # get lat/lons of ny by nx evenly space grid.
    x, y = m(lons, lats) # compute map proj coordinates.

    # draw filled contours.
    clevs = np.arange(np.min(emisnh3hrsenssurf),np.max(emisnh3hrsenssurf)*1.1,np.max(emisnh3hrsenssurf)*0.1)
    # shift the hours by a fixed amount to the start of the CMAQ day of interest
    cs = m.contourf(gridLon,gridLat,emisnh3hrsenssurf[:,:],clevs,cmap=cm.Spectral_r,vmin=np.min(emisnh3hrsenssurf),vmax=(np.max(emisnh3hrsenssurf)*1.1),latlon='true')

    # add colorbar.
    cbar = m.colorbar(cs,location='right',pad="10%")
    cbar.set_label('ppm/(mol/s)')
    plt.tight_layout()

    # add title
    plt.title(r'$\mathrm{\mathsf{adj: \frac{\delta[NH_3]|_{hr2}}{\delta Emis_{NH_3}|hr1}}*Emis_{NH_3}|hr1}$')
    pdf.savefig()
    plt.close()

    # Create scatter plot
    fdarray = np.reshape(emfdsens,[-1,])
    adjarray = np.reshape(emisnh3hrsenssurf,[-1,])
    cs = plt.scatter(fdarray,adjarray) #, c=emisnh3hrsenssurf, cmap=cm.Spectral_r)
    rangemin = min(np.min(fdarray),np.min(adjarray))
    rangemax = max(np.max(fdarray),np.max(adjarray))
    v = [rangemin, rangemax, rangemin, rangemax]
    plt.axis(v)
    ax = plt.gca()
    ax.set_ylabel(r'$\mathrm{\mathsf{adj: \frac{\delta[NH_3]|_{hr2}}{\delta Emis_{NH_3}|_{hr1}}}*Emis_{NH_3}|_{hr1}}$', fontsize= 14)
    ax.set_xlabel(r'$\mathrm{\mathsf{FD: \frac{\Delta[NH_3]|_{hr2}}{20\%Emis_{NH_3}|_{hr1}}}*Emis_{NH_3}|_{hr1}}$', fontsize= 14)
        
    #add standard 1:1 line
    plt.plot( [rangemin,rangemax],[rangemin,rangemax] )
    #add linear regression
    plt.plot(np.unique(fdarray), np.poly1d(np.polyfit(fdarray, adjarray, 1))(np.unique(fdarray)))
    par = np.polyfit(fdarray, adjarray, 1, full=True)
    slope=par[0][0]
    intercept=par[0][1]
    variance = np.var(adjarray)
    residuals = np.var([(slope*xx + intercept - yy)  for xx,yy in zip(fdarray,adjarray)])
    Rsqr = np.round(1-residuals/variance, decimals=2)
    plt.text(0.9*min(fdarray)+0.1*max(fdarray),0.2*min(adjarray)+0.7*max(adjarray),'$k = %0.2f$'% slope, fontsize=14)
    plt.text(0.9*min(fdarray)+0.1*max(fdarray),0.1*min(adjarray)+0.8*max(adjarray),'$b = %0.2f$'% intercept, fontsize=14)
    plt.text(0.9*min(fdarray)+0.1*max(fdarray),0*min(adjarray)+0.9*max(adjarray),'$R^2 = %0.2f$'% Rsqr, fontsize=14)
   
   # change tick font size
    ax.tick_params(labelsize=14)
    plt.xticks(rotation=45)
    #cb = plt.colorbar()
    #cb.set_label('ppm/(mol/s)')
    plt.tight_layout()

    # add title
    #plt.title('Evaluate emis sensitivities')
    pdf.savefig()
    plt.close()






