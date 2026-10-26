"""
IMB2 supporting code -- reference copy, not an importable module.

Excerpts of the IMB2-specific helpers that mb_scal() (imb2_mb_scal.py) calls
in other modules of the modified py4dvar framework, in the order mb_scal()
uses them. Each excerpt is preceded by its source file and line numbers. The
code is unchanged; one outdated comment in CalcIDWvalue_1st now gives the
13*13 moving-box size. Framework parts that IMB2 shares with 4D-Var (datadef
classes, obs_operator, condition/uncondition, prepare_model, callback_func)
and the CMAQ run-environment setup (setup_run_mb, cmaq_config) are not
reproduced here.

Derived from py4dvar (https://github.com/steven-thomas/py4dvar),
Copyright 2016 University of Melbourne, Apache License 2.0; modified.
"""


# -----------------------------------------------------------------------------
# fourdvar/user_driver.py, lines 170-181: observed CrIS total columns averaged within grid cells (Omega_o)
# -----------------------------------------------------------------------------

def get_observed_avg_tot_col():
    """
    application: get the observed average total column observations for the MB scaling
    input: None
    output: ObservationData_avg_tot_col
    """
    global observed_avg_tot_col
    
    if observed_avg_tot_col is None:
        observed_avg_tot_col = d.ObservationData_avg_tot_col.from_file( input_defn.obs_avg_tot_col_file )
        observed_avg_tot_col.assert_params()
    return observed_avg_tot_col


# -----------------------------------------------------------------------------
# fourdvar/user_driver.py, lines 95-105: IMB2 prior (initial emission scaling factors)
# -----------------------------------------------------------------------------

def get_background_mb():
    """
    application: get the background / prior estimate for the MB
    input: None
    output: PhysicalData (prior estimate)
    """
    global background_mb
    
    if background_mb is None:
        background_mb = d.PhysicalData.from_file( input_defn.prior_file_mb )
    return background_mb


# -----------------------------------------------------------------------------
# fourdvar/_transform.py, lines 5-6, 24-26, 43-56: transform_mb() sends the IMB2 forward run to run_model_mb
# -----------------------------------------------------------------------------

from fourdvar import transfunc as t
from fourdvar import datadef as d

transmap_mb = {
        ( d.ModelInputData, d.ModelOutputData ): t.run_model_mb
    }

def transform_mb( input_instance, output_class ):
    """
    framework: mapping of every transform to its input & output class
    input: instance of transform input, class of transform output
    output: result of mapped transformation (instance of output_class)
    
    eg:
    from datadef._transform import transform
    model_output = transform( model_input, datadef.ModelOutputData )
    """
    
    key = (input_instance.__class__, output_class)
    function = transmap_mb[ key ]
    return function( input_instance )


# -----------------------------------------------------------------------------
# fourdvar/transfunc/run_model_mb.py (whole file): CMAQ forward run for IMB2
# -----------------------------------------------------------------------------

"""
application: run the forward model, save result to ModelOutputData
like all transform in transfunc this is referenced from the transform function
eg: transform( model_input_instance, datadef.ModelOutputData ) == run_model_mb( model_input_instance )
"""

import numpy as np

from fourdvar.datadef import ModelInputData, ModelOutputData
import fourdvar.util.cmaq_handle as cmaq
import setup_logging

logger = setup_logging.get_logger( __file__ )

def run_model_mb( model_input ):
    """
    application: run the forward model, save result to ModelOutputData
    input: ModelInputData
    output: ModelOutputData
    """
    #run the forward model
    assert isinstance( model_input, ModelInputData )
    cmaq.wipeout()
    cmaq.run_fwd_mb()
    try:
        output = ModelOutputData()
    except AssertionError as assert_error:
        logger.error( 'cmaq_fwd_l_failed. logs exported.' )
        raise assert_error
        
    return ModelOutputData()


# -----------------------------------------------------------------------------
# fourdvar/util/cmaq_handle.py, lines 2-21: module imports used by the cmaq_handle excerpts below
# -----------------------------------------------------------------------------

import os
import glob
import subprocess
import fourdvar.util.date_handle as dt
import fourdvar.params.cmaq_config as cfg
import fourdvar.params.template_defn as template
import fourdvar.util.netcdf_handle as ncf
import fourdvar.util.file_handle as fh
from copy import deepcopy
import numpy as np
import scipy.integrate
import setup_logging as logging
logger = logging.get_logger( __file__ )
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import cm
import geopy.distance
from fourdvar.params.root_path_defn import plot_path


