#   Makefile generated using program [bldmake]
#
#   Generation date [01/29/2020  11:13:34]
#   Configuration file [cfg.bwd_NH3.bld]
#   Using GIT repository
#

MODEL = ADJOINT_BWD

FC = /mnt/HA/opt/openmpi/intel/2015/1.8.1-mlnx-ofed/bin/mpifort
CC = /opt/mellanox/openshmem/2.2/bin/mpicc

#f_FLAGS    = -extend-source 132 -g -traceback -check all -check bounds -check uninit -ftrapuv -debug all -fpe-all=3 -O0 -override-limits -mp1 -fp-model precise -module /home/cl3293/CMAQ_adj_NH3/cmaq_adj/scripts/BLD_bwd_NH3/MOD_DIR  -I. -I /mnt/HA/groups/cappsGrp/lib/ioapi/Linux2_x86_64ifort -I /mnt/HA/opt/openmpi/intel/2015/1.8.1-mlnx-ofed/include -I. -I /mnt/HA/opt/ioapi/intel/2015/3.2/lib
f_FLAGS    = -extend-source 132 -traceback -O0 -override-limits -mp1 -fp-model precise -module /home/cl3293/CMAQ_adj_NH3/cmaq_adj/scripts/BLD_bwd_NH3/MOD_DIR  -I. -I /mnt/HA/groups/cappsGrp/lib/ioapi/Linux2_x86_64ifort -I /mnt/HA/opt/openmpi/intel/2015/1.8.1-mlnx-ofed/include -I. -I /mnt/HA/opt/ioapi/intel/2015/3.2/lib
F_FLAGS    = $(f_FLAGS)
f90_FLAGS  = -free -traceback -O0 -module /home/cl3293/CMAQ_adj_NH3/cmaq_adj/scripts/BLD_bwd_NH3/MOD_DIR  -I. -I /mnt/HA/groups/cappsGrp/lib/ioapi/Linux2_x86_64ifort -I /mnt/HA/opt/openmpi/intel/2015/1.8.1-mlnx-ofed/include -I. -I /mnt/HA/opt/ioapi/intel/2015/3.2/lib
F90_FLAGS  = $(f90_FLAGS)
C_FLAGS    = -O2 -DFLDMN -I /mnt/HA/opt/openmpi/intel/2015/1.8.1-mlnx-ofed/include

LINKER     = $(FC)
LINK_FLAGS = -static-intel -openmp

REPOROOT = /home/cl3293/CMAQ_adj_NH3/cmaq_adj/CCTM

CPP = $(FC)
CPP_FLAGS = \
  -Dparallel \
  -Dcluster \
  -DIncl \
  -DINTERPB=PINTERPB \
  -DM3ERR=PM3ERR \
  -DM3EXIT=PM3EXIT \
  -DM3WARN=PM3WARN \
  -DSHUT3=PSHUT3 \
  -DWRITE3=PWRITE3 \
  -DSUBST_MODULES=SE_MODULES \
  -DSUBST_BARRIER=SE_BARRIER \
  -DSUBST_GLOBAL_MAX=SE_GLOBAL_MAX \
  -DSUBST_GLOBAL_MIN=SE_GLOBAL_MIN \
  -DSUBST_GLOBAL_MIN_DATA=SE_GLOBAL_MIN_DATA \
  -DSUBST_GLOBAL_TO_LOCAL_COORD=SE_GLOBAL_TO_LOCAL_COORD \
  -DSUBST_GLOBAL_SUM=SE_GLOBAL_SUM \
  -DSUBST_GLOBAL_LOGICAL=SE_GLOBAL_LOGICAL \
  -DSUBST_LOOP_INDEX=SE_LOOP_INDEX \
  -DSUBST_SUBGRID_INDEX=SE_SUBGRID_INDEX \
  -DSUBST_HI_LO_BND_PE=SE_HI_LO_BND_PE \
  -DSUBST_SUM_CHK=SE_SUM_CHK \
  -DSUBST_INIT_ARRAY=SE_INIT_ARRAY \
  -DSUBST_COMM=SE_COMM \
  -DSUBST_MY_REGION=SE_MY_REGION \
  -DSUBST_SLICE=SE_SLICE \
  -DSUBST_GATHER=SE_GATHER \
  -DSUBST_DATA_COPY=SE_DATA_COPY \
  -DSUBST_IN_SYN=SE_IN_SYN

SE_SNL =  -L/mnt/HA/groups/cappsGrp/lib/se_snl -lse_snl
PARIO =  -L/mnt/HA/groups/cappsGrp/lib/pario -lpario
MPICH =  -L/mnt/HA/opt/openmpi/intel/2015/1.8.1-mlnx-ofed/lib -lmpi
IOAPI =  -L /mnt/HA/opt/ioapi/intel/2015/3.2/lib -lioapi #/mnt/HA/groups/cappsGrp/lib/ioapi/Linux2_x86_64ifort -lioapi
NETCDF =  -L/mnt/HA/groups/cappsGrp/lib/netcdf/lib -lnetcdf -lnetcdff

LIBRARIES = $(SE_SNL) $(PARIO) $(MPICH) $(IOAPI) $(NETCDF)

BASE_INC = /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/fixed
MECH_INC = /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/cb05cl_ae5_aq
PA_INC = /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/procan/pa_noop

