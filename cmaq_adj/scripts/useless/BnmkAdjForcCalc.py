#!/home/shannon/utilities/anaconda/bin/python

### CHANGE: specify local python installation

from netCDF4 import Dataset
from math import fsum, exp
from random import uniform
import numpy as np

## O3 forcing at 6th hour of 20070610

# For benchmarking episode, which is 4 days in length - June 10 - 13, 2007
days = 14

# Iterate over this period of time
for dd in range(10, days):
    # Ensure that the string for day will match the CMAQ file
    if (dd < 10):
        # Add zero before 
        small = str('0')
        dStamp = small+str(dd)
    else:
        dStamp = str(dd)
    
    
    # For each day, open the hourly average concentration file
    ### CHANGE: specify path
    concname = '/data/shannon/cmaqadj/bnmk/test_data/newoutput/CONC.200706'+dStamp
    concfile = Dataset(concname, mode='r', open=True)
    
    # Read from output of model the ozone concentration
    o3hr = np.squeeze(concfile.variables['O3'][:][:][:])
    
    # Prepare arrays to receive result of next calculation
    ltime, llay, lrow, lcol = (o3hr.shape)
    dayo3hrly = o3hr[0:25,1,:,:]
    dayO3mx  = np.zeros([ltime, lrow, lcol])
    binO3max = np.ones([ltime,lrow, lcol])
    binO3max = np.where(dayo3hrly[:,:,:] == np.max(dayo3hrly[:,:,:],axis=0), binO3max, dayO3mx)
    
    # Write adjoint forcing to one file per day
    ### CHANGE: specify path
    forcO3mxhrpath = '/data/shannon/cmaqadj/bnmk/test_data/newoutput/ADJ_FORCE.200706'+dStamp
    forcO3mxhrfile = Dataset(forcO3mxhrpath, 'w', format='NETCDF3_64BIT')
    
    # I/O Api attributes to be included in forcing file (originally coded by M.Russell / Carleton.U)
    attrs=["IOAPI_VERSION", "EXEC_ID", "FTYPE", "CDATE", "CTIME", "WDATE", "WTIME", "SDATE", "STIME", "TSTEP", "NTHIK", "NCOLS", "NROWS", "GDTYP", "P_ALP", "P_BET", "P_GAM", "XCENT", "YCENT", "XORIG", "YORIG", "XCELL", "YCELL", "VGTYP", "VGTOP", "VGLVLS", "GDNAM", "HISTORY"]
    
    for attr in attrs:
        # Read the attribute
        if hasattr(concfile, attr): 
            attrVal = getattr(concfile, attr);
            # Write it to the forcing file
            setattr(forcO3mxhrfile, attr, attrVal)
    
    setattr(forcO3mxhrfile,"NVARS",1)
    setattr(forcO3mxhrfile,"NLAYS",1) 
    setattr(forcO3mxhrfile,"UPNAM","RD_FORCE_FILE")
    setattr(forcO3mxhrfile,"VAR-LIST","O3             ")
    setattr(forcO3mxhrfile,"FILEDESC","Adjoint forcing file. Cost function: sum of max O3 in every cell, each day (ppm)")
    
    ltime, lrow, lcol = (binO3max.shape)
    llay = 1
    ldattim = 2
    ltime = 25
    
    forcO3mxhrfile.createDimension("TSTEP", None)
    forcO3mxhrfile.createDimension("DATE-TIME", ldattim)
    forcO3mxhrfile.createDimension("LAY", llay)
    forcO3mxhrfile.createDimension("VAR", 1)
    forcO3mxhrfile.createDimension("ROW", lrow)
    forcO3mxhrfile.createDimension("COL", lcol)
    
    forcO3mxhrfile.sync()
    
    dattim = np.squeeze(concfile.variables['TFLAG'][:][:])
    dattim = dattim[0:ltime,1,:]
    
    # Create variables
    forc_o3hrmx_tflag = forcO3mxhrfile.createVariable('TFLAG', 'i4', ('TSTEP', 'VAR', 'DATE-TIME'))
    forc_o3hrmx_tflag[:] = np.zeros([ltime,llay,ldattim])
    forc_o3hrmx_tflag[:] = np.reshape(dattim,[ltime,llay,ldattim])
    
    varattrs=["long_name","units","var_desc"]
    for varattr in varattrs:
        # Read the attribute
        if hasattr(concfile.variables['TFLAG'], varattr): 
            varattrVal = getattr(concfile.variables['TFLAG'], varattr);
            # Write it to the forcing file
            setattr(forc_o3hrmx_tflag, varattr, varattrVal)
    
    forc_o3hrmx = forcO3mxhrfile.createVariable('O3','f4',('TSTEP','LAY','ROW','COL'))
    forc_o3hrmx[:] = np.zeros([ltime,llay,lrow,lcol])
    forc_o3hrmx[:] = np.reshape(binO3max,[ltime,llay,lrow,lcol])
    
    varattrs=["long_name","units","var_desc"]
    for varattr in varattrs:
        # Read the attribute
        if hasattr(concfile.variables['O3'], varattr): 
            varattrVal = getattr(concfile.variables['O3'], varattr);
            # Write it to the forcing file
            setattr(forc_o3hrmx, varattr, varattrVal)
    
    forcO3mxhrfile.close()

