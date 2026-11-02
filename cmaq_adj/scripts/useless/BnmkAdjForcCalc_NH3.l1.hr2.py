#!/home/cl3293/anaconda3/bin/python

### CHANGE: specify local python installation

from netCDF4 import Dataset
from math import fsum, exp
from random import uniform
import numpy as np

## Forcing of NH3 (or other selected species) at beginning of 2nd hour of June 10 for finite difference testing

# For benchmarking episode, which is 4 days in length - June 10 - 13, 2007
days = 10

# Iterate over this period of time
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
    
    # For each day, open the hourly average concentration file
    ### CHANGE: specify path
    concname = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day_base.l1.hr2/CONC.200706'+dStamp
    concfile = Dataset(concname, mode='r', open=True)
    
    # Read from output of model the ozone concentration
    NH3hr = np.squeeze(concfile.variables['NH3'][:][:][:][:])
    #NH3hr = concfile.variables[:][:][:][:][:]

    print("NH3hr.shape",NH3hr.shape) 
    # Prepare arrays to receive result of next calculation
    ltime, llay, lrow, lcol = (NH3hr.shape)
    llay = 1
    #dayNH3hrly = NH3hr[0:ltime+1,:,:]
    binNH3max  = np.zeros([ltime, llay, lrow, lcol])
    oneNH3max = np.ones([ltime,llay, lrow, lcol])
    forc_hr = 2
    binNH3max[forc_hr,:,:,:] = oneNH3max[1,:,:,:]
    
    # Write adjoint forcing to one file per day
    ### CHANGE: specify path
    forcNH3mxhrpath = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day_base.l1.hr2/ADJ_FORCE.200706'+dStamp
    forcNH3mxhrfile = Dataset(forcNH3mxhrpath, 'w', format='NETCDF3_64BIT')
    
    # I/O Api attributes to be included in forcing file (originally coded by M.Russell / Carleton.U)
    attrs=["IOAPI_VERSION", "EXEC_ID", "FTYPE", "CDATE", "CTIME", "WDATE", "WTIME", "SDATE", "STIME", "TSTEP", "NTHIK", "NCOLS", "NROWS", "GDTYP", "P_ALP", "P_BET", "P_GAM", "XCENT", "YCENT", "XORIG", "YORIG", "XCELL", "YCELL", "VGTYP", "VGTOP", "VGLVLS", "GDNAM", "HISTORY"]
    
    for attr in attrs:
        # Read the attribute
        if hasattr(concfile, attr): 
            attrVal = getattr(concfile, attr);
            # Write it to the forcing file
            setattr(forcNH3mxhrfile, attr, attrVal)
    
    setattr(forcNH3mxhrfile,"NVARS",1)
    setattr(forcNH3mxhrfile,"NLAYS",1) 
    setattr(forcNH3mxhrfile,"UPNAM","RD_FORCE_FILE")
    setattr(forcNH3mxhrfile,"VAR-LIST","NH3           ")
    setattr(forcNH3mxhrfile,"FILEDESC","Adjoint forcing file. Cost function: NH3 in every cell, second hour only (micrograms/m**3)")
    
    ltime, llay, lrow, lcol = (binNH3max.shape)
    llay = 1
    ldattim = 2
    ltime = 25
    
    forcNH3mxhrfile.createDimension("TSTEP", None)
    forcNH3mxhrfile.createDimension("DATE-TIME", ldattim)
    forcNH3mxhrfile.createDimension("LAY", llay)
    forcNH3mxhrfile.createDimension("VAR", 1)
    forcNH3mxhrfile.createDimension("ROW", lrow)
    forcNH3mxhrfile.createDimension("COL", lcol)
    
    forcNH3mxhrfile.sync()
   
    #dattim = np.squeeze(concfile.variables['TFLAG'][:][:])
    dattim = concfile.variables['TFLAG'][:][:]
    dattim = dattim[0:ltime,0,:]

    # Create variables
    forc_NH3hrmx_tflag = forcNH3mxhrfile.createVariable('TFLAG', 'i4', ('TSTEP', 'VAR', 'DATE-TIME'))
    forc_NH3hrmx_tflag[:] = np.zeros([ltime,llay,ldattim])
    forc_NH3hrmx_tflag[:] = np.reshape(dattim,[ltime,llay,ldattim])
    
    varattrs=["long_name","units","var_desc"]
    for varattr in varattrs:
        # Read the attribute
        if hasattr(concfile.variables['TFLAG'], varattr): 
            varattrVal = getattr(concfile.variables['TFLAG'], varattr);
            # Write it to the forcing file
            setattr(forc_NH3hrmx_tflag, varattr, varattrVal)
    
    forc_NH3hrmx = forcNH3mxhrfile.createVariable('NH3','f4',('TSTEP','LAY','ROW','COL'))
    forc_NH3hrmx[:] = np.zeros([ltime,llay,lrow,lcol])
    forc_NH3hrmx[:] = np.reshape(binNH3max,[ltime,llay,lrow,lcol])
    print("forc_NH3hrmx.shape",forc_NH3hrmx.shape)
    varattrs=["long_name","units","var_desc"]
    for varattr in varattrs:
        # Read the attribute
        if hasattr(concfile.variables['NH3'], varattr): 
            varattrVal = getattr(concfile.variables['NH3'], varattr);
            # Write it to the forcing file
            setattr(forc_NH3hrmx, varattr, varattrVal)
    
    forcNH3mxhrfile.close()

