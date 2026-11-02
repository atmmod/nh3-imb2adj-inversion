

from netCDF4 import Dataset
from shutil import copyfile

#NH3 active model ACONC
NH3_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day/ACONC.20070610'

NH3 = Dataset(NH3_file, 'r')

#Full model ACONC
force_file = '/mnt/HA/groups/cappsGrp/mm4862/CMAQ/cmaq_adj/CMAQadjBnmkData/output_base_NH3_testTracer/ACONC.20070610'
force = Dataset(force_file, 'r')

diff_file = '/mnt/HA/groups/cappsGrp/cl3293/CMAQ_adj_NH3/cmaq_adj/CMAQadjBnmkData/output_NH3_2day/diff.ncf'
copyfile(NH3_file, diff_file)

diff = Dataset(diff_file, 'a')
#diff = diff.groups['emis']
print (NH3['ANH4J'][:,0,:,:])
print (force['ANH4J'][:,0,:,:])
for var in ['NH3', 'ANH4I', 'ANH4J', 'ANO3I', 'ANO3J', 'ASO4I', 'ASO4J', 'HCL', 'HNO3']:
    print (var)
    diff[var][:,0,:,:] = force[var][:,0,:,:] - NH3[var][:,0,:,:]

diff.close()
#finalAnswer.close()
#prior.close()