INCLUDES =  \
  -DSUBST_PE_COMM=\"$(BASE_INC)/par/PE_COMM.EXT\" \
  -DSUBST_CONST=\"$(BASE_INC)/const/CONST.EXT\" \
  -DSUBST_FILES_ID=\"$(BASE_INC)/filenames/FILES_CTM.EXT\" \
  -DSUBST_EMPR_VD=\"$(BASE_INC)/emctrl/EMISPRM.vdif.EXT\" \
  -DSUBST_EMPR_CH=\"$(BASE_INC)/emctrl/EMISPRM.chem.EXT\" \
  -DSUBST_IOPARMS=\"/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT\" \
  -DSUBST_IOFDESC=\"/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT\" \
  -DSUBST_IODECL=\"/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT\" \
  -DSUBST_RXCMMN=\"$(MECH_INC)/RXCM.EXT\" \
  -DSUBST_RXDATA=\"$(MECH_INC)/RXDT.EXT\" \
  -DSUBST_GC_SPC=\"$(MECH_INC)/GC_SPC.EXT\" \
  -DSUBST_GC_EMIS=\"$(MECH_INC)/GC_EMIS.EXT\" \
  -DSUBST_GC_ICBC=\"$(MECH_INC)/GC_ICBC.EXT\" \
  -DSUBST_GC_DIFF=\"$(MECH_INC)/GC_DIFF.EXT\" \
  -DSUBST_GC_DDEP=\"$(MECH_INC)/GC_DDEP.EXT\" \
  -DSUBST_GC_DEPV=\"$(MECH_INC)/GC_DEPV.EXT\" \
  -DSUBST_GC_ADV=\"$(MECH_INC)/GC_ADV.EXT\" \
  -DSUBST_GC_CONC=\"$(MECH_INC)/GC_CONC.EXT\" \
  -DSUBST_GC_G2AE=\"$(MECH_INC)/GC_G2AE.EXT\" \
  -DSUBST_GC_G2AQ=\"$(MECH_INC)/GC_G2AQ.EXT\" \
  -DSUBST_GC_SCAV=\"$(MECH_INC)/GC_SCAV.EXT\" \
  -DSUBST_GC_WDEP=\"$(MECH_INC)/GC_WDEP.EXT\" \
  -DSUBST_AE_SPC=\"$(MECH_INC)/AE_SPC.EXT\" \
  -DSUBST_AE_EMIS=\"$(MECH_INC)/AE_EMIS.EXT\" \
  -DSUBST_AE_ICBC=\"$(MECH_INC)/AE_ICBC.EXT\" \
  -DSUBST_AE_DIFF=\"$(MECH_INC)/AE_DIFF.EXT\" \
  -DSUBST_AE_DDEP=\"$(MECH_INC)/AE_DDEP.EXT\" \
  -DSUBST_AE_DEPV=\"$(MECH_INC)/AE_DEPV.EXT\" \
  -DSUBST_AE_ADV=\"$(MECH_INC)/AE_ADV.EXT\" \
  -DSUBST_AE_CONC=\"$(MECH_INC)/AE_CONC.EXT\" \
  -DSUBST_AE_A2AQ=\"$(MECH_INC)/AE_A2AQ.EXT\" \
  -DSUBST_AE_SCAV=\"$(MECH_INC)/AE_SCAV.EXT\" \
  -DSUBST_AE_WDEP=\"$(MECH_INC)/AE_WDEP.EXT\" \
  -DSUBST_NR_SPC=\"$(MECH_INC)/NR_SPC.EXT\" \
  -DSUBST_NR_EMIS=\"$(MECH_INC)/NR_EMIS.EXT\" \
  -DSUBST_NR_ICBC=\"$(MECH_INC)/NR_ICBC.EXT\" \
  -DSUBST_NR_DIFF=\"$(MECH_INC)/NR_DIFF.EXT\" \
  -DSUBST_NR_DDEP=\"$(MECH_INC)/NR_DDEP.EXT\" \
  -DSUBST_NR_DEPV=\"$(MECH_INC)/NR_DEPV.EXT\" \
  -DSUBST_NR_ADV=\"$(MECH_INC)/NR_ADV.EXT\" \
  -DSUBST_NR_N2AE=\"$(MECH_INC)/NR_N2AE.EXT\" \
  -DSUBST_NR_CONC=\"$(MECH_INC)/NR_CONC.EXT\" \
  -DSUBST_NR_N2AQ=\"$(MECH_INC)/NR_N2AQ.EXT\" \
  -DSUBST_NR_SCAV=\"$(MECH_INC)/NR_SCAV.EXT\" \
  -DSUBST_NR_WDEP=\"$(MECH_INC)/NR_WDEP.EXT\" \
  -DSUBST_TR_SPC=\"/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT\" \
  -DSUBST_TR_EMIS=\"/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_EMIS.EXT\" \
  -DSUBST_TR_ICBC=\"/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_ICBC.EXT\" \
  -DSUBST_TR_DIFF=\"/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_DIFF.EXT\" \
  -DSUBST_TR_DDEP=\"/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_DDEP.EXT\" \
  -DSUBST_TR_DEPV=\"/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_DEPV.EXT\" \
  -DSUBST_TR_ADV=\"/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_ADV.EXT\" \
  -DSUBST_TR_T2AQ=\"/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_T2AQ.EXT\" \
  -DSUBST_TR_SCAV=\"/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SCAV.EXT\" \
  -DSUBST_TR_WDEP=\"/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_WDEP.EXT\" \
  -DSUBST_PACTL_ID=\"$(PA_INC)/PA_CTL.EXT\" \
  -DSUBST_PACMN_ID=\"$(PA_INC)/PA_CMN.EXT\" \
  -DSUBST_PADAT_ID=\"$(PA_INC)/PA_DAT.EXT\" \
  -DSUBST_MPICH=\"/mnt/HA/opt/openmpi/intel/2015/1.8.1-mlnx-ofed/include/mpif.h\"