# -----------------------------------------------------------------------------
# fourdvar/util/cmaq_handle.py, lines 812-823: run_fwd_mb(), forward sweep with checkpoint files disabled
# -----------------------------------------------------------------------------

def run_fwd_mb(): #cl3293 #run fwd sweep for only forcing days with check point files disabled
    """
    extension: run cmaq fwd from current config
    input: None
    output: None
    """
    isfirst = True
    for cur_date in dt.get_datelist_bwd():
        run_fwd_single_mb(cur_date, isfirst)
        isfirst = False
        clear_local_logs()
    return None


# -----------------------------------------------------------------------------
# fourdvar/util/cmaq_handle.py, lines 583-642: run_fwd_single_mb(), one day of the IMB2 forward run
# -----------------------------------------------------------------------------

def run_fwd_single_mb( date, is_first ):
    """
    extension: run cmaq fwd for a single day
    input: dt.date, Boolean (is this day the first of the model)
    output: None
    """
    
    env_dict = setup_run_mb()

    env_dict['PERTCOLS'] = cfg.pertcols
    env_dict['PERTROWS'] = cfg.pertrows
    env_dict['PERTLEVS'] = cfg.pertlevs
    #env_dict['PERTSPCS'] = cfg.pertspcs #cl3293
    env_dict['PERTEMIS'] = cfg.pertemis  #cl3293
    env_dict['PERTDELT'] = cfg.pertdelt
    env_dict['CTM_APPL'] = cfg.fwd_appl
    env_dict['CTM_XFIRST_OUT'] = cfg.fwd_xfirst_file
    #env_dict['LOGFILE'] = cfg.fwd_logfile #cl3293
    env_dict['FLOOR_FILE'] = cfg.floor_file
    env_dict['CTM_PROGNAME'] = cfg.fwd_mb

    if is_first is True:
        env_dict['INIT_GASC_1'] = cfg.icon_file
        env_dict['INIT_AERO_1'] = cfg.icon_file
        env_dict['INIT_NONR_1'] = cfg.icon_file
        env_dict['INIT_TRAC_1'] = cfg.icon_file
        #env_dict['CTM_XFIRST_IN'] = '' #cause segfault
    else:
        prev_grid = dt.move_tag( cfg.last_grid_file, -1 )
        prev_xfirst = dt.move_tag( cfg.fwd_xfirst_file, -1 )
        env_dict['INIT_GASC_1'] = prev_grid
        env_dict['INIT_AERO_1'] = prev_grid
        env_dict['INIT_NONR_1'] = prev_grid
        env_dict['INIT_TRAC_1'] = prev_grid
        env_dict['CTM_XFIRST_IN'] = prev_xfirst
    
    env_dict = parse_env_dict( env_dict, date )
    load_env( env_dict )
    os.system('ulimit -s unlimited') #cl3293 unlimited stacksize
    run_cmd = cfg.cmd_preamble
    if int(cfg.npcol) != 1 or int(cfg.nprow) != 1:
        #use mpi
        run_cmd += '$MPI_RUN -np {:} '.format( int( cfg.npcol ) * int( cfg.nprow ) ) #cl3293 $MPI_RUN
    run_cmd += cfg.fwd_mb
    stdout_fname = dt.replace_date( cfg.fwd_stdout_log, date )
    fh.ensure_path( stdout_fname, inc_file=True )
    with open( stdout_fname, 'w' ) as stdout_file:
        msg = 'calling external process:\n{:}> {:}'.format( cfg.cmd_shell, run_cmd )
        logger.debug( msg )
        statcode = subprocess.call( run_cmd, stdout=stdout_file,
                                    stderr=subprocess.STDOUT,
                                    shell=True, executable=cfg.cmd_shell )
        logger.debug( 'external process finished.' )
    if statcode != 0:
        msg = 'cmaq fwd failed on {}.'.format( date.strftime('%Y%m%d') )
        logger.error( msg )
        raise AssertionError( msg )
    
    clean_env( env_dict )
    return None


# -----------------------------------------------------------------------------
# fourdvar/transfunc/retv_2_tot_col.py (whole file): CrIS-space NH3 profiles to total columns
# -----------------------------------------------------------------------------

