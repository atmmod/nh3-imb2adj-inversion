# =============================================================================
# IMB2: iterative moving-box mass balance ("MB"/"mb" in the code, e.g. mb_scal)
#
# Authors: Congmeng Lyu (CU CIRES / NOAA CSL), Shannon L. Capps (Drexel University)
# 
# Extracted from py4dvar/fourdvar/_main_driver.py of the py4dvar
# working copy used for the April 2017 36US2 NH3 production run (gama = 5000):
# 
# The 4D-Var routines in the same file (cost_func, gradient_func, get_answer;) 
# are not included, and the original 4DVar code are available at: 
# https://github.com/steven-thomas/py4dvar
#
# Notice of modification (Apache License 2.0, Section 4(b)): this file is
# derived from _main_driver.py of the py4dvar framework
# (https://github.com/steven-thomas/py4dvar, Copyright 2016 University of
# Melbourne). mb_scal() is not part of the original framework; it was added in
# the modified version by the Drexel University team. 
# This extract keeps only that routine, with the original header, imports and gama.
# =============================================================================
"""
_main_driver.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""
import os
import numpy as np
from scipy.optimize import fmin_l_bfgs_b as minimize
import time
from fourdvar import datadef as d
from fourdvar._transform import transform
from fourdvar._transform import transform_mb
from fourdvar import user_driver
import fourdvar.params.data_access as data_access
import fourdvar.params.archive_defn as archive_defn
import setup_logging
import fourdvar.util.cmaq_handle as cmaq_handle
from netCDF4 import Dataset
logger = setup_logging.get_logger( __file__ )
from fourdvar.params.root_path_defn import store_path
from fourdvar.params.root_path_defn import latlon_path
import fourdvar.params.cmaq_config as cmaq_config

#define gama
gama = 5000.0

##########################################################################################
#mb_physical
def mb_scal():
    """
    framework: mb method main_driver
    input: numpy.ndarray
    output: scalar
    """
    start_time = time.time()
    
    ######################################################################################
    #load cmaq latlon file 
    cmaq_coord_file = os.path.join(latlon_path, 'GRDFILE_36US2')
    ccoordfile = Dataset(cmaq_coord_file,'r') # Read file
    # arrays are in the format of (TSTEP,LAY,ROW,COL);(1,1,80,100)
    lat = np.asarray(ccoordfile.variables["LAT"])            # latitude (degrees)(south negative)
    lon = np.asarray(ccoordfile.variables["LON"])            #longitude (degrees)(west negative)
    ccoordfile.close()

    CMAQ_lats = lat[0, 0, :, :]
    CMAQ_lons = lon[0, 0, :, :]
    
    ######################################################################################
    #create vector index to row col mapping
    nrow = cmaq_config.model_row
    ncol = cmaq_config.model_col
    index_row_col_map = np.zeros([nrow*ncol,2])
    for row in range(0, nrow):
        for col in range(0, ncol):
            index = row*ncol + col
            index_row_col_map[index,0] = row
            index_row_col_map[index,1] = col
    #print("index_row_col_map", index_row_col_map)
    
    ######################################################################################
    #get 36km to n*36km index mapping
    #NH3 average life time in the US: 12 hours
    #horizontal average wind speed in the US: 10 m/s (including elevated layers)
    #so, emissions of NH3 from one given grid cell can transport a maximum distance of 10m/s*12hrs*3600s/hr=432km
    #that is equivalent to 12 36km-grid cells
    #we use box average observation to inform emission changes in the whole box,
    #so emissions from every single grid cell within the box should be able to influence concentrations in the box
    #the most extreme situation is the emissions from one edge of the moving box have to be able to influence concentrations on the other edge, 
    #that is the basis of Mass Balance approach.
    #so, cells on opposite edges of the box are 12 grid cells (432 km) apart, center to center: n=1+6*2=13, 13 by 13 moving box
    trans_rad = 6 
    box_edge = 1+trans_rad*2
    box_num_grid = box_edge**2
    coars_map = np.ones([nrow*ncol,box_num_grid]) * np.nan
    
    #for each grid cell on the COUNS domain
    for center_row in range(0,nrow):
        for center_col in range(0,ncol):
            center_index = int(center_row*ncol + center_col)
            #first determine the surrounding grid cells' row col indices
            count_sur = 0
            for sur_row in range((center_row-trans_rad), (center_row+trans_rad+1)):
                for sur_col in range((center_col-trans_rad), (center_col+trans_rad+1)):
                    #second, calculate the surrounding grid cells' indices in the vector space
                    if sur_row >=0 and sur_row < nrow and sur_col >=0 and sur_col < ncol:
                        sur_ind = int(sur_row*ncol + sur_col)
                    else:
                        sur_ind = np.nan
                    #Third, document the surrounding grid cells' indexes
                    coars_map[center_index,count_sur] = sur_ind
                    count_sur += 1
    logger.info( 'coarser resolution simulator map generated' )
    
    ######################################################################################
    #set up averaged total column observation, Omega_o_bar
    observed_avg_tot_col = user_driver.get_observed_avg_tot_col()#avg. total column observation, Omega_o_bar
    observed_avg_tot_col_vector = observed_avg_tot_col.get_vector()# 0 and value
    #if value equals to 0, make it NaN
    observed_avg_tot_col_vector[observed_avg_tot_col_vector==0] = np.nan
    
    #get moving box average
    observed_mbox_avg_tot_col_vector = observed_avg_tot_col_vector.copy()
    for center_row in range(0,nrow):
        for center_col in range(0,ncol):
            center_index = int(center_row*ncol + center_col)
            sur_ind_all = coars_map[center_index,:] #13*13, has nan
            #remove nan elements
            sur_ind_all = sur_ind_all[~np.isnan(sur_ind_all)].astype(int)
            observed_mbox_avg_tot_col_vector[center_index] = np.nanmean(observed_avg_tot_col_vector[sur_ind_all])
    
    ######################################################################################
    MB_no = 0
    
    #sigma_a(0) data ----> Omega_a_bar(0)
    phy_sigma_a = user_driver.get_background_mb() #unitless proportional emission factors, 1, sigma_a(0)
    unk_sigma_a = transform( phy_sigma_a, d.UnknownData ) #condition: proportional emission factors/proportional uncertainty, 1/1
    unk_sigma_init = unk_sigma_a
    model_in_a = transform( phy_sigma_a, d.ModelInputData ) #prepare_mode: proportional emission factors * template_emis(mol/s), which is initial guess of emission (halved of true emission before calling make_template.py), so current factor*50% true emission
    model_out_a = transform_mb( model_in_a, d.ModelOutputData ) #run model
    CMAQ_retv_a = transform( model_out_a, d.ObservationData ) #obs_operator
    CMAQ_tot_col_a = transform( CMAQ_retv_a, d.ObservationData_tot_col )  #retv_2_tot_col, just take the ground layer of retrievals at this point
    CMAQ_avg_tot_col_a = transform( CMAQ_tot_col_a, d.ObservationData_avg_tot_col )  #avg_tot_col, get Omega_a_bar, data in shape row*col, zero or value
    CMAQ_avg_tot_col_a_vector = CMAQ_avg_tot_col_a.get_vector()
    #if value equals to 0, make it NaN
    CMAQ_avg_tot_col_a_vector[CMAQ_avg_tot_col_a_vector==0] = np.nan
    
    #get moving box average
    CMAQ_mbox_avg_tot_col_a_vector = CMAQ_avg_tot_col_a_vector.copy()
    for center_row in range(0,nrow):
        for center_col in range(0,ncol):
            center_index = int(center_row*ncol + center_col)
            sur_ind_all = coars_map[center_index,:] #13*13, has nan
            #remove nan elements
            sur_ind_all = sur_ind_all[~np.isnan(sur_ind_all)].astype(int)
            CMAQ_mbox_avg_tot_col_a_vector[center_index] = np.nanmean(CMAQ_avg_tot_col_a_vector[sur_ind_all])

    ##########################################################################################   
    #cost function initial value
    bg_vector = unk_sigma_a.get_vector() #one time define, does not change
    un_vector = unk_sigma_a.get_vector() #changes in each iteration
    bg_cost = 0.5 * gama * np.sum( ( un_vector - bg_vector )**2 ) #changes in each iteration
    logger.info( 'bg_cost init = {:}'.format( bg_cost ) ) #changes in each iteration
    
    observed_avg = user_driver.get_observed_avg()#avg. pseudo observation, one time define, does not change
    simulated_avg = transform( model_out_a, d.ObservationData_avg ) #obs_operator_avg, changes in each iteration
    residual = d.ObservationData_avg.get_residual( observed_avg, simulated_avg ) #changes in each iteration
    w_residual = d.ObservationData_avg.error_weight( residual ) #devide by average unc, changes in each iteration
    res_vector = residual.get_vector() #changes in each iteration
    wres_vector = w_residual.get_vector() #changes in each iteration
    ob_cost = 0.5 * np.sum( res_vector * wres_vector ) #changes in each iteration
    logger.info( 'ob_cost init = {:}'.format( ob_cost ) ) #changes in each iteration
    
    cost_init = bg_cost + ob_cost #changes in each iteration
    logger.info( 'cost init = {:}'.format( cost_init ) ) #changes in each iteration
    
    ob_cost_previous = ob_cost
    
    #########################################################################################
    ####################
    #raw norm_diff_omega
    diff_omega = observed_mbox_avg_tot_col_vector - CMAQ_mbox_avg_tot_col_a_vector #might be zero
    norm_diff_omega = np.multiply(diff_omega, np.reciprocal(CMAQ_mbox_avg_tot_col_a_vector))

    #get statistics of the raw norm_diff_omega
    raw_norm_diff_omega_mean = np.nanmean(norm_diff_omega)
    raw_norm_diff_omega_std = np.nanstd(norm_diff_omega)
    raw_norm_diff_omega_max = np.nanmax(norm_diff_omega)
    raw_norm_diff_omega_min = np.nanmin(norm_diff_omega)
    logger.info( 'raw_norm_diff_omega_mean = {:}'.format( raw_norm_diff_omega_mean ) )
    logger.info( 'raw_norm_diff_omega_std = {:}'.format( raw_norm_diff_omega_std ) )
    logger.info( 'raw_norm_diff_omega_max = {:}'.format( raw_norm_diff_omega_max ) )
    logger.info( 'raw_norm_diff_omega_min = {:}'.format( raw_norm_diff_omega_min ) )
    
    p995_norm_diff_omega = np.nanpercentile(norm_diff_omega, 99.5)
    p990_norm_diff_omega = np.nanpercentile(norm_diff_omega, 99.0)
    p985_norm_diff_omega = np.nanpercentile(norm_diff_omega, 98.5)
    p980_norm_diff_omega = np.nanpercentile(norm_diff_omega, 98.0)
    p975_norm_diff_omega = np.nanpercentile(norm_diff_omega, 97.5)
    p970_norm_diff_omega = np.nanpercentile(norm_diff_omega, 97.0)
    p965_norm_diff_omega = np.nanpercentile(norm_diff_omega, 96.5)
    p960_norm_diff_omega = np.nanpercentile(norm_diff_omega, 96.0)
    p955_norm_diff_omega = np.nanpercentile(norm_diff_omega, 95.5)
    p950_norm_diff_omega = np.nanpercentile(norm_diff_omega, 95.0)
    p050_norm_diff_omega = np.nanpercentile(norm_diff_omega, 5.0)
    p045_norm_diff_omega = np.nanpercentile(norm_diff_omega, 4.5)
    p040_norm_diff_omega = np.nanpercentile(norm_diff_omega, 4.0)
    p035_norm_diff_omega = np.nanpercentile(norm_diff_omega, 3.5)
    p030_norm_diff_omega = np.nanpercentile(norm_diff_omega, 3.0)
    p025_norm_diff_omega = np.nanpercentile(norm_diff_omega, 2.5)
    p020_norm_diff_omega = np.nanpercentile(norm_diff_omega, 2.0)
    p015_norm_diff_omega = np.nanpercentile(norm_diff_omega, 1.5)
    p010_norm_diff_omega = np.nanpercentile(norm_diff_omega, 1.0)
    p005_norm_diff_omega = np.nanpercentile(norm_diff_omega, 0.5)

    logger.info( 'raw norm_diff_omega 99.5 percentile = {:}'.format( p995_norm_diff_omega ) )
    logger.info( 'raw norm_diff_omega 99.0 percentile = {:}'.format( p990_norm_diff_omega ) )
    logger.info( 'raw norm_diff_omega 98.5 percentile = {:}'.format( p985_norm_diff_omega ) )
    logger.info( 'raw norm_diff_omega 98.0 percentile = {:}'.format( p980_norm_diff_omega ) )
    logger.info( 'raw norm_diff_omega 97.5 percentile = {:}'.format( p975_norm_diff_omega ) )
    logger.info( 'raw norm_diff_omega 97.0 percentile = {:}'.format( p970_norm_diff_omega ) )
    logger.info( 'raw norm_diff_omega 96.5 percentile = {:}'.format( p965_norm_diff_omega ) )
    logger.info( 'raw norm_diff_omega 96.0 percentile = {:}'.format( p960_norm_diff_omega ) )
    logger.info( 'raw norm_diff_omega 95.5 percentile = {:}'.format( p955_norm_diff_omega ) )
    logger.info( 'raw norm_diff_omega 95.0 percentile = {:}'.format( p950_norm_diff_omega ) )
    logger.info( 'raw norm_diff_omega 5.0 percentile = {:}'.format( p050_norm_diff_omega ) )
    logger.info( 'raw norm_diff_omega 4.5 percentile = {:}'.format( p045_norm_diff_omega ) )
    logger.info( 'raw norm_diff_omega 4.0 percentile = {:}'.format( p040_norm_diff_omega ) )
    logger.info( 'raw norm_diff_omega 3.5 percentile = {:}'.format( p035_norm_diff_omega ) )
    logger.info( 'raw norm_diff_omega 3.0 percentile = {:}'.format( p030_norm_diff_omega ) )
    logger.info( 'raw norm_diff_omega 2.5 percentile = {:}'.format( p025_norm_diff_omega ) )
    logger.info( 'raw norm_diff_omega 2.0 percentile = {:}'.format( p020_norm_diff_omega ) )
    logger.info( 'raw norm_diff_omega 1.5 percentile = {:}'.format( p015_norm_diff_omega ) )
    logger.info( 'raw norm_diff_omega 1.0 percentile = {:}'.format( p010_norm_diff_omega ) )
    logger.info( 'raw norm_diff_omega 0.5 percentile = {:}'.format( p005_norm_diff_omega ) )
    
    #########################################################################################
    ####################
    #raw sig_adj_frac
    sig_adj_frac = norm_diff_omega.copy()

    #get moving box average
    mbox_sig_adj_frac = sig_adj_frac.copy()
    for center_row in range(0,nrow):
        for center_col in range(0,ncol):
            center_index = int(center_row*ncol + center_col)
            sur_ind_all = coars_map[center_index,:] #13*13, has nan
            #remove nan elements
            sur_ind_all = sur_ind_all[~np.isnan(sur_ind_all)].astype(int)
            mbox_sig_adj_frac[center_index] = np.nanmean(sig_adj_frac[sur_ind_all])
    
    sig_adj_frac = mbox_sig_adj_frac.copy()

    #get statistics of the raw sig_adj_frac
    raw_sig_adj_frac_mean = np.nanmean(sig_adj_frac)
    raw_sig_adj_frac_std = np.nanstd(sig_adj_frac)
    raw_sig_adj_frac_max = np.nanmax(sig_adj_frac)
    raw_sig_adj_frac_min = np.nanmin(sig_adj_frac)
    logger.info( 'raw_sig_adj_frac_mean = {:}'.format( raw_sig_adj_frac_mean ) )
    logger.info( 'raw_sig_adj_frac_std = {:}'.format( raw_sig_adj_frac_std ) )
    logger.info( 'raw_sig_adj_frac_max = {:}'.format( raw_sig_adj_frac_max ) )
    logger.info( 'raw_sig_adj_frac_min = {:}'.format( raw_sig_adj_frac_min ) )

    p995_sig_adj_frac = np.nanpercentile(sig_adj_frac, 99.5)
    p990_sig_adj_frac = np.nanpercentile(sig_adj_frac, 99.0)
    p985_sig_adj_frac = np.nanpercentile(sig_adj_frac, 98.5)
    p980_sig_adj_frac = np.nanpercentile(sig_adj_frac, 98.0)
    p975_sig_adj_frac = np.nanpercentile(sig_adj_frac, 97.5)
    p970_sig_adj_frac = np.nanpercentile(sig_adj_frac, 97.0)
    p965_sig_adj_frac = np.nanpercentile(sig_adj_frac, 96.5)
    p960_sig_adj_frac = np.nanpercentile(sig_adj_frac, 96.0)
    p955_sig_adj_frac = np.nanpercentile(sig_adj_frac, 95.5)
    p950_sig_adj_frac = np.nanpercentile(sig_adj_frac, 95.0)
    p050_sig_adj_frac = np.nanpercentile(sig_adj_frac, 5.0)
    p045_sig_adj_frac = np.nanpercentile(sig_adj_frac, 4.5)
    p040_sig_adj_frac = np.nanpercentile(sig_adj_frac, 4.0)
    p035_sig_adj_frac = np.nanpercentile(sig_adj_frac, 3.5)
    p030_sig_adj_frac = np.nanpercentile(sig_adj_frac, 3.0)
    p025_sig_adj_frac = np.nanpercentile(sig_adj_frac, 2.5)
    p020_sig_adj_frac = np.nanpercentile(sig_adj_frac, 2.0)
    p015_sig_adj_frac = np.nanpercentile(sig_adj_frac, 1.5)
    p010_sig_adj_frac = np.nanpercentile(sig_adj_frac, 1.0)
    p005_sig_adj_frac = np.nanpercentile(sig_adj_frac, 0.5)

    logger.info( 'raw sig_adj_frac 99.5 percentile = {:}'.format( p995_sig_adj_frac ) )
    logger.info( 'raw sig_adj_frac 99.0 percentile = {:}'.format( p990_sig_adj_frac ) )
    logger.info( 'raw sig_adj_frac 98.5 percentile = {:}'.format( p985_sig_adj_frac ) )
    logger.info( 'raw sig_adj_frac 98.0 percentile = {:}'.format( p980_sig_adj_frac ) )
    logger.info( 'raw sig_adj_frac 97.5 percentile = {:}'.format( p975_sig_adj_frac ) )
    logger.info( 'raw sig_adj_frac 97.0 percentile = {:}'.format( p970_sig_adj_frac ) )
    logger.info( 'raw sig_adj_frac 96.5 percentile = {:}'.format( p965_sig_adj_frac ) )
    logger.info( 'raw sig_adj_frac 96.0 percentile = {:}'.format( p960_sig_adj_frac ) )
    logger.info( 'raw sig_adj_frac 95.5 percentile = {:}'.format( p955_sig_adj_frac ) )
    logger.info( 'raw sig_adj_frac 95.0 percentile = {:}'.format( p950_sig_adj_frac ) )
    logger.info( 'raw sig_adj_frac 5.0 percentile = {:}'.format( p050_sig_adj_frac ) )
    logger.info( 'raw sig_adj_frac 4.5 percentile = {:}'.format( p045_sig_adj_frac ) )
    logger.info( 'raw sig_adj_frac 4.0 percentile = {:}'.format( p040_sig_adj_frac ) )
    logger.info( 'raw sig_adj_frac 3.5 percentile = {:}'.format( p035_sig_adj_frac ) )
    logger.info( 'raw sig_adj_frac 3.0 percentile = {:}'.format( p030_sig_adj_frac ) )
    logger.info( 'raw sig_adj_frac 2.5 percentile = {:}'.format( p025_sig_adj_frac ) )
    logger.info( 'raw sig_adj_frac 2.0 percentile = {:}'.format( p020_sig_adj_frac ) )
    logger.info( 'raw sig_adj_frac 1.5 percentile = {:}'.format( p015_sig_adj_frac ) )
    logger.info( 'raw sig_adj_frac 1.0 percentile = {:}'.format( p010_sig_adj_frac ) )
    logger.info( 'raw sig_adj_frac 0.5 percentile = {:}'.format( p005_sig_adj_frac ) )
    
    sig_adj_frac = np.clip(sig_adj_frac, -0.99,99)

    #########################################################################################    
    scaling_factors = sig_adj_frac + 1.0 #nan & extreme #alpha_i

    #plot adjustment factors before IDW, plot alpha_k*
    scaling_factors_matrix = np.zeros([nrow, ncol])
    for i in range(0,len(scaling_factors)):
        row_sf = int(index_row_col_map[i,0]) #row
        col_sf = int(index_row_col_map[i,1]) #col
        scaling_factors_matrix[row_sf, col_sf] = scaling_factors[i] #alpha_i
    iteration_number = MB_no + 1
    before_IDW = True
    where_are_NaNs = np.isnan(scaling_factors_matrix)
    scaling_factors_matrix[where_are_NaNs] = 1.0 #nan to 1.0 #alpha_g* U alpha_i = alpha_k*
    cmaq_handle.plot_scal_factors(scaling_factors_matrix, iteration_number, before_IDW) #plot alpha_k*

    adj_frac_NaN_ind = np.isnan(scaling_factors)
    #print("adj_frac_NaN_ind", adj_frac_NaN_ind) #True or False

    #create unknown&known arrays
    number_unknown = np.count_nonzero(adj_frac_NaN_ind)
    number_known = nrow*ncol
    factor_unknown = np.zeros([number_unknown,2])
    factor_known = np.zeros([number_known])

    unknown_index, = np.where(adj_frac_NaN_ind)
    #print('unknown_index', unknown_index)
    count_unknown = 0
    for unknown_ind in unknown_index:
        factor_unknown[count_unknown,0] = int(index_row_col_map[unknown_ind,0])
        factor_unknown[count_unknown,1] = int(index_row_col_map[unknown_ind,1])
        count_unknown += 1
    #print("factor_unknown", factor_unknown)
 
    count_known = 0
    scaling_factors[adj_frac_NaN_ind] = 1.0 #nan to 1 #alpha_g* U alpha_i = alpha_k*
    for known_ind in range(0,len(scaling_factors)):
        factor_known[count_known] = scaling_factors[known_ind] #alpha_k*
        count_known += 1  
    #print("factor_known", factor_known)

    #Apply spatial interpolation (IDW)
    sur_grid_edge = box_edge
    sur_grid_num = sur_grid_edge**2
    distance_array = np.zeros([number_unknown,sur_grid_num]) #MemoryError
    logger.info( 'distance_array created' )
    for unknown_count in range(0,number_unknown):
        unkcoord = []
        unk_row = int(factor_unknown[unknown_count,0])
        unk_col = int(factor_unknown[unknown_count,1])
        unkcoord.append((CMAQ_lats[unk_row, unk_col], CMAQ_lons[unk_row, unk_col]))
        #prepare surrounding grid cells factor_known_sur
        sur_num = 0
        factor_known_sur = np.zeros([sur_grid_num])
        knowncoords_sur = []
        #first determine the surrounding grid cells' row col based on unk_row, unk_col
        for sur_row in range((unk_row-((sur_grid_edge-1)/2.0)), (unk_row+((sur_grid_edge-1)/2.0)+1)):
            for sur_col in range((unk_col-((sur_grid_edge-1)/2.0)), (unk_col+((sur_grid_edge-1)/2.0)+1)):
                if sur_row >=0 and sur_row < nrow and sur_col >=0 and sur_col < ncol:
                    #second, calculate the surrounding grid cells' indexes in the vector space
                    sur_ind = sur_row*ncol + sur_col
                    #Third, use the surrounding grid cells' indexes to get a subset of factor_known
                    #Also need to get a subset of knowncoords (index order) to get the surrounding grid cells' coords
                    factor_known_sur[sur_num] = factor_known[sur_ind]
                    knowncoords_sur.append((CMAQ_lats[sur_row, sur_col], CMAQ_lons[sur_row, sur_col]))
                else:
                    factor_known_sur[sur_num] = np.nan
                    knowncoords_sur.append((np.nan,np.nan))
                sur_num += 1
        scaling_factors[int(unk_row*ncol + unk_col)], distance_array[unknown_count, :] = cmaq_handle.CalcIDWvalue_1st(unkcoord, knowncoords_sur, factor_known_sur) #alpha_g U alpha_i = alpha_k
    #print("scaling_factors after IDW", scaling_factors)
    #print("distance_array", distance_array)
    logger.info( 'CalcIDWvalue_1st finished' )

    #save alpha_g of current iteration for use as alpha_g* of next iteration
    scaling_factors_IDW = scaling_factors.copy()

    #plot adjustment factors after IDW plot alpha_k
    scaling_factors_matrix = np.zeros([nrow, ncol])
    for i in range(0,len(scaling_factors)):
        row_sf = int(index_row_col_map[i,0]) #row
        col_sf = int(index_row_col_map[i,1]) #col
        scaling_factors_matrix[row_sf, col_sf] = scaling_factors[i]
    before_IDW = False
    cmaq_handle.plot_scal_factors(scaling_factors_matrix, iteration_number, before_IDW) #plot alpha_k

    #########################################################################################
    #Perform mb scaling
    #scaling_factors are just for one layer, need to make it em.lays to scale the 4D emissions sigma
    fDemis_lay = cmaq_config.fDemis_lay
    scal_fct_em_lay = np.zeros([fDemis_lay*nrow*ncol])
    for ll in range(0,fDemis_lay):
        scal_fct_em_lay[(ll*nrow*ncol):((ll+1)*nrow*ncol)] = scaling_factors
    unk_sigma_t_vector = unk_sigma_a.get_vector() * scal_fct_em_lay
    #limit unk_sigma_t_vector to be 0.1 to 10
    unk_sigma_t_vector = np.clip(unk_sigma_t_vector, 0.1, 10.0)
    unk_sigma_t = d.UnknownData(unk_sigma_t_vector) #mb_emis_scal
    ########################################################################################
    #output sigma at this iteration includes plot emission factors
    user_driver.callback_func(unk_sigma_t.get_vector())
    #########################################################################################
    MB_no = MB_no + 1
    logger.info( 'MB_no = {:}'.format( MB_no ) ) #changes in each iteration 
    #########################################################################################
    NMD = (np.nansum(np.abs(unk_sigma_t.get_vector() - unk_sigma_a.get_vector())))/(np.nansum(unk_sigma_a.get_vector()))
    logger.info( 'NMD = {:}'.format( NMD ) ) #changes in each iteration
    ##########################################################################################
    #Accumulated scaling from mb prior 
    accum_scal = (np.nanmean(unk_sigma_t.get_vector()))/(np.nanmean(unk_sigma_init.get_vector()))
    logger.info( 'accum_scal = {:}'.format( accum_scal ) ) #changes in each iteration
    ##########################################################################################   
    #cost function value after the mb scaling
    un_vector = unk_sigma_t.get_vector() #changes in each iteration
    bg_cost = 0.5 * gama * np.sum( ( un_vector - bg_vector )**2 ) #changes in each iteration
    logger.info( 'bg_cost = {:}'.format( bg_cost ) ) #changes in each iteration

    phy_sigma_t = transform( unk_sigma_t, d.PhysicalData ) #uncondition, proportional emission factors
    model_in_t = transform( phy_sigma_t, d.ModelInputData ) #prepare_mode: proportional emission factors * template_emis(mol/s), which is initial guess of emission (halved of true emission before calling make_template.py), so current factor*50% true emission
    model_out_t = transform_mb( model_in_t, d.ModelOutputData ) #run model
    simulated_avg = transform( model_out_t, d.ObservationData_avg ) #obs_operator_avg, changes in each iteration
    residual = d.ObservationData_avg.get_residual( observed_avg, simulated_avg ) #changes in each iteration
    w_residual = d.ObservationData_avg.error_weight( residual ) #devide by average unc, changes in each iteration
    res_vector = residual.get_vector() #changes in each iteration
    wres_vector = w_residual.get_vector() #changes in each iteration
    ob_cost = 0.5 * np.sum( res_vector * wres_vector ) #changes in each iteration
    logger.info( 'ob_cost = {:}'.format( ob_cost ) ) #changes in each iteration

    cost = bg_cost + ob_cost #changes in each iteration
    logger.info( 'cost = {:}'.format( cost ) ) #changes in each iteration

    #########################################################################################
    end_time = time.time()
    logger.info( 'iteration completed in {:}s'.format(int(end_time-start_time) ) )   
    #########################################################################################

    #determine if continue iterations
    while NMD >= 0.05 and ob_cost <= ob_cost_previous:
        start_time = time.time()
        ob_cost_previous = ob_cost
        unk_sigma_a = unk_sigma_t
        CMAQ_retv_a = transform( model_out_t, d.ObservationData ) #obs_operator
        CMAQ_tot_col_a = transform( CMAQ_retv_a, d.ObservationData_tot_col )  #retv_2_tot_col
        CMAQ_avg_tot_col_a = transform( CMAQ_tot_col_a, d.ObservationData_avg_tot_col )  #avg_tot_col, get Omega_a_bar
        CMAQ_avg_tot_col_a_vector = CMAQ_avg_tot_col_a.get_vector()
        #if value equals to 0, make it NaN
        CMAQ_avg_tot_col_a_vector[CMAQ_avg_tot_col_a_vector==0] = np.nan

        #get moving box average
        CMAQ_mbox_avg_tot_col_a_vector = CMAQ_avg_tot_col_a_vector.copy()
        for center_row in range(0,nrow):
            for center_col in range(0,ncol):
                center_index = int(center_row*ncol + center_col)
                sur_ind_all = coars_map[center_index,:] #13*13, has nan
                #remove nan elements
                sur_ind_all = sur_ind_all[~np.isnan(sur_ind_all)].astype(int)
                CMAQ_mbox_avg_tot_col_a_vector[center_index] = np.nanmean(CMAQ_avg_tot_col_a_vector[sur_ind_all])
                
        #########################################################################################
        ####################
        #raw norm_diff_omega
        diff_omega = observed_mbox_avg_tot_col_vector - CMAQ_mbox_avg_tot_col_a_vector #might be zero
        norm_diff_omega = np.multiply(diff_omega, np.reciprocal(CMAQ_mbox_avg_tot_col_a_vector))

        #get statistics of the raw norm_diff_omega
        raw_norm_diff_omega_mean = np.nanmean(norm_diff_omega)
        raw_norm_diff_omega_std = np.nanstd(norm_diff_omega)
        raw_norm_diff_omega_max = np.nanmax(norm_diff_omega)
        raw_norm_diff_omega_min = np.nanmin(norm_diff_omega)
        logger.info( 'raw_norm_diff_omega_mean = {:}'.format( raw_norm_diff_omega_mean ) )
        logger.info( 'raw_norm_diff_omega_std = {:}'.format( raw_norm_diff_omega_std ) )
        logger.info( 'raw_norm_diff_omega_max = {:}'.format( raw_norm_diff_omega_max ) )
        logger.info( 'raw_norm_diff_omega_min = {:}'.format( raw_norm_diff_omega_min ) )

        p995_norm_diff_omega = np.nanpercentile(norm_diff_omega, 99.5)
        p990_norm_diff_omega = np.nanpercentile(norm_diff_omega, 99.0)
        p985_norm_diff_omega = np.nanpercentile(norm_diff_omega, 98.5)
        p980_norm_diff_omega = np.nanpercentile(norm_diff_omega, 98.0)
        p975_norm_diff_omega = np.nanpercentile(norm_diff_omega, 97.5)
        p970_norm_diff_omega = np.nanpercentile(norm_diff_omega, 97.0)
        p965_norm_diff_omega = np.nanpercentile(norm_diff_omega, 96.5)
        p960_norm_diff_omega = np.nanpercentile(norm_diff_omega, 96.0)
        p955_norm_diff_omega = np.nanpercentile(norm_diff_omega, 95.5)
        p950_norm_diff_omega = np.nanpercentile(norm_diff_omega, 95.0)
        p050_norm_diff_omega = np.nanpercentile(norm_diff_omega, 5.0)
        p045_norm_diff_omega = np.nanpercentile(norm_diff_omega, 4.5)
        p040_norm_diff_omega = np.nanpercentile(norm_diff_omega, 4.0)
        p035_norm_diff_omega = np.nanpercentile(norm_diff_omega, 3.5)
        p030_norm_diff_omega = np.nanpercentile(norm_diff_omega, 3.0)
        p025_norm_diff_omega = np.nanpercentile(norm_diff_omega, 2.5)
        p020_norm_diff_omega = np.nanpercentile(norm_diff_omega, 2.0)
        p015_norm_diff_omega = np.nanpercentile(norm_diff_omega, 1.5)
        p010_norm_diff_omega = np.nanpercentile(norm_diff_omega, 1.0)
        p005_norm_diff_omega = np.nanpercentile(norm_diff_omega, 0.5)

        logger.info( 'raw norm_diff_omega 99.5 percentile = {:}'.format( p995_norm_diff_omega ) )
        logger.info( 'raw norm_diff_omega 99.0 percentile = {:}'.format( p990_norm_diff_omega ) )
        logger.info( 'raw norm_diff_omega 98.5 percentile = {:}'.format( p985_norm_diff_omega ) )
        logger.info( 'raw norm_diff_omega 98.0 percentile = {:}'.format( p980_norm_diff_omega ) )
        logger.info( 'raw norm_diff_omega 97.5 percentile = {:}'.format( p975_norm_diff_omega ) )
        logger.info( 'raw norm_diff_omega 97.0 percentile = {:}'.format( p970_norm_diff_omega ) )
        logger.info( 'raw norm_diff_omega 96.5 percentile = {:}'.format( p965_norm_diff_omega ) )
        logger.info( 'raw norm_diff_omega 96.0 percentile = {:}'.format( p960_norm_diff_omega ) )
        logger.info( 'raw norm_diff_omega 95.5 percentile = {:}'.format( p955_norm_diff_omega ) )
        logger.info( 'raw norm_diff_omega 95.0 percentile = {:}'.format( p950_norm_diff_omega ) )
        logger.info( 'raw norm_diff_omega 5.0 percentile = {:}'.format( p050_norm_diff_omega ) )
        logger.info( 'raw norm_diff_omega 4.5 percentile = {:}'.format( p045_norm_diff_omega ) )
        logger.info( 'raw norm_diff_omega 4.0 percentile = {:}'.format( p040_norm_diff_omega ) )
        logger.info( 'raw norm_diff_omega 3.5 percentile = {:}'.format( p035_norm_diff_omega ) )
        logger.info( 'raw norm_diff_omega 3.0 percentile = {:}'.format( p030_norm_diff_omega ) )
        logger.info( 'raw norm_diff_omega 2.5 percentile = {:}'.format( p025_norm_diff_omega ) )
        logger.info( 'raw norm_diff_omega 2.0 percentile = {:}'.format( p020_norm_diff_omega ) )
        logger.info( 'raw norm_diff_omega 1.5 percentile = {:}'.format( p015_norm_diff_omega ) )
        logger.info( 'raw norm_diff_omega 1.0 percentile = {:}'.format( p010_norm_diff_omega ) )
        logger.info( 'raw norm_diff_omega 0.5 percentile = {:}'.format( p005_norm_diff_omega ) )

        #########################################################################################
        ####################
        #raw sig_adj_frac
        sig_adj_frac = norm_diff_omega.copy()

        #get moving box average
        mbox_sig_adj_frac = sig_adj_frac.copy()
        for center_row in range(0,nrow):
            for center_col in range(0,ncol):
                center_index = int(center_row*ncol + center_col)
                sur_ind_all = coars_map[center_index,:] #13*13, has nan
                #remove nan elements
                sur_ind_all = sur_ind_all[~np.isnan(sur_ind_all)].astype(int)
                mbox_sig_adj_frac[center_index] = np.nanmean(sig_adj_frac[sur_ind_all])
    
        sig_adj_frac = mbox_sig_adj_frac.copy()

        #get statistics of the raw sig_adj_frac
        raw_sig_adj_frac_mean = np.nanmean(sig_adj_frac)
        raw_sig_adj_frac_std = np.nanstd(sig_adj_frac)
        raw_sig_adj_frac_max = np.nanmax(sig_adj_frac)
        raw_sig_adj_frac_min = np.nanmin(sig_adj_frac)
        logger.info( 'raw_sig_adj_frac_mean = {:}'.format( raw_sig_adj_frac_mean ) )
        logger.info( 'raw_sig_adj_frac_std = {:}'.format( raw_sig_adj_frac_std ) )
        logger.info( 'raw_sig_adj_frac_max = {:}'.format( raw_sig_adj_frac_max ) )
        logger.info( 'raw_sig_adj_frac_min = {:}'.format( raw_sig_adj_frac_min ) )

        p995_sig_adj_frac = np.nanpercentile(sig_adj_frac, 99.5)
        p990_sig_adj_frac = np.nanpercentile(sig_adj_frac, 99.0)
        p985_sig_adj_frac = np.nanpercentile(sig_adj_frac, 98.5)
        p980_sig_adj_frac = np.nanpercentile(sig_adj_frac, 98.0)
        p975_sig_adj_frac = np.nanpercentile(sig_adj_frac, 97.5)
        p970_sig_adj_frac = np.nanpercentile(sig_adj_frac, 97.0)
        p965_sig_adj_frac = np.nanpercentile(sig_adj_frac, 96.5)
        p960_sig_adj_frac = np.nanpercentile(sig_adj_frac, 96.0)
        p955_sig_adj_frac = np.nanpercentile(sig_adj_frac, 95.5)
        p950_sig_adj_frac = np.nanpercentile(sig_adj_frac, 95.0)
        p050_sig_adj_frac = np.nanpercentile(sig_adj_frac, 5.0)
        p045_sig_adj_frac = np.nanpercentile(sig_adj_frac, 4.5)
        p040_sig_adj_frac = np.nanpercentile(sig_adj_frac, 4.0)
        p035_sig_adj_frac = np.nanpercentile(sig_adj_frac, 3.5)
        p030_sig_adj_frac = np.nanpercentile(sig_adj_frac, 3.0)
        p025_sig_adj_frac = np.nanpercentile(sig_adj_frac, 2.5)
        p020_sig_adj_frac = np.nanpercentile(sig_adj_frac, 2.0)
        p015_sig_adj_frac = np.nanpercentile(sig_adj_frac, 1.5)
        p010_sig_adj_frac = np.nanpercentile(sig_adj_frac, 1.0)
        p005_sig_adj_frac = np.nanpercentile(sig_adj_frac, 0.5)

        logger.info( 'raw sig_adj_frac 99.5 percentile = {:}'.format( p995_sig_adj_frac ) )
        logger.info( 'raw sig_adj_frac 99.0 percentile = {:}'.format( p990_sig_adj_frac ) )
        logger.info( 'raw sig_adj_frac 98.5 percentile = {:}'.format( p985_sig_adj_frac ) )
        logger.info( 'raw sig_adj_frac 98.0 percentile = {:}'.format( p980_sig_adj_frac ) )
        logger.info( 'raw sig_adj_frac 97.5 percentile = {:}'.format( p975_sig_adj_frac ) )
        logger.info( 'raw sig_adj_frac 97.0 percentile = {:}'.format( p970_sig_adj_frac ) )
        logger.info( 'raw sig_adj_frac 96.5 percentile = {:}'.format( p965_sig_adj_frac ) )
        logger.info( 'raw sig_adj_frac 96.0 percentile = {:}'.format( p960_sig_adj_frac ) )
        logger.info( 'raw sig_adj_frac 95.5 percentile = {:}'.format( p955_sig_adj_frac ) )
        logger.info( 'raw sig_adj_frac 95.0 percentile = {:}'.format( p950_sig_adj_frac ) )
        logger.info( 'raw sig_adj_frac 5.0 percentile = {:}'.format( p050_sig_adj_frac ) )
        logger.info( 'raw sig_adj_frac 4.5 percentile = {:}'.format( p045_sig_adj_frac ) )
        logger.info( 'raw sig_adj_frac 4.0 percentile = {:}'.format( p040_sig_adj_frac ) )
        logger.info( 'raw sig_adj_frac 3.5 percentile = {:}'.format( p035_sig_adj_frac ) )
        logger.info( 'raw sig_adj_frac 3.0 percentile = {:}'.format( p030_sig_adj_frac ) )
        logger.info( 'raw sig_adj_frac 2.5 percentile = {:}'.format( p025_sig_adj_frac ) )
        logger.info( 'raw sig_adj_frac 2.0 percentile = {:}'.format( p020_sig_adj_frac ) )
        logger.info( 'raw sig_adj_frac 1.5 percentile = {:}'.format( p015_sig_adj_frac ) )
        logger.info( 'raw sig_adj_frac 1.0 percentile = {:}'.format( p010_sig_adj_frac ) )
        logger.info( 'raw sig_adj_frac 0.5 percentile = {:}'.format( p005_sig_adj_frac ) )

        sig_adj_frac = np.clip(sig_adj_frac, -0.99,99)
    
        #########################################################################################
        scaling_factors = sig_adj_frac + 1.0 #nan #alpha_i
    
        #alpha_g* = alpha_g of previous iteration, alpha_g* U alpha_i = alpha_k*
        scaling_factors[unknown_index] = scaling_factors_IDW[unknown_index]

        #plot adjustment factors before IDW, plot alpha_k*
        scaling_factors_matrix = np.zeros([nrow, ncol])
        for i in range(0,len(scaling_factors)):
            row_sf = int(index_row_col_map[i,0]) #row
            col_sf = int(index_row_col_map[i,1]) #col
            scaling_factors_matrix[row_sf, col_sf] = scaling_factors[i] #alpha_k*
        iteration_number = MB_no + 1
        before_IDW = True
        cmaq_handle.plot_scal_factors(scaling_factors_matrix, iteration_number, before_IDW) #plot alpha_k*
    
        #update known array value
        count_known = 0
        for known_ind in range(0,len(scaling_factors)):
            factor_known[count_known] = scaling_factors[known_ind] #alpha_k*
            count_known += 1  
        #print("factor_known", factor_known)

        #Apply spatial interpolation (IDW)
        for unknown_count in range(0,number_unknown):
            unk_row = int(factor_unknown[unknown_count,0])
            unk_col = int(factor_unknown[unknown_count,1])
            #prepare surrounding grid cells factor_known_sur
            sur_num = 0
            factor_known_sur = np.zeros([sur_grid_num])
            #first determine the surrounding grid cells' row col based on unk_row, unk_col
            for sur_row in range((unk_row-((sur_grid_edge-1)/2.0)), (unk_row+((sur_grid_edge-1)/2.0)+1)):
                for sur_col in range((unk_col-((sur_grid_edge-1)/2.0)), (unk_col+((sur_grid_edge-1)/2.0)+1)):
                    if sur_row >=0 and sur_row < nrow and sur_col >=0 and sur_col < ncol:
                        #second, calculate the surrounding grid cells' indexes in the vector space
                        sur_ind = sur_row*ncol + sur_col
                        #Third, use the surrounding grid cells' indexes to get a subset of factor_known
                        factor_known_sur[sur_num] = factor_known[sur_ind]
                    else:
                        factor_known_sur[sur_num] = np.nan
                    sur_num += 1
            scaling_factors[int(unk_row*ncol + unk_col)] = cmaq_handle.CalcIDWvalue(distance_array[unknown_count,:], factor_known_sur) #alpha_g U alpha_i = alpha_k
        #print("scaling_factors after IDW", scaling_factors)
        logger.info( 'CalcIDWvalue finished' )
        #save alpha_g of current iteration for use as alpha_g* of next iteration
        scaling_factors_IDW = scaling_factors.copy()

        #plot adjustment factors after IDW, plot alpha_k
        scaling_factors_matrix = np.zeros([nrow, ncol])
        for i in range(0,len(scaling_factors)):
            row_sf = int(index_row_col_map[i,0]) #row
            col_sf = int(index_row_col_map[i,1]) #col
            scaling_factors_matrix[row_sf, col_sf] = scaling_factors[i]
        before_IDW = False
        cmaq_handle.plot_scal_factors(scaling_factors_matrix, iteration_number, before_IDW) #plot alpha_k

        #########################################################################################
        #Perform mb scaling
        #scaling_factors are just for one layer, need to make it em.lays to scale the 4D emissions sigma
        fDemis_lay = cmaq_config.fDemis_lay
        scal_fct_em_lay = np.zeros([fDemis_lay*nrow*ncol])
        for ll in range(0,fDemis_lay):
            scal_fct_em_lay[(ll*nrow*ncol):((ll+1)*nrow*ncol)] = scaling_factors
        unk_sigma_t_vector = unk_sigma_a.get_vector() * scal_fct_em_lay
        #limit unk_sigma_t_vector to be 0.1 to 10
        unk_sigma_t_vector = np.clip(unk_sigma_t_vector, 0.1, 10.0)
        unk_sigma_t = d.UnknownData(unk_sigma_t_vector) #mb_emis_scal
        #########################################################################################
        #output sigma at this iteration includes plot emission factors
        user_driver.callback_func(unk_sigma_t.get_vector())
        #########################################################################################
        MB_no = MB_no + 1
        logger.info( 'MB_no = {:}'.format( MB_no ) ) #changes in each iteration 
        #########################################################################################
        NMD = (np.nansum(np.abs(unk_sigma_t.get_vector() - unk_sigma_a.get_vector())))/(np.nansum(unk_sigma_a.get_vector()))
        logger.info( 'NMD = {:}'.format( NMD ) ) #changes in each iteration
        ##########################################################################################   
        #Accumulated scaling from mb prior 
        accum_scal = (np.nanmean(unk_sigma_t.get_vector()))/(np.nanmean(unk_sigma_init.get_vector()))
        logger.info( 'accum_scal = {:}'.format( accum_scal ) ) #changes in each iteration
        ##########################################################################################   
        #cost function value after the mb scaling
        un_vector = unk_sigma_t.get_vector() #changes in each iteration
        bg_cost = 0.5 * gama * np.sum( ( un_vector - bg_vector )**2 ) #changes in each iteration
        logger.info( 'bg_cost = {:}'.format( bg_cost ) ) #changes in each iteration

        phy_sigma_t = transform( unk_sigma_t, d.PhysicalData ) #uncondition, proportional emission factors
        model_in_t = transform( phy_sigma_t, d.ModelInputData ) #prepare_mode: proportional emission factors * template_emis(mol/s), which is initial guess of emission (halved of true emission before calling make_template.py), so current factor*50% true emission
        model_out_t = transform_mb( model_in_t, d.ModelOutputData ) #run model
        simulated_avg = transform( model_out_t, d.ObservationData_avg ) #obs_operator_avg, changes in each iteration
        residual = d.ObservationData_avg.get_residual( observed_avg, simulated_avg ) #changes in each iteration
        w_residual = d.ObservationData_avg.error_weight( residual ) #devide by average unc, changes in each iteration
        res_vector = residual.get_vector() #changes in each iteration
        wres_vector = w_residual.get_vector() #changes in each iteration
        ob_cost = 0.5 * np.sum( res_vector * wres_vector ) #changes in each iteration
        logger.info( 'ob_cost = {:}'.format( ob_cost ) ) #changes in each iteration

        cost = bg_cost + ob_cost #changes in each iteration
        logger.info( 'cost = {:}'.format( cost ) ) #changes in each iteration

        #########################################################################################
        end_time = time.time()
        logger.info( 'iteration completed in {:}s'.format(int(end_time-start_time) ) )   

    #if MB iterations end because of ob_cost function value going up and not 1st iteration:
    if ob_cost > ob_cost_previous and MB_no > 1.0:
        #return phy_sigma_t for previous iteration as MB result
        unk_sigma_t_pre = unk_sigma_a
        phy_sigma_t_pre = transform( unk_sigma_t_pre, d.PhysicalData )
        phy_sigma_mb_result = phy_sigma_t_pre
    else:
        phy_sigma_mb_result = phy_sigma_t
            
    logger.info( 'sigma_t conditioned norm = {:}'.format( np.linalg.norm(unk_sigma_t.get_vector())))    
    return phy_sigma_mb_result