GLOBAL_MODULES = \
  CGRID_SPCS.o \
  HGRD_DEFN.o \
  VGRD_DEFN.o \
  GRID_CONF.o \
  PMEM_DEFN.o \
  AERO_EMIS.o \
  EMIS_DEFN.o \
  CHK_FILES_DEFS.o \
  MET_DATA.o \
  PRECURSOR_DATA.o \
  precursor_data_b.o \
  AERO_DATA.o \
  aero_data_b.o \
  PAGRD_DEFN.o \
  ADJOINT_FILES.o \
  CHK_FILES_IMPL.o \
  CHK_FILES.o \
  NH3_OFFLINE_FILE.o

DRIVER = \
  adj_array_mod.o \
  PCGRID_DEFN.o \
  advstep.o \
  driver_bwd.o \
  hcontvel.o \
  hveloc.o \
  readconf.o \
  sciproc_bwd.o \
  syncstep.o

PAR = \
  distr_env.o \
  par_init.o \
  par_term.o

INIT = \
  define_receptor.o \
  diffmsg.o \
  flcheck.o \
  grdcheck.o \
  init_lgrid.o \
  setup_logdev.o

ADJCON = \
  adjadv_noop.o

COUPLE = \
  couple.o \
  couple_cadj.o \
  ppmv_msmr.o

HADV = \
  ADV_CADJ.o \
  hadv_bwd.o \
  hppm.o \
  advbc_map_adj.o \
  rdbcon_rj.o \
  rdbcon_adj.o \
  xadv_bwd.o \
  xadv_rj_fwd.o \
  yadv_bwd.o \
  yadv_rj_fwd.o \
  zfdbc.o

VADV = \
  vppm.o \
  zadvyppm_bwd.o

HDIFF = \
  deform.o \
  hcdiff3d.o \
  hdiff_bwd.o \
  rho_j.o

VDIFF = \
  aero_emis_b.o \
  DEPVVARS.o \
  DEPV_DEFN.o \
  emis_defn_b.o \
  VDIFF_MAP.o \
  cgrid_depv.o \
  chkgrid.o \
  conv_cgrid_bwd.o \
  eddyx.o \
  gas_depv_map.o \
  m3dry.o \
  matrix_bwd.o \
  opddep.o \
  opdepv_diag.o \
  opemis.o \
  opmet.o \
  rddepv.o \
  rdmet.o \
  tri_bwd.o \
  vdiffacm2_bwd.o \
  write3_distr.o

PHOT = \
  phot_noop.o

CHEM = \
  chem_bwd_noop.o

AERO = \
  aero_driver_b.o \
  aero_subs_b.o \
  aero_subs.o \
  calc_h2o_adj.o \
  coags_b.o \
  coags.o \
  compute_flux_adj.o \
  getcoags_adj.o \
  getpar_b.o \
  getpar.o \
  getsc_adj.o \
  hcond3_adj.o \
  hetchem_adj.o \
  hetchem_b.o \
  hetchem.o \
  intercoag_gh_adj.o \
  intracoag_gh_adj.o \
  isoropiaIIcode_adj.o \
  n2o5prob_adj.o \
  newpart3_adj.o \
  opdiam.o \
  opvis.o \
  volinorg_adj.o
  #SOA_DEFN.o \
  #soa_defn_b.o \

AERO_DEPV = \
  aero_depv.o

CLOUD = \
  aqchem_Precision.o \
  aqchem_Parameters.o \
  aqchem_HessianSP.o \
  aqchem_Hessian.o \
  aqchem_Global.o \
  aqchem_JacobianSP.o \
  aqchem_Jacobian.o \
  aqchem_LinearAlgebra.o \
  aqchem_Function.o \
  aqchem_Rates.o \
  aqchem_Integrator.o \
  aqchem_Integrator_ADJ.o \
  AQ_DATA.o \
  aqchem_Model.o \
  aqchem_initialize_b.o \
  acmcld_b.o \
  acmcld.o \
  aqchem_b.o \
  aqchem_kpp.o \
  aq_map_b.o \
  aq_map.o \
  cldproc_b.o \
  convcld_acm_b.o \
  convcld_acm.o \
  getalpha_b.o \
  getalpha.o \
  hlconst.o \
  indexn.o \
  rescld_b.o \
  rescld.o \
  scavwdep_b.o \
  scavwdep.o \
  set_aeconcmin.o

PROCAN = \
  pa_init.o \
  pa_irr_ctl.o \
  pa_irr.o \
  pa_mkhdr.o \
  pa_output.o \
  pa_update.o

UTIL = \
  adBuffer.o \
  adStack.o \
  cksummer.o \
  findex.o \
  get_envlist.o \
  lstepf.o \
  subhdomain.o \
  subhfile.o

OBJS = \
  $(GLOBAL_MODULES) \
  $(DRIVER) \
  $(PAR) \
  $(INIT) \
  $(ADJCON) \
  $(COUPLE) \
  $(HADV) \
  $(VADV) \
  $(HDIFF) \
  $(VDIFF) \
  $(PHOT) \
  $(CHEM) \
  $(AERO) \
  $(AERO_DEPV) \
  $(CLOUD) \
  $(PROCAN) \
  $(UTIL)

.SUFFIXES: .F .f .c .F90 .f90

$(MODEL): $(OBJS)
	$(LINKER) $(LINK_FLAGS) $(OBJS) $(LIBRARIES) -o $@

.F.o:
	$(FC) -c $(F_FLAGS) $(CPP_FLAGS) $(INCLUDES) $<

.f.o:
	$(FC) -c $(f_FLAGS) $<

.F90.o:
	$(FC) -c $(F90_FLAGS) $(CPP_FLAGS) $(INCLUDES) $<

.f90.o:
	$(FC) -c $(f90_FLAGS) $<

.c.o:
	$(CC) -c $(C_FLAGS) $<

clean:
	rm -f $(OBJS) *.mod