"""
application: convert profile level retrievals (ppmV) to total columns (molec/cm2)
"""

import numpy as np
from fourdvar.datadef import ObservationData, ObservationData_tot_col
import fourdvar.util.netcdf_handle as ncf
from netCDF4 import Dataset
import fourdvar.params.date_defn as defn
import fourdvar.util.cmaq_handle as handle
                
for yyyymmdd in range(defn.start_date, defn.forc_end_date+1):
    mStamp = str(yyyymmdd)[4:6]
    dStamp = str(yyyymmdd)[-2:]

    for w1 in (140, 130, 120, 100, 80):
    
        if w1 ==130:
            w2 = 120
        else:
            w2 = w1 - 20
            
        if len(str(w1)) < 3:
            w1Stamp = '0' + str(w1)
        else:
            w1Stamp = str(w1)
        
        if len(str(w2)) < 3:
            w2Stamp = '0' + str(w2)
        else:
            w2Stamp = str(w2)

        for n1 in (45, 30, 15):
            if w1 == 140 and n1 == 45 or w1 == 130 and n1 == 30 or w1 == 120 or w1 == 100 or w1 == 80:
                n2 = n1 + 15
            else:
                continue
                
            if len(str(n1)) < 3:
                n1Stamp = '0' + str(n1)
            else:
                n1Stamp = str(n1)

            if len(str(n2)) < 3:
                n2Stamp = '0' + str(n2)
            else:
                n2Stamp = str(n2)

            #load CrIS data
            cris_data       = '/ifs/groups/cappsGrp/cris/data_v1.6.3/2017/'+mStamp+'/hpfx.collab.science.gc.ca/~mas001/satellite_ext/cris/snpp/nh3/v1_6_3/global/2017/'+mStamp+'/2017/'+mStamp+'/'+dStamp+'/Combined_NH3_n'+w1Stamp+'_0_n'+w2Stamp+'_0_p'+n1Stamp+'_0_p'+n2Stamp+'_0_2017'+mStamp+dStamp+'.nc'
            crisfile = Dataset(cris_data,'r',format = "NETCDF4")
            CrIS_press = np.asarray(crisfile.variables['pressure']) #mbar
            CrIS_alt = np.asarray(crisfile.variables['zm']) #km
            CrIS_temp = np.asarray(crisfile.variables['tm']) #K
            CrIS_h2o = np.asarray(crisfile.variables['h2o'])
            crisfile.close() 
            
            globals()["CrIS_press" + mStamp + dStamp + w1Stamp + n1Stamp] = CrIS_press
            globals()["CrIS_alt" + mStamp + dStamp + w1Stamp + n1Stamp] = CrIS_alt
            globals()["CrIS_temp" + mStamp + dStamp + w1Stamp + n1Stamp] = CrIS_temp
            globals()["CrIS_h2o" + mStamp + dStamp + w1Stamp + n1Stamp] = CrIS_h2o