# dependencies
ADV_CADJ.o: GRID_CONF.F /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
            /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT 
couple_cadj.o: GRID_CONF.F CGRID_SPCS.F $(BASE_INC)/filenames/FILES_CTM.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT $(MECH_INC)/GC_SPC.EXT \
		$(MECH_INC)/AE_SPC.EXT $(MECH_INC)/NR_SPC.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT 
rdbcon_adj.o: GRID_CONF.F $(BASE_INC)/filenames/FILES_CTM.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT $(MECH_INC)/GC_SPC.EXT \
		$(MECH_INC)/AE_SPC.EXT $(MECH_INC)/NR_SPC.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT \
		$(MECH_INC)/GC_ADV.EXT $(MECH_INC)/AE_ADV.EXT $(MECH_INC)/NR_ADV.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_ADV.EXT \
		$(MECH_INC)/GC_ICBC.EXT $(MECH_INC)/AE_ICBC.EXT $(MECH_INC)/NR_ICBC.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_ICBC.EXT \
		$(BASE_INC)/const/CONST.EXT
advbc_map_adj.o: $(BASE_INC)/filenames/FILES_CTM.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT \
		$(MECH_INC)/GC_ADV.EXT $(MECH_INC)/AE_ADV.EXT $(MECH_INC)/NR_ADV.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_ADV.EXT \
		$(MECH_INC)/GC_ICBC.EXT $(MECH_INC)/AE_ICBC.EXT $(MECH_INC)/NR_ICBC.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_ICBC.EXT