def retv_2_tot_col( retv ):
    """
    application: convert profile level retrievals (ppmV) to total columns (molec/cm2)
    """
    ObservationData_tot_col.assert_params()
    
    val_list_tot_col = [ o for o in ObservationData_tot_col.place_holder ]
    #print("val_list_tot_col", val_list_tot_col)
    for ymd1, ilist1 in ObservationData_tot_col.ind_by_date.items():
        mStamp1 = ymd1[4:6]
        dStamp1 = ymd1[-2:]
        
        #loop over days in retv obs sequence file to find the block of ilist2 for the same day as current tot_col ilist1 block
        for ymd2, ilist2 in ObservationData.ind_by_date.items():
        
            if ymd2 == ymd1:
                
                i2_start = ilist2[0]
                for i1 in ilist1:
                    for coord1, cg1 in ObservationData_tot_col.coord_grid[i1].items():
                        if str( coord1[0] ) == ymd1:
                        #date, timestep, row, column, species, observation, w1, n1
                            step1,row1,col1,spc1,obs1,w11,n11 = coord1[1:]
                            
                            if len(str(w11)) < 3:
                                w11Stamp = '0' + str(w11)
                            else:
                                w11Stamp = str(w11)
                    
                            if len(str(n11)) < 3:
                                n11Stamp = '0' + str(n11)
                            else:
                                n11Stamp = str(n11)
                                
                            #load CrIS data
                            CrIS_press = globals()["CrIS_press" + mStamp1 + dStamp1 + w11Stamp + n11Stamp]
                            CrIS_alt = globals()["CrIS_alt" + mStamp1 + dStamp1 + w11Stamp + n11Stamp]
                            CrIS_temp = globals()["CrIS_temp" + mStamp1 + dStamp1 + w11Stamp + n11Stamp]
                            CrIS_h2o = globals()["CrIS_h2o" + mStamp1 + dStamp1 + w11Stamp + n11Stamp]
        
                            #define missing pressure layers
                            indexOfMissingPress = np.nonzero(CrIS_press[obs1] == -999.5)
        
                            #delete missing pressure layer for pressure
                            CrIS_press_new = np.delete(CrIS_press[obs1], indexOfMissingPress, 0) #15 to 14                                        
                            CrIS_alt_new = np.delete(CrIS_alt[obs1], indexOfMissingPress, 0) #15 to 14
                            CrIS_temp_new = np.delete(CrIS_temp[obs1], indexOfMissingPress, 0) #15 to 14
                            CrIS_h2o_new = np.delete(CrIS_h2o[obs1], indexOfMissingPress, 0) #15 to 14
                            
                            pres_min =       200.        # minimum pressure to use in profile (hPa)
                            np.seterr(invalid="ignore")
                            ilev_srf = 0
                            ilev_top = np.max(np.where(CrIS_press_new>pres_min)[0]) #needed
                            np.seterr(invalid="warn")
        
                            #only keep pressure layers within range
                            CrIS_press_new = CrIS_press_new[ilev_srf:ilev_top+1]
                            CrIS_alt_new = CrIS_alt_new[ilev_srf:ilev_top+1]
                            CrIS_temp_new = CrIS_temp_new[ilev_srf:ilev_top+1]
                            CrIS_h2o_new = CrIS_h2o_new[ilev_srf:ilev_top+1]
        
                            #print("len(CrIS_press_new)", len(CrIS_press_new))
                            retv_column = np.zeros([len(CrIS_press_new)])
                            
                            i2_end = i2_start + len(CrIS_press_new)
                            for i2 in range(i2_start, i2_end):
                                lay2 = i2 - i2_start
                                retv_column[lay2] = retv.value[i2]
                            i2_start = i2_end
                            #print("retv_column", retv_column) #retv_column has negative value, causing problem
                            tot_col_calc = handle.get_column_amt(retv_column, CrIS_h2o_new, CrIS_temp_new, CrIS_press_new, CrIS_alt_new) #dbg
                            #print("tot_col_calc", tot_col_calc)
                            val_list_tot_col[i1] = tot_col_calc

    return ObservationData_tot_col( val_list_tot_col )

    

# -----------------------------------------------------------------------------
# fourdvar/util/cmaq_handle.py, lines 1206-1293: get_column_amt(), column integration used by retv_2_tot_col
# -----------------------------------------------------------------------------

def get_column_amt(vmol, h2o_vmol, tm, pm, zm): #vmol negative
    #print("h2o_vmol", h2o_vmol)
    #print("tm", tm)
    #print("pm", pm)
    #print("zm", zm)
    orig_grid = pm
    #print("orig_grid", orig_grid)
    new_grid_dbl = pm
    #print("new_grid_dbl", new_grid_dbl)
    #----------------------------------------------------------------
    #Constants and units
    #-----------------------------------------------------------------
    k_boltz = 1.380662e-23  # Boltzmann constant [J/K] = [(kg m^2)/(K s^2)]
    n_i = 1458

    ufGrid, pm_uf = ultra_fine(orig_grid, pm, n_i=n_i, press_include=new_grid_dbl)
    ufGrid, zm_uf = ultra_fine(orig_grid, zm, n_i=n_i, press_include=new_grid_dbl)
    ufGrid, tm_uf = ultra_fine(orig_grid, tm, n_i=n_i, press_include=new_grid_dbl)
    ufGrid, h2o_vmol_uf = ultra_fine(orig_grid, h2o_vmol, n_i=n_i, press_include=new_grid_dbl)
    #print("h2o_vmol_uf", h2o_vmol_uf)
    vmol_uf = np.zeros(len(ufGrid), float)
    ufGrid, vmol_uf = ultra_fine(orig_grid, vmol, n_i=n_i, press_include=new_grid_dbl)
    #print("vmol_uf", vmol_uf) #negative
    pm_uf = ufGrid
    #print("pm_uf", pm_uf)
    w_grid = where_array(list(new_grid_dbl), list(ufGrid))  # (new_grid_dbl, ufGrid, compare_thres=1e-6)
    n_grid = len(w_grid)

    #-----------------------------------------------------------------
    # Unit conversions
    #-----------------------------------------------------------------
    vmol_uf_ppv = vmol_uf / 1e6  #convert from ppmv to ppv, negative
    h2o_vmol_uf_ppv = h2o_vmol_uf / 1e6  #convert from ppmv to ppv
    pm_uf_hPa = pm_uf * 100.0  #convert pressure units from 1mb = 1hPa = 100Pa = 100 [N/m^2] = 100 [(kg m/s^2)/m^2]
    #print("vmol_uf_ppv", vmol_uf_ppv)
    #print("h2o_vmol_uf_ppv", h2o_vmol_uf_ppv)
    #print("pm_uf_hPa", pm_uf_hPa)
    #-----------------------------------------------------------------
    # Delta's
    #-----------------------------------------------------------------

    IMMAX = len(pm_uf)
    delta_zm_uf = zm_uf[1:] - zm_uf[0:-1]
    #print("delta_zm_uf", delta_zm_uf)

    #*****************************************************************
    # Compute the Level Number Density   
    #*****************************************************************

    lev_density = np.zeros(IMMAX)
    lev_density_total_air = np.zeros(IMMAX)
    lev_density_dry_air = np.zeros(IMMAX)

    # --- Total Air Number Density ---
    #PV=NkT -> den_tot=P/kT -> total air density (ideal gas law)
    lev_density_total_air = pm_uf_hPa[:] / (k_boltz * tm_uf[:] * 1000000.0)  # units [molecs/cm^3]
    #print("lev_density_total_air", lev_density_total_air)
    # --- Number Density of Dry Air --- 
    #den_dry = den_tot - den_h2o # mr_h2o = den_h2o/den_dry -> den_h2o = mr_h2o*den_dry
    #den_dry=den_tot/(1+mr_h2o)
    lev_density_dry_air = lev_density_total_air / (1.0 + h2o_vmol_uf_ppv)  # units [molecs/cm^3]
    #print("lev_density_dry_air", lev_density_dry_air)
    lev_density[:] = vmol_uf_ppv[:] * lev_density_dry_air[:]  # units [molecs/cm^3]
    #print("lev_density", lev_density) #negative
    #*****************************************************************
    # Compute Column Number Density 
    # -> The column density is defined as the integral of lev_density*dz 
    #*****************************************************************

    col_den = calc_column_amt(lev_density, delta_zm_uf) #lev_density has negative value, causing problem

    w_grid = where_array(new_grid_dbl, pm_uf)  # , compare_thres=10d-6)
    n_grid = len(w_grid)
    zm_grid = zm_uf[w_grid]

    # For altitude inputs
    #  -> assuming zm_uf goes from the bottom to the TOA
    col_den_grid = np.zeros(n_grid - 1)

    for j in range(n_grid-1):
        w_zm_uf, = np.where((zm_uf >= zm_grid[j]) & (zm_uf < zm_grid[j + 1]))
        n_col = len(w_zm_uf)
        if n_col > 0:
            col_den_grid[j] = np.sum(col_den[w_zm_uf])

    tot_col_den_grid = np.sum(col_den_grid[:])  # [molecs/cm^2]

    return  tot_col_den_grid


# -----------------------------------------------------------------------------
# fourdvar/transfunc/avg_tot_col.py (whole file): average total columns within each grid cell
# -----------------------------------------------------------------------------

"""
application: calculate average for total columns
"""

import numpy as np
from fourdvar.datadef import ObservationData_tot_col, ObservationData_avg_tot_col
import fourdvar.util.netcdf_handle as ncf
from netCDF4 import Dataset
import fourdvar.params.date_defn as defn