NH3_OFFLINE_FILE.o: CGRID_SPCS.F GRID_CONF.F PRECURSOR_DATA.F AERO_DATA.F \
                $(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
                /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT \
                $(MECH_INC)/GC_SPC.EXT $(MECH_INC)/GC_EMIS.EXT $(MECH_INC)/AE_SPC.EXT \
                $(MECH_INC)/AE_EMIS.EXT $(MECH_INC)/NR_SPC.EXT $(MECH_INC)/NR_EMIS.EXT \
                /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_EMIS.EXT
ADJOINT_FILES.o:	GRID_CONF.F CHK_FILES_DEFS.F PMEM_DEFN.F EMIS_DEFN.F \
		CGRID_SPCS.F $(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT \
		$(MECH_INC)/GC_SPC.EXT $(MECH_INC)/GC_EMIS.EXT $(MECH_INC)/AE_SPC.EXT \
		$(MECH_INC)/AE_EMIS.EXT $(MECH_INC)/NR_SPC.EXT $(MECH_INC)/NR_EMIS.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_EMIS.EXT
advstep.o:	GRID_CONF.F $(BASE_INC)/const/CONST.EXT $(BASE_INC)/filenames/FILES_CTM.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
CGRID_SPCS.o:	$(MECH_INC)/GC_SPC.EXT $(MECH_INC)/AE_SPC.EXT $(MECH_INC)/NR_SPC.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT
driver_bwd.o:	PCGRID_DEFN.F VGRD_DEFN.F ADJOINT_FILES.F CHK_FILES_DEFS.F \
		CHK_FILES.F adj_array_mod.f $(BASE_INC)/filenames/FILES_CTM.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT \
		$(MECH_INC)/RXCM.EXT $(MECH_INC)/RXDT.EXT
GRID_CONF.o:	HGRD_DEFN.F VGRD_DEFN.F
hcontvel.o:	GRID_CONF.F $(BASE_INC)/par/PE_COMM.EXT $(BASE_INC)/filenames/FILES_CTM.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
HGRD_DEFN.o:	/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
hveloc.o:	GRID_CONF.F $(BASE_INC)/par/PE_COMM.EXT $(BASE_INC)/const/CONST.EXT \
		$(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
PCGRID_DEFN.o:	GRID_CONF.F CGRID_SPCS.F EMIS_DEFN.F PMEM_DEFN.F \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT $(MECH_INC)/GC_EMIS.EXT \
		$(MECH_INC)/AE_EMIS.EXT $(MECH_INC)/NR_EMIS.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_EMIS.EXT
sciproc_bwd.o:	ADJOINT_FILES.F adj_array_mod.f /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
syncstep.o:	GRID_CONF.F $(BASE_INC)/const/CONST.EXT $(BASE_INC)/filenames/FILES_CTM.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
VGRD_DEFN.o:	/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
par_init.o:	GRID_CONF.F PAGRD_DEFN.F /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT \
		$(PA_INC)/PA_CTL.EXT /mnt/HA/opt/openmpi/intel/2015/1.8.1-mlnx-ofed/include #lib
par_term.o:	/mnt/HA/opt/openmpi/intel/2015/1.8.1-mlnx-ofed/include #lib
define_receptor.o:	GRID_CONF.F CGRID_SPCS.F /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		$(MECH_INC)/GC_SPC.EXT $(MECH_INC)/AE_SPC.EXT $(MECH_INC)/NR_SPC.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT
diffmsg.o:	/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
flcheck.o:	$(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
grdcheck.o:	GRID_CONF.F $(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
init_lgrid.o:	ADJOINT_FILES.F $(BASE_INC)/filenames/FILES_CTM.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
setup_logdev.o:	/mnt/HA/opt/openmpi/intel/2015/1.8.1-mlnx-ofed/lib
adjadv_noop.o:	/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
couple.o:	GRID_CONF.F CGRID_SPCS.F $(BASE_INC)/filenames/FILES_CTM.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT $(MECH_INC)/GC_SPC.EXT \
		$(MECH_INC)/AE_SPC.EXT $(MECH_INC)/NR_SPC.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT
ppmv_msmr.o:	GRID_CONF.F $(BASE_INC)/const/CONST.EXT $(BASE_INC)/filenames/FILES_CTM.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
hadv_bwd.o:	GRID_CONF.F CHK_FILES_DEFS.F CHK_FILES.F CGRID_SPCS.F ADV_CADJ.F $(BASE_INC)/par/PE_COMM.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT $(MECH_INC)/GC_ADV.EXT \
		$(MECH_INC)/AE_ADV.EXT $(MECH_INC)/NR_ADV.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_ADV.EXT \
		$(MECH_INC)/GC_SPC.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT $(BASE_INC)/filenames/FILES_CTM.EXT 
hppm.o:	HGRD_DEFN.F
rdbcon_rj.o:	GRID_CONF.F $(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
xadv_bwd.o:	GRID_CONF.F CGRID_SPCS.F /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		$(MECH_INC)/GC_SPC.EXT $(MECH_INC)/GC_ADV.EXT $(MECH_INC)/AE_ADV.EXT \
		$(MECH_INC)/NR_ADV.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_ADV.EXT
xadv_rj_fwd.o:	HGRD_DEFN.F
yadv_bwd.o:	GRID_CONF.F CGRID_SPCS.F /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		$(MECH_INC)/GC_SPC.EXT $(MECH_INC)/GC_ADV.EXT $(MECH_INC)/AE_ADV.EXT \
		$(MECH_INC)/NR_ADV.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_ADV.EXT
yadv_rj_fwd.o:	HGRD_DEFN.F
vppm.o:	/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT
zadvyppm_bwd.o:	GRID_CONF.F CGRID_SPCS.F ADV_CADJ.F \
		$(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT $(MECH_INC)/GC_SPC.EXT \
		$(MECH_INC)/GC_ADV.EXT $(MECH_INC)/AE_SPC.EXT $(MECH_INC)/AE_ADV.EXT \
		$(MECH_INC)/NR_SPC.EXT $(MECH_INC)/NR_ADV.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_ADV.EXT
deform.o:	GRID_CONF.F $(BASE_INC)/par/PE_COMM.EXT $(BASE_INC)/const/CONST.EXT \
		$(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
hcdiff3d.o:	GRID_CONF.F $(BASE_INC)/par/PE_COMM.EXT $(BASE_INC)/const/CONST.EXT \
		$(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
hdiff_bwd.o:	GRID_CONF.F CGRID_SPCS.F $(BASE_INC)/const/CONST.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT \
		$(MECH_INC)/GC_DIFF.EXT $(MECH_INC)/AE_DIFF.EXT $(MECH_INC)/NR_DIFF.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_DIFF.EXT
rho_j.o:	GRID_CONF.F $(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
aero_emis_b.o:	AERO_EMIS.F PMEM_DEFN.F $(BASE_INC)/const/CONST.EXT \
		$(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT $(MECH_INC)/RXCM.EXT \
		$(MECH_INC)/GC_EMIS.EXT $(MECH_INC)/AE_SPC.EXT
AERO_EMIS.o:	GRID_CONF.F $(MECH_INC)/AE_EMIS.EXT
cgrid_depv.o:	HGRD_DEFN.F $(MECH_INC)/GC_SPC.EXT $(MECH_INC)/GC_DEPV.EXT \
		$(MECH_INC)/AE_SPC.EXT $(MECH_INC)/AE_DEPV.EXT $(MECH_INC)/NR_SPC.EXT \
		$(MECH_INC)/NR_DEPV.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_DEPV.EXT
chkgrid.o:	/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT
conv_cgrid_bwd.o:	GRID_CONF.F CGRID_SPCS.F $(BASE_INC)/const/CONST.EXT \
		$(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT $(MECH_INC)/GC_SPC.EXT \
		$(MECH_INC)/AE_SPC.EXT $(MECH_INC)/NR_SPC.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT
DEPV_DEFN.o:	HGRD_DEFN.F DEPVVARS.F GRID_CONF.F CGRID_SPCS.F $(BASE_INC)/const/CONST.EXT \
		$(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		$(MECH_INC)/RXCM.EXT $(MECH_INC)/GC_SPC.EXT $(MECH_INC)/GC_DEPV.EXT \
		$(MECH_INC)/AE_SPC.EXT $(MECH_INC)/AE_DEPV.EXT $(MECH_INC)/NR_SPC.EXT \
		$(MECH_INC)/NR_DEPV.EXT $(MECH_INC)/NR_N2AE.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_DEPV.EXT
DEPVVARS.o:	HGRD_DEFN.F /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT
eddyx.o:	GRID_CONF.F $(BASE_INC)/par/PE_COMM.EXT $(BASE_INC)/const/CONST.EXT \
		$(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
emis_defn_b.o:	EMIS_DEFN.F aero_emis_b.F PMEM_DEFN.F $(BASE_INC)/filenames/FILES_CTM.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT $(MECH_INC)/GC_EMIS.EXT \
		$(MECH_INC)/AE_SPC.EXT $(MECH_INC)/NR_EMIS.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_EMIS.EXT
EMIS_DEFN.o:	GRID_CONF.F PMEM_DEFN.F $(BASE_INC)/const/CONST.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT $(MECH_INC)/GC_EMIS.EXT \
		$(MECH_INC)/AE_SPC.EXT $(MECH_INC)/AE_EMIS.EXT $(MECH_INC)/NR_EMIS.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_EMIS.EXT
gas_depv_map.o:	DEPVVARS.F /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT $(MECH_INC)/GC_SPC.EXT \
		$(MECH_INC)/GC_DEPV.EXT $(MECH_INC)/NR_SPC.EXT $(MECH_INC)/NR_DEPV.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_DEPV.EXT
m3dry.o:	HGRD_DEFN.F DEPVVARS.F $(BASE_INC)/const/CONST.EXT $(BASE_INC)/filenames/FILES_CTM.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
matrix_bwd.o:	VGRD_DEFN.F $(MECH_INC)/GC_DIFF.EXT $(MECH_INC)/AE_DIFF.EXT \
		$(MECH_INC)/NR_DIFF.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_DIFF.EXT
opddep.o:	GRID_CONF.F $(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT \
		$(MECH_INC)/GC_DDEP.EXT $(MECH_INC)/AE_DDEP.EXT $(MECH_INC)/NR_DDEP.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_DDEP.EXT
opdepv_diag.o:	HGRD_DEFN.F DEPVVARS.F $(BASE_INC)/filenames/FILES_CTM.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
opemis.o:	VGRD_DEFN.F $(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT \
		$(MECH_INC)/GC_EMIS.EXT $(MECH_INC)/NR_EMIS.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_EMIS.EXT
opmet.o:	$(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
PMEM_DEFN.o:	HGRD_DEFN.F $(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT
rddepv.o:	HGRD_DEFN.F $(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT \
		$(MECH_INC)/RXCM.EXT $(MECH_INC)/GC_DEPV.EXT $(MECH_INC)/AE_DEPV.EXT \
		$(MECH_INC)/NR_DEPV.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_DEPV.EXT
rdmet.o:	GRID_CONF.F $(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
tri_bwd.o:	VGRD_DEFN.F $(MECH_INC)/GC_DIFF.EXT $(MECH_INC)/AE_DIFF.EXT \
		$(MECH_INC)/NR_DIFF.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_DIFF.EXT
vdiffacm2_bwd.o:	emis_defn_b.F DEPV_DEFN.F VDIFF_MAP.F CHK_FILES_DEFS.F \
		CHK_FILES.F $(BASE_INC)/const/CONST.EXT $(BASE_INC)/filenames/FILES_CTM.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
VDIFF_MAP.o:	CGRID_SPCS.F AERO_EMIS.F $(BASE_INC)/emctrl/EMISPRM.vdif.EXT \
		$(BASE_INC)/emctrl/EMISPRM.chem.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT $(MECH_INC)/GC_SPC.EXT \
		$(MECH_INC)/GC_EMIS.EXT $(MECH_INC)/GC_DIFF.EXT $(MECH_INC)/GC_DDEP.EXT \
		$(MECH_INC)/GC_DEPV.EXT $(MECH_INC)/AE_SPC.EXT $(MECH_INC)/AE_DIFF.EXT \
		$(MECH_INC)/AE_DDEP.EXT $(MECH_INC)/AE_DEPV.EXT $(MECH_INC)/NR_SPC.EXT \
		$(MECH_INC)/NR_EMIS.EXT $(MECH_INC)/NR_DIFF.EXT $(MECH_INC)/NR_DDEP.EXT \
		$(MECH_INC)/NR_DEPV.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_EMIS.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_DIFF.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_DDEP.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_DEPV.EXT
phot_noop.o:	HGRD_DEFN.F VGRD_DEFN.F /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT \
		$(MECH_INC)/RXCM.EXT
chem_bwd_noop.o:	/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
aero_data_b.o:	MET_DATA.F /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT
AERO_DATA.o:	CGRID_SPCS.F MET_DATA.F /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		$(MECH_INC)/AE_SPC.EXT
aero_driver_b.o:	soa_defn_b.F aero_data_b.F GRID_CONF.F precursor_data_b.F \
		MET_DATA.F CGRID_SPCS.F CHK_FILES_DEFS.F CHK_FILES.F $(BASE_INC)/filenames/FILES_CTM.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT \
		$(MECH_INC)/RXCM.EXT $(MECH_INC)/GC_SPC.EXT $(MECH_INC)/GC_EMIS.EXT \
		$(MECH_INC)/GC_G2AE.EXT $(MECH_INC)/AE_SPC.EXT $(MECH_INC)/NR_SPC.EXT \
		$(MECH_INC)/NR_N2AE.EXT $(PA_INC)/PA_CTL.EXT
aero_subs_b.o:	soa_defn_b.F aero_data_b.F MET_DATA.F precursor_data_b.F
aero_subs.o:	SOA_DEFN.F AERO_DATA.F MET_DATA.F PRECURSOR_DATA.F
compute_flux_adj.o:	aero_data_b.F MET_DATA.F precursor_data_b.F
getpar_b.o:	aero_data_b.F MET_DATA.F
getpar.o:	AERO_DATA.F MET_DATA.F
hetchem_adj.o:	aero_data_b.F precursor_data_b.F MET_DATA.F
hetchem_b.o:	aero_data_b.F precursor_data_b.F MET_DATA.F
hetchem.o:	AERO_DATA.F PRECURSOR_DATA.F MET_DATA.F
MET_DATA.o:	$(BASE_INC)/const/CONST.EXT
n2o5prob_adj.o:	aero_data_b.F MET_DATA.F
newpart3_adj.o:	aero_data_b.F MET_DATA.F
opdiam.o:	GRID_CONF.F $(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
opvis.o:	GRID_CONF.F $(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
precursor_data_b.o:	PRECURSOR_DATA.F MET_DATA.F /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT
PRECURSOR_DATA.o:	CGRID_SPCS.F MET_DATA.F /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		$(MECH_INC)/GC_SPC.EXT $(MECH_INC)/GC_G2AE.EXT $(MECH_INC)/NR_SPC.EXT \
		$(MECH_INC)/NR_N2AE.EXT
soa_defn_b.o:	SOA_DEFN.F aero_data_b.F MET_DATA.F CGRID_SPCS.F \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT $(MECH_INC)/GC_SPC.EXT \
		$(MECH_INC)/GC_G2AE.EXT $(MECH_INC)/AE_SPC.EXT $(MECH_INC)/NR_SPC.EXT \
		$(MECH_INC)/NR_N2AE.EXT
SOA_DEFN.o:	AERO_DATA.F MET_DATA.F CGRID_SPCS.F /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		$(MECH_INC)/GC_SPC.EXT $(MECH_INC)/GC_G2AE.EXT $(MECH_INC)/AE_SPC.EXT \
		$(MECH_INC)/NR_SPC.EXT $(MECH_INC)/NR_N2AE.EXT
volinorg_adj.o:	soa_defn_b.F MET_DATA.F aero_data_b.F precursor_data_b.F
aero_depv.o:	GRID_CONF.F CGRID_SPCS.F NH3_OFFLINE_FILE.F $(BASE_INC)/const/CONST.EXT \
		$(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT \
		$(MECH_INC)/RXCM.EXT $(MECH_INC)/AE_SPC.EXT $(MECH_INC)/AE_DEPV.EXT
aqchem_b.o:	AQ_DATA.F aqchem_Model.f90 aqchem_initialize_b.f
aqchem_Function.o:	aqchem_Parameters.f90
aqchem_Global.o:	aqchem_Parameters.f90
aqchem_Hessian.o:	aqchem_Parameters.f90 aqchem_HessianSP.f90
aqchem_initialize_b.o:	aqchem_Parameters.f90 aqchem_Global.f90 \
		AQ_DATA.F
aqchem_Integrator_ADJ.o:	aqchem_Precision.f90 aqchem_Parameters.f90 \
		aqchem_Global.f90 aqchem_LinearAlgebra.f90 aqchem_Rates.f90 \
		aqchem_Function.f90 aqchem_Jacobian.f90 aqchem_Hessian.f90
aqchem_Integrator.o:	aqchem_Parameters.f90 aqchem_Global.f90 aqchem_LinearAlgebra.f90 \
		aqchem_Function.f90 aqchem_Rates.f90 aqchem_Jacobian.f90
aqchem_Jacobian.o:	aqchem_Parameters.f90 aqchem_JacobianSP.f90
aqchem_kpp.o:	AQ_DATA.F aqchem_Model.f90 aqchem_initialize_b.f
aqchem_LinearAlgebra.o:	aqchem_Parameters.f90 aqchem_JacobianSP.f90
aqchem_Model.o:	aqchem_Precision.f90 aqchem_Parameters.f90 aqchem_Global.f90 \
		aqchem_Function.f90 aqchem_Integrator.F90 aqchem_Integrator_ADJ.F90 \
		aqchem_Rates.f90 aqchem_Jacobian.f90 aqchem_Hessian.f90 aqchem_LinearAlgebra.f90
aqchem_Parameters.o:	aqchem_Precision.f90
aqchem_Rates.o:	aqchem_Parameters.f90 aqchem_Global.f90
AQ_DATA.o:	AERO_DATA.F HGRD_DEFN.F CGRID_SPCS.F /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		$(MECH_INC)/GC_SPC.EXT $(MECH_INC)/GC_G2AQ.EXT $(MECH_INC)/AE_SPC.EXT \
		$(MECH_INC)/AE_A2AQ.EXT $(MECH_INC)/NR_SPC.EXT $(MECH_INC)/NR_N2AQ.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_T2AQ.EXT
aq_map_b.o:	aero_data_b.F CGRID_SPCS.F AQ_DATA.F /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		$(MECH_INC)/RXCM.EXT $(MECH_INC)/GC_SPC.EXT $(MECH_INC)/GC_G2AQ.EXT \
		$(MECH_INC)/AE_SPC.EXT $(MECH_INC)/AE_A2AQ.EXT $(MECH_INC)/NR_SPC.EXT \
		$(MECH_INC)/NR_N2AQ.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_T2AQ.EXT
aq_map.o:	CGRID_SPCS.F AQ_DATA.F AERO_DATA.F $(BASE_INC)/const/CONST.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT $(MECH_INC)/RXCM.EXT \
		$(MECH_INC)/GC_SPC.EXT $(MECH_INC)/GC_G2AQ.EXT $(MECH_INC)/AE_SPC.EXT \
		$(MECH_INC)/AE_A2AQ.EXT $(MECH_INC)/NR_SPC.EXT $(MECH_INC)/NR_N2AQ.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_T2AQ.EXT
cldproc_b.o:	GRID_CONF.F CGRID_SPCS.F CHK_FILES_DEFS.F CHK_FILES.F \
		$(BASE_INC)/const/CONST.EXT $(BASE_INC)/filenames/FILES_CTM.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT \
		$(MECH_INC)/GC_SPC.EXT $(MECH_INC)/GC_WDEP.EXT $(MECH_INC)/AE_SPC.EXT \
		$(MECH_INC)/AE_WDEP.EXT $(MECH_INC)/NR_SPC.EXT $(MECH_INC)/NR_WDEP.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_WDEP.EXT
convcld_acm_b.o:	GRID_CONF.F CGRID_SPCS.F $(BASE_INC)/const/CONST.EXT \
		$(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT \
		$(MECH_INC)/GC_SPC.EXT $(MECH_INC)/AE_SPC.EXT $(MECH_INC)/NR_SPC.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT
convcld_acm.o:	GRID_CONF.F CGRID_SPCS.F $(BASE_INC)/const/CONST.EXT \
		$(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT \
		$(MECH_INC)/GC_SPC.EXT $(MECH_INC)/AE_SPC.EXT $(MECH_INC)/NR_SPC.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT
getalpha_b.o:	AERO_DATA.F
getalpha.o:	AERO_DATA.F
hlconst.o:	/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
rescld_b.o:	GRID_CONF.F CGRID_SPCS.F $(BASE_INC)/const/CONST.EXT \
		$(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT \
		$(MECH_INC)/GC_SPC.EXT $(MECH_INC)/AE_SPC.EXT $(MECH_INC)/NR_SPC.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT
rescld.o:	GRID_CONF.F CGRID_SPCS.F $(BASE_INC)/const/CONST.EXT \
		$(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT \
		$(MECH_INC)/GC_SPC.EXT $(MECH_INC)/AE_SPC.EXT $(MECH_INC)/NR_SPC.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT
scavwdep_b.o:	CGRID_SPCS.F $(BASE_INC)/const/CONST.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		$(MECH_INC)/GC_SPC.EXT $(MECH_INC)/GC_SCAV.EXT $(MECH_INC)/AE_SPC.EXT \
		$(MECH_INC)/AE_SCAV.EXT $(MECH_INC)/NR_SPC.EXT $(MECH_INC)/NR_SCAV.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SCAV.EXT
scavwdep.o:	CGRID_SPCS.F $(BASE_INC)/const/CONST.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		$(MECH_INC)/GC_SPC.EXT $(MECH_INC)/GC_SCAV.EXT $(MECH_INC)/AE_SPC.EXT \
		$(MECH_INC)/AE_SCAV.EXT $(MECH_INC)/NR_SPC.EXT $(MECH_INC)/NR_SCAV.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SCAV.EXT
set_aeconcmin.o:	CGRID_SPCS.F $(BASE_INC)/const/CONST.EXT $(MECH_INC)/AE_SPC.EXT
PAGRD_DEFN.o:	GRID_CONF.F /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT \
		$(PA_INC)/PA_CTL.EXT $(PA_INC)/PA_CMN.EXT
pa_init.o:	GRID_CONF.F PAGRD_DEFN.F $(BASE_INC)/filenames/FILES_CTM.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT $(PA_INC)/PA_CTL.EXT \
		$(PA_INC)/PA_CMN.EXT $(PA_INC)/PA_DAT.EXT
pa_irr_ctl.o:	GRID_CONF.F PAGRD_DEFN.F $(MECH_INC)/GC_SPC.EXT \
		$(PA_INC)/PA_CMN.EXT
pa_irr.o:	GRID_CONF.F $(MECH_INC)/RXCM.EXT $(MECH_INC)/GC_SPC.EXT \
		$(PA_INC)/PA_CMN.EXT
pa_mkhdr.o:	GRID_CONF.F PAGRD_DEFN.F /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT $(MECH_INC)/GC_SPC.EXT \
		$(MECH_INC)/AE_SPC.EXT $(PA_INC)/PA_CMN.EXT
pa_output.o:	GRID_CONF.F PAGRD_DEFN.F $(BASE_INC)/filenames/FILES_CTM.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT \
		$(PA_INC)/PA_CTL.EXT $(PA_INC)/PA_CMN.EXT
pa_update.o:	PAGRD_DEFN.F AERO_EMIS.F $(BASE_INC)/const/CONST.EXT \
		$(BASE_INC)/filenames/FILES_CTM.EXT $(BASE_INC)/emctrl/EMISPRM.vdif.EXT \
		$(BASE_INC)/emctrl/EMISPRM.chem.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT \
		$(MECH_INC)/GC_SPC.EXT $(MECH_INC)/GC_EMIS.EXT $(MECH_INC)/GC_DDEP.EXT \
		$(MECH_INC)/GC_DEPV.EXT $(MECH_INC)/AE_SPC.EXT $(MECH_INC)/AE_DDEP.EXT \
		$(MECH_INC)/AE_DEPV.EXT $(MECH_INC)/NR_SPC.EXT $(MECH_INC)/NR_EMIS.EXT \
		$(MECH_INC)/NR_DDEP.EXT $(MECH_INC)/NR_DEPV.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_EMIS.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_DDEP.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_DEPV.EXT \
		$(PA_INC)/PA_CTL.EXT $(PA_INC)/PA_CMN.EXT
cksummer.o:	GRID_CONF.F CGRID_SPCS.F /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT $(MECH_INC)/GC_SPC.EXT \
		$(MECH_INC)/AE_SPC.EXT $(MECH_INC)/NR_SPC.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT
lstepf.o:	$(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
subhdomain.o:	/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
subhfile.o:	GRID_CONF.F $(BASE_INC)/filenames/FILES_CTM.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
CHK_FILES.o:	GRID_CONF.F CHK_FILES_DEFS.F CHK_FILES_IMPL.F $(BASE_INC)/filenames/FILES_CTM.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT $(MECH_INC)/RXCM.EXT \
		$(MECH_INC)/GC_SPC.EXT $(MECH_INC)/GC_EMIS.EXT $(MECH_INC)/GC_DIFF.EXT \
		$(MECH_INC)/GC_ADV.EXT $(MECH_INC)/GC_CONC.EXT $(MECH_INC)/AE_SPC.EXT \
		$(MECH_INC)/AE_EMIS.EXT $(MECH_INC)/AE_DIFF.EXT $(MECH_INC)/AE_ADV.EXT \
		$(MECH_INC)/AE_CONC.EXT $(MECH_INC)/NR_SPC.EXT $(MECH_INC)/NR_EMIS.EXT \
		$(MECH_INC)/NR_DIFF.EXT $(MECH_INC)/NR_ADV.EXT /home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_SPC.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_EMIS.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_DIFF.EXT \
		/home/cl3293/CMAQ_adj_NH3/cmaq_adj/ICL/mech/trac0/TR_ADV.EXT
CHK_FILES_IMPL.o:	CHK_FILES_DEFS.F HGRD_DEFN.F VGRD_DEFN.F /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/PARMS3.EXT \
		/mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/FDESC3.EXT /mnt/HA/groups/cappsGrp/lib/ioapi/fixed_src/IODECL3.EXT