def avg_tot_col( tot_col ):
    """
    application: calculate average for total columns
    """
    ObservationData_avg_tot_col.assert_params()
    
    val_list_avg_tot_col = [ o for o in ObservationData_avg_tot_col.place_holder ]
    for ymd, ilist in ObservationData_avg_tot_col.ind_by_date.items():
        #print("ilist avg_tot_col", ilist)
        for i in ilist:
            #print("i", i)
            sum_tot_col = 0
            count_obs = 0
            for coord, cg in ObservationData_avg_tot_col.coord_grid[i].items():
                step,row,col,spc,_ = coord[1:]
                for ymd2, ilist2 in ObservationData_tot_col.ind_by_date.items():
                    for i2 in ilist2:
                        for coord2, cg2 in ObservationData_tot_col.coord_grid[i2].items():
                            step2,row2,col2,spc2,_,_,_= coord2[1:]
                            if row == row2 and col == col2:
                                sum_tot_col += tot_col.value[i2]
                                count_obs += 1
            #print("sum_tot_col", sum_tot_col)  
            #print("count_obs", count_obs)  
            if count_obs != 0:
                avg_tot_col_val = sum_tot_col/count_obs
            else:
                avg_tot_col_val = 0
            
            val_list_avg_tot_col[i] = avg_tot_col_val

    return ObservationData_avg_tot_col( val_list_avg_tot_col )

# -----------------------------------------------------------------------------
# fourdvar/util/cmaq_handle.py, lines 1371-1395: plot_scal_factors(), diagnostic maps of alpha
# -----------------------------------------------------------------------------

#######################################################################################################################################################
#plot MB scaling factors (alpha) field
def plot_scal_factors(scaling_factors_matrix, iteration_number, before_IDW):
    if  before_IDW:
        before_IDW_str = 'before IDW'
    else:
        before_IDW_str = 'after IDW'

    font_size = 15
    plot_name = os.path.join(plot_path, 'alpha_'+str(iteration_number)+before_IDW_str+'.pdf')
    with PdfPages(plot_name) as pdf:
        fig = plt.figure( figsize=(15,10) )
        plt.title( 'MB scaling factors of iteration#'+str(iteration_number)+' '+before_IDW_str, fontsize=font_size )
        cmap=cm.seismic
        cov = plt.pcolormesh( scaling_factors_matrix, vmin=-8.0, vmax=10.0, cmap=cmap,
                              edgecolor='k', linestyle=':', linewidth=.1 )
        plt.tick_params(labelsize=font_size)
        cbar = plt.colorbar()
        cbar.set_label('alpha (unitless)', fontsize=font_size)
        cbar.set_ticks( np.linspace(-8.0,10.0,num = 19))
        cbar.ax.tick_params(labelsize=font_size)

        plt.show()
        pdf.savefig()   
        plt.close()


# -----------------------------------------------------------------------------
# fourdvar/util/cmaq_handle.py, lines 1295-1331: inverse-distance weighting for cells without a valid alpha
# -----------------------------------------------------------------------------

#######################################################################################################################################################
#Inverse Distance Weighting real distance version, 1st iteration
#both knowncoords_sur and factor_known_sur may have np.nan in the same locations outside of the domain
def CalcIDWvalue_1st(unkcoord, knowncoords_sur, factor_known_sur):
    distance_vector = np.zeros([len(factor_known_sur)]) #13*13
    sum_of_weights = 0
    weighted_values_sum = 0
    power = 1.0
    #find which index of factor_known_sur have a value (not np.nan)
    factor_known_val_log = np.isfinite(factor_known_sur) #true or false, true for value; false for np.nan&infinity
    factor_known_val_ind, = np.where(factor_known_val_log)
    
    for known_id in factor_known_val_ind:
        distance = geopy.distance.distance(unkcoord,knowncoords_sur[known_id]).km
        distance_vector[known_id] = distance
        #print("distance",distance) #include 0
        if distance != 0:
            weight = (distance**power)**(-1)
            #print("weight", weight)
            sum_of_weights += weight
            #print("sum_of_weights", sum_of_weights)
            weighted_values_sum += weight * factor_known_sur[known_id]
            #print("weighted_values_sum", weighted_values_sum)
        else:
            continue
    return weighted_values_sum / sum_of_weights, distance_vector
#######################################################################################################################################################
#Inverse Distance Weighting real distance version, other iterations
#distance_vector have zero and value, factor_known_sur have np.nan and value
def CalcIDWvalue(distance_vector, factor_known_sur):
    power = 1.0
    distance_vector[distance_vector==0] = np.nan #make 0 to nan
    weight = (distance_vector**power)**(-1) #nan
    sum_of_weights = np.nansum(weight) #treat nan as zero in sum
    weighted_values_sum = np.nansum(weight * factor_known_sur)

    return weighted_values_sum / sum_of_weights

