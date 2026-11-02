
!------------------------------------------------------------------------!
!  The Community Multiscale Air Quality (CMAQ) system software is in     !
!  continuous development by various groups and is based on information  !
!  from these groups: Federal Government employees, contractors working  !
!  within a United States Government contract, and non-Federal sources   !
!  including research institutions.  These groups give the Government    !
!  permission to use, prepare derivative works of, and distribute copies !
!  of their work in the CMAQ system to the public and to permit others   !
!  to do so.  The United States Environmental Protection Agency          !
!  therefore grants similar permission to use the CMAQ system software,  !
!  but users are requested to provide copies of derivative works or      !
!  products designed to operate in the CMAQ system to the United States  !
!  Government without restrictions as to use by others.  Software        !
!  that is used with the CMAQ system but distributed under the GNU       !
!  General Public License or the GNU Lesser General Public License is    !
!  subject to their copyright restrictions.                              !
!------------------------------------------------------------------------!


! RCS file, release, date & time of last delta, author, state, [and locker]
! $Header: /project/work/rep/arc/CCTM/src/cloud/cloud_acm_ae6/aqchem.F,v 1.6 2012/03/19 15:43:49 yoj Exp $

! what(1) key, module and SID; SCCS file; date and time of last delta:
! %W% %P% %G% %U%

!-----------------------------------------------------------------------
!  Description:
!    Compute concentration changes in cloud due to aqueous chemistry,
!    scavenging and wet deposition amounts.
!
!  Revision History:
!      No   Date   Who  What
!      -- -------- ---  -----------------------------------------
!      0  / /86    CW   BEGIN PROGRAM - Walceks's Original Code
!      1  / /86    RB   INCORPORATE INTO RADM
!      2  03/23/87 DH   REFORMAT
!      3  04/11/88 SJR  STREAMLINED CODE - ADDED COMMENTS
!      4  08/27/88 SJR  COMMENTS, MODIFIED FOR RPM
!      4a 03/15/96 FSB  Scanned hard copy to develop Models3
!                       Version.
!      5  04/24/96 FSB  Made into Models3 Format
!      6  02/18/97 SJR  Revisions to link with Models3
!      7  08/12/97 SJR  Revised for new concentration units (moles/mole)
!                       and new treatment of nitrate and nitric acid
!      8  01/15/98 sjr  revised to add new aitken mode scavenging
!                       and aerosol number scavenging
!      9  12/15/98 David Wong at LM:
!             -- change division of XL, TEMP to multiplication of XL, TEMP
!                reciprocal, respectively
!             -- change / TOTOX / TSIV to / ( TOTOX * TSIV )
!     10  03/18/99 David Wong at LM:
!             -- removed "* 1.0" redundant calculation at TEMP1 calculation
!     11  04/27/00 sjr  Added aerosol surface area as modeled species
!     12  12/02    sjr  changed calls to HLCONST and updated the dissociation
!                       constants
!     13  06/26/03 sjr  revised calculations of DTW based on CMAS website
!                       discussions
!     14  08/05/03 sjr  revision made to the coarse aerosol number washout
!     15  04/20/05  us  revisions to add sea salt species in the fine and
!                       coarse aerosol modes, and HCl dissolution/dissociation
!     16  10/13/05 sjr  fixed bug in the integration time step calculation
!                       (reported by Bonyoung Koo)
!     17  03/01/06 sjr  added elemental carbon aerosol; organic aerosols
!                       replaced with primary, secondary biogenic, and
!                       secondary anthropogenic; fixed 3rd moment calc to
!                       include EC and primary organics (not secondary);
!                       re-arranged logic for setting Cl & Na ending conc;
!                       added pointers/indirect addressing for arrays WETDEP
!                       and LIQUID
!     16  03/30/07 sjr  Limit integration timestep by cloud washout time
!     17  04/10/07 sjr  increased loop limits as follows: I20C <10000,
!                       I7777C <10000, I30C <10000, ICNTAQ <60000
!     18  01/10/07 agc  added organic chemistry for GLY and MGLY oxidation
!     19  09/10/07 sln  updated SOA species list for AE5
!     20  01/29/08 agc  updated DOHDT calculation
!     21  04/14/08 jtk  added coding for coarse NH4 and scavenging of
!                       coarse surface area
!     22  05/20/08 agc  for CB05, use the Henry's Law constant for glyoxal
!                       as a surrogate for methyl glyoxal
!     23  04/15/09 sjr& Several changes made to improve mass conservation in the
!                  agc  solver.  (1) OH concentration is now considered to be
!                       steady state; (2) only allow sulfur oxidation to affect
!                       time step; (3) implemented mass conservation checks -
!                       limit oxidation rates by the available mass for the
!                       specified timestep.
!   10 Oct 10 J.Young:  update to use aero_reeng by Steve Howard, Prakash Bhave,
!                       Jeff Young, Sergey Napelenok, and Shawn Roselle
!   01 Mar 11 S.Roselle: replaced I/O API include files with UTILIO_DEFN
!    9 Mar 11 S.Napelenok: update for AE6 - pH calculation now expanded to 
!                       include Ca Mg K SOIL CORS SEAS
!   23 May 11 G.Sarwar: update S(VI) production rate via H2O2, O3, MHP, PAA 
!                       pathways (Jacobson 1997)
!   23 May 11 G.Sarwar: update S(VI) production rate via O2 pathway (metal 
!                       catalysis) (Martin and Goodman, 1991)
!   01 Jul 11 G.Sarwar: Incorporate day and night dependent Fe III oxidation
!                       state (Alexander et al.,  2009)
!   12 Aug 11 G.Sarwar: Revise Fe and Mn solubility based on 
!                       Alexander et al., 2009
!    8 Mar 12 J.Bash:   FE_OX and MN_OX were calculated from FE and MN before
!                       a floor value of 0.0 was established for these 
!                       concentrations sometimes resulting in negative 
!                       concentrations and model crashes. The code used to 
!                       estimate FE_OX and MN_OX was moved to be after a floor 
!                       value for FE and MN was set. Also the washout rate was
!                       removed from the calculation of the estimate for doubling
!                       the time step based on sulfur oxidized < 5%.
!   28 Nov 12 G.Sarwar: Sulfate inhibition effect is implemented in the metal catalysis pathway
!   04 Mar 14 K. Fahey: Used the Kinetic PreProcessor to generate the RODAS3 solver
!                       for the CMAQ aqueous phase chemistry mechanism (Damian et al., 2002). 
!                       Aitken scavenging, mass transfer between the phases, dissociation, 
!                       chemical kinetics, and wet deposition are solved dynamically 
!                       and simultaneously.  The mass transfer between the phases is
!                       based on the resistance model of Schwartz (Schwartz, 1986).  The SIV-O3
!                       oxidation reaction has been corrected for potential aqueous 
!                       diffusion limitations.
!  07 Jul 14 B.Hutzell: replaced mechanism include file(s) with fortran module
!
!  References:
!     Walcek & Taylor, 1986, A theoretical Method for computing
!        vertical distributions of acidity and sulfate within cumulus
!        clouds, J. Atmos Sci.,  Vol. 43, no. 4 pp 339 - 355
!     Carlton, A.G., B.J. Turpin, K.E. Altieri, S.P. Seitzinger, R. Mathur,
!        S.J. Roselle, and R.J. Weber, CMAQ Model Performance Enhanced When
!        In-Cloud Secondary Organic Aerosol is Included:  Comparison of Organic
!        Carbon Predictions with Measurements, Environ. Sci. Technol., 42(23),
!        8798-8802, 2008.
!     Jacobson, M., Development and application of a new air pollution modeling 
!        system II. Aerosol module structure and design, Atmospheric 
!        Environment, 31, 131-144, 1997
!     Martin, R.L. and T.W. Good, catalyzed oxidation of sulfur dioxide in 
!        solution: the iron-manganese synergism, Atmospheric Environment, 25A, 
!        2395-2399, 1991
!     Alexander, B., R.J. Park, D.J. Jacob, S. Gong, Transition metal-catalyzed  
!        oxidation of atmospheric sulfur: global implications for the sulfur
!        budget, GRL, 114, D02309, 2009
!     Damian, V., A. Sandu, M. Damian, F. Potra, and G.R. Carmichael, The Kinetic 
!        PreProcessor KPP -- A Software Environment for Solving Chemical Kinetics,
!        Computers and Chemical Engineering, 26(11), 1567-1579, 2002.
!     Schwartz, S.E., Mass transport considerations pertinent to aqueous-phase
!        reactions of gases in liquid water clouds. In Chemistry of multiphase
!        atmospheric systems, NATO ASI Series, G6, 415-471, 1986. 
!
!
!  Called by:  AQMAP
!
!  Calls the following subroutines:  Initialize, Update_RCONST, INTEGRATE
!
!  Calls the following functions: 
!
!  Arguments     Type      I/O       Description
!  ---------     ----  ------------  --------------------------------
!  GAS(ngas)     real  input&output  Concentration for species i=1,15
!  GASWDEP(ngas) real     output     wet deposition for species
!
!  AEROSOL(naer,nmodes) real input&output   Concentration for species i=1,51
!  AERWDEP(naer,nmodes) real     output     wet deposition for species
!-----------------------------------------------------------------------

!:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE AQCHEM ( JDATE, JTIME, TEMP2, PRES_PA, TAUCLD, PRCRATE, &
                         WCAVG, WTAVG, AIRM, ALFA0, ALFA2, ALFA3, GAS, &
                         AEROSOL, GASWDEP, AERWDEP, HPWDEP, BETASO4, &
			 MECHCHK )	
!-----------------------------------------------------------------------

      USE AQ_DATA
!slz      USE UTILIO_DEFN

      
! FROM KPP MAIN     **************************     
  USE aqchem_Model
  USE aqchem_initialize_b, ONLY: Initialize
!*****************************************     

      IMPLICIT NONE
      
! kf comment below for CMAQ
!     INCLUDE 'new_AQ_PARAMS.EXT'      ! aqueous chemistry parameters for box
! kf

!      INCLUDE SUBST_CONST          ! constants
!      INCLUDE SUBST_RXCMMN         ! Mechanism reaction common block

      CHARACTER( 120 ) :: XMSG = ' '  ! Exit status message

!..........Parameters:

      INTEGER, PARAMETER :: NUMOX = 5          ! number of oxidation reactions

      REAL( 8 ), PARAMETER :: H2ODENS = 1000.0D0   ! water density at 20 C and 1 ATM (kg/m3)
      REAL( 8 ), PARAMETER :: SEC2HR = 1.0D0 / 3600.0D0 ! convert seconds to hours

!...........Arguments:

      INTEGER,   INTENT( IN )  :: JDATE  ! current model date, coded YYYYDDD
      INTEGER,   INTENT( IN )  :: JTIME  ! current model time, coded HHMMSS

      REAL,      INTENT( IN )  :: AIRM      ! total air mass in cloudy layers (mol/m2)
      REAL,      INTENT( IN )  :: ALFA0     ! scav coef for aitken aerosol number
      REAL,      INTENT( IN )  :: ALFA2     ! scav coef for aitken aerosol sfc area
      REAL,      INTENT( IN )  :: ALFA3     ! scav coef for aitken aerosol mass
      REAL,      INTENT( OUT ) :: HPWDEP    ! hydrogen wet deposition (mm mol/liter)
      REAL( 8 ), INTENT( OUT ) :: BETASO4  
      REAL,      INTENT( IN )  :: PRCRATE   ! precip rate (mm/hr)
      REAL,      INTENT( IN )  :: PRES_PA   ! pressure (Pa)
      REAL,      INTENT( IN )  :: TAUCLD    ! timestep for cloud (s)
      REAL,      INTENT( IN )  :: TEMP2      ! temperature (K)
      REAL,      INTENT( IN )  :: WCAVG     ! liquid water content (kg/m3)
      REAL,      INTENT( IN )  :: WTAVG     ! total water content (kg/m3)
!      LOGICAL,   INTENT( IN )  :: CB5       ! CB5 = TRUE means CB05 gas phase mechanism 
!      LOGICAL,   INTENT( IN )  :: DARK      ! DARK = TRUE is night,  DARK = FALSE is day 
      CHARACTER( 32 ), INTENT( IN ) :: MECHCHK    
      REAL( 8 ), INTENT( INOUT ) :: GAS    ( NGAS )         ! gas phase concentrations (mol/molV)
      REAL( 8 ), INTENT( INOUT ) :: AEROSOL( NAER, NMODES ) ! aerosol concentrations (mol/molV)
      REAL( 8 ), INTENT( INOUT ) :: GASWDEP( NGAS )         ! gas phase wet deposition array (mm mol/liter)
      REAL( 8 ), INTENT( INOUT ) :: AERWDEP( NAER, NMODES ) ! aerosol wet deposition array (mm mol/liter)

!...........Local Variables (scalars):

      LOGICAL, SAVE :: FIRSTIME = .TRUE. ! flag for first pass thru

      CHARACTER( 16 ), SAVE :: PNAME = 'AQCHEM'             ! driver program name
      CHARACTER( 16 ), SAVE :: MGLYSUR = 'METHYL_GLYOXAL  ' ! Henry's law surrogate for MGLY
      
      REAL( 8 ) :: CTHK1, test
      REAL( 8 ) :: ONE_OVER_TEMP
      REAL( 8 ) :: WFACTOR, INVCFAC
      REAL( 8 ) :: DEPSUM, EXPWET
      
      REAL( 8 ) :: TOTNIT, TOTAMM, TOTCL
      REAL( 8 ) :: FNH3, FNH4ACC
      REAL( 8 ) :: FHNO3, FNO3ACC
      REAL( 8 ) :: FHCL, FCLACC
      
!      REAL( 8 ) :: NACOR, CACOR, MGCOR, KCOR, FECOR, MNCOR
!      REAL( 8 ) :: WDNACOR, WDCACOR, WDMGCOR, WDKCOR, WDFECOR, WDMNCOR
      
!      REAL( 8 ) :: S_INIT, S_FINAL, S_PTDIFF
!      REAL( 8 ) :: S_FINAL2, S_PTDIFF2

	REAL :: HEFF,K1,K2,RATIO
      
      INTEGER :: J      
     
! FROM KPP MAIN     **************************
      REAL(kind=dp) :: T, DVAL(NSPEC)
      REAL(kind=dp) :: RSTATE(20)
      INTEGER :: i

!*****************************************     
      INTEGER      IGAS, IAER, IMOD, count
      INTEGER :: XSTAT2, XSTAT3


!...........External Functions:

      INTEGER, SAVE :: LOGDEV
      INTEGER, EXTERNAL :: SETUP_LOGDEV

!*********************************************************************

!...Initialization

      IF ( FIRSTIME ) THEN

        FIRSTIME = .FALSE.

        LOGDEV = SETUP_LOGDEV()

!...Make sure an AE5 version of the mechanism is being used

        IF ( INDEX ( MECHCHK, 'AE5' ) .LE. 0 ) THEN
          XMSG = 'This version of AQCHEM requires an AE5 chemical mechanism'
          CALL M3EXIT ( PNAME, JDATE, JTIME, XMSG, XSTAT3 )
        END IF

!...special treatment of MGLY for CB05 mechanism:
!...  use Henry's law constant for glyoxal as a surrogate for methyl glyoxal

        IF ( INDEX ( MECHCHK, 'CB05' ) .GT. 0 ) THEN
          MGLYSUR = 'GLYOXAL         '
        END IF
      
      END IF    ! FIRSTIME

      ONE_OVER_TEMP = 1.0D0 / TEMP2
      
      IF ( INDEX ( MGLYSUR, 'METHYL' ) .GT. 0 ) THEN
      MGLYH = 3.2D+04 
      ELSE
      MGLYH = 3.6D+05
      ENDIF 
      
!      write(6,*) MGLYH

!...check for bad temperature, cloud air mass, or pressure

      IF ( TEMP2 .LE. 0.0D0 .OR. AIRM .LE. 0.0D0 .OR. PRES_PA .LE. 0.0D0 ) THEN
        XMSG = 'MET DATA ERROR'
        CALL M3EXIT ( PNAME, JDATE, JTIME, XMSG, XSTAT2 )
      END IF
      
      JDATEKPP = JDATE
      JTIMEKPP = JTIME
      

!!!!!!!!!!!!!!! FROM KPP MAIN !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  
!~~~> Initialization 

      STEPMIN = 0.0d0
!      STEPMAX = 0.0d0

!...compute fractional weights for several species     
! NEEDED TO CALCULATE END DISTRIBUTIONS (TO KEEP CONSISTENT WITH BASE)

      TOTNIT = GAS( LHNO3 ) + AEROSOL( LNO3, ACC ) !+ AEROSOL( LNO3, COR )
      IF ( TOTNIT .GT. 0.0D0 ) THEN
        FHNO3   = GAS( LHNO3 ) / TOTNIT
      ELSE
        FHNO3   = 1.0D0
      END IF
      
      IF ( AEROSOL( LNO3, ACC ) + AEROSOL( LNO3, COR ) .GT. 0.0D0 ) THEN
      FNO3ACC = AEROSOL( LNO3, ACC ) / (AEROSOL( LNO3, ACC ) + AEROSOL( LNO3, COR ))  !just aerosol
      ELSE
      FNO3ACC = 1.d0
      ENDIF

      TOTAMM = GAS( LNH3 ) + AEROSOL( LNH4, ACC ) !+ AEROSOL( LNH4, COR )
      IF ( TOTAMM .GT. 0.0D0 ) THEN
        FNH3    = GAS( LNH3 ) / TOTAMM
      ELSE
        FNH3    = 1.0D0
      END IF
      
      IF ( AEROSOL( LNH4, ACC ) + AEROSOL( LNH4, COR ) .GT. 0.0D0 ) THEN      
      FNH4ACC = AEROSOL( LNH4, ACC ) / (AEROSOL( LNH4, ACC ) + AEROSOL( LNH4, COR ))  !just aerosol
      ELSE
      FNH4ACC = 1.d0
      ENDIF
      
      TOTCL = GAS( LHCL ) + AEROSOL( LCL, ACC ) !+ AEROSOL( LCL, COR )
      IF ( TOTCL .GT. 0.0D0 ) THEN
        FHCL    = GAS( LHCL ) / TOTCL
      ELSE
        FHCL    = 1.0D0
      END IF
      
      IF ( AEROSOL( LCL, ACC ) + AEROSOL( LCL, COR ) .GT. 0.0D0 ) THEN            
      FCLACC = AEROSOL( LCL, ACC ) / (AEROSOL( LCL, ACC ) + AEROSOL( LCL, COR ))  !just aerosol
            ELSE
      FCLACC = 1.d0
      ENDIF
     
!!!!!!!!!!

     CTHK1 = AIRM * TEMP2 * 0.08206D0 / ( PRES_PA / 101325.D0 * 1000.0D0 ) ! cloud thickness (m)
          
!kf      CALL Initialize()
      CALL Initialize( TEMP2, PRES_PA, TAUCLD, PRCRATE, &
                         WCAVG, WTAVG, AIRM, ALFA0, ALFA3, GAS, &
                         AEROSOL, CTHK1) !, DARK )
			 
			 INVCFAC = 1.d0 / CFACTOR
			 
!			 S_INIT = 0.d0
!			 S_FINAL = 0.d0
!			 S_PTDIFF =  0.d0
!			 S_FINAL2 = 0.d0
!			 S_PTDIFF2 =  0.d0
			 
!      S_INIT = var(ind_G_SO2)+var(ind_L_SO2) + var(ind_L_HSO3MIN) + &
!           var(ind_L_SO3MIN2) + var(ind_A_SO4AKN) + &
!	   var(ind_L_H2SO4) + var(ind_L_HSO4MIN) + &
!	   var(ind_L_SO4MIN2)

!~~~> Time loop
      T = TSTART
kron: DO WHILE (T < TEND)

        TIME = T

!        CALL SaveData()
!        CALL Update_SUN() 
        CALL Update_RCONST()
	

        CALL INTEGRATE( TIN = T, TOUT = T+DT, RSTATUS_U = RSTATE, &
        ICNTRL_U = (/ 1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 /))  ! rodas3 - autonomous
!        ICNTRL_U = (/ 1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 /) )  ! ros2 - autonomous
!        ICNTRL_U = (/ 1,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 /) )  ! ros3 - autonomous
!	 ICNTRL_U = (/ 1,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 /) )  ! ros4 - autonomous
!        ICNTRL_U = (/ 1,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 /) )  ! rodas4 - autonomous
!        ICNTRL_U = (/ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 /) )  ! rodas3 - default
!kf        ICNTRL_U = (/ 0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 /) )  ! ros2
!kf        ICNTRL_U = (/ 0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 /) )  ! ros3
!kf        ICNTRL_U = (/ 0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 /) )  ! rodas4
!kf	ICNTRL_U = (/ 0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 /)) 
!	write(6,*) VAR(ind_L_GLY), VAR(ind_L_ORGC), VAR(ind_G_GLY)
!	write(6,*) VAR(ind_L_MGLY), VAR(ind_G_MGLY)
!	write(6,*)(VAR(ind_G_GLY) + VAR(ind_L_GLY))*INVCFAC*1e9
!	pause


        T = RSTATE(1)

      END DO kron

      TIME = T
      
!            S_FINAL = var(ind_G_SO2)+var(ind_L_SO2) + var(ind_L_HSO3MIN) + &
!           var(ind_L_SO3MIN2) + var(ind_A_SO4AKN) + &
!	   var(ind_L_H2SO4) + var(ind_L_HSO4MIN) + &
!	   var(ind_L_SO4MIN2) + var(ind_WD_SO2) + var(ind_WD_H2SO4) 
	   
!	   IF(S_INIT .gt. 0d0) then
!	   S_PTDIFF = 100.d0 * (S_INIT - S_FINAL) / S_INIT
!	   else
!	   write(6,*) "NO INIT S"
!	   endif


!END PROGRAM aqchem_Driver


!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!     Output 

        GASWDEP = 0.d0
        AERWDEP = 0.d0
     
        WFACTOR = WCAVG * CTHK1 * PHI2 !1/XC1 in original AQCHEM
        EXPWET = EXP( -WETFAC_KPP * TAUCLD )
	
!	K1 = 1.39E-02*EXP(1870*DELINVT)
!	K2 = 6.72E-08*EXP(355*DELINVT)
!	HEFF = 1.4*EXP(2900*DELINVT) !* &
!	(1+K1/(var(ind_L_HPLUS)*PHI2)+K1*K2/(var(ind_L_HPLUS)*PHI2)/(var(ind_L_HPLUS)*PHI2))
	
!	RATIO =  (VAR(ind_L_SO2) + VAR(ind_L_HSO3MIN) + VAR(ind_L_SO3MIN2))*PHI2 / &
!	((VAR(ind_G_SO2))*INVCFAC)
	
!	RATIO =  (VAR(ind_L_SO2))*PHI2 / &
!	((VAR(ind_G_SO2))*INVCFAC)
	
!	write(6,*) HEFF, RATIO
!	pause
	
!    AEROSOL SPECIES, AKN

        AEROSOL(LNO3,AKN) = VAR(ind_A_NO3AKN) *INVCFAC
        AEROSOL(LNH4,AKN) = VAR(ind_A_NH4AKN)*INVCFAC
        AEROSOL(LCL,AKN) = VAR(ind_A_CLAKN) *INVCFAC
        AEROSOL(LNA,AKN) = VAR(ind_A_NAAKN) *INVCFAC
        AEROSOL(LSO4,AKN) = VAR(ind_A_SO4AKN) *INVCFAC
        AEROSOL(LEC,AKN) = VAR(ind_A_PECAKN) *INVCFAC
!slz        AEROSOL(LPOA,AKN) = VAR(ind_A_POAAKN) *INVCFAC
        AEROSOL(LPRI,AKN) = VAR(ind_A_PRIAKN) *INVCFAC
        AEROSOL(LNUM, AKN) = AEROSOL(LNUM, AKN) * EXP(-ALFA0 * TAUCLD) 
     
!    AERWDEP, COR

!	AERWDEP(LSOILC, COR) = AEROSOL(LSOILC,COR) * (1 - EXPWET) * CFACTOR !* WFACTOR	
!	AERWDEP(LSEASC, COR) = AEROSOL(LSEASC,COR) * (1 - EXPWET) * CFACTOR !* WFACTOR	
!	AERWDEP(LANTHC, COR) = AEROSOL(LANTHC,COR) * (1 - EXPWET) * CFACTOR !* WFACTOR	
	AERWDEP(LSO4, COR) = AEROSOL(LSO4,COR) * (1 - EXPWET) * CFACTOR !* WFACTOR
	AERWDEP(LNH4, COR) = AEROSOL(LNH4,COR) * (1 - EXPWET) * CFACTOR !* WFACTOR
	AERWDEP(LNO3, COR) = AEROSOL(LNO3,COR) * (1 - EXPWET) * CFACTOR !* WFACTOR
	AERWDEP(LCL, COR) = AEROSOL(LCL,COR) * (1 - EXPWET) * CFACTOR !* WFACTOR
	
        AERWDEP(LPRICOR, COR) = AEROSOL(LPRICOR,COR) * (1 - EXPWET) * CFACTOR !* WFACTOR
        AERWDEP(LNA, COR) = AEROSOL(LNA,COR) * (1 - EXPWET) * CFACTOR !* WFACTOR
	
	AERWDEP(LA3FE,COR) = AEROSOL(LA3FE,COR) * (1 - EXPWET) * CFACTOR !* WFACTOR
	AERWDEP(LB2MN,COR) = AEROSOL(LB2MN,COR) * (1 - EXPWET) * CFACTOR !* WFACTOR			
	AERWDEP(LCACO3,COR) = AEROSOL(LCACO3,COR) * (1 - EXPWET) * CFACTOR !* WFACTOR
        AERWDEP(LMGCO3,COR) = AEROSOL(LMGCO3,COR) * (1 - EXPWET) * CFACTOR !* WFACTOR
        AERWDEP(LK,COR) = AEROSOL(LK,COR) * (1 - EXPWET) * CFACTOR !* WFACTOR
	
!       WRITE(6,*) CHECK THAT THIS MATCHES WITH DYNAMIC SPECIES!!!	

!    AEROSOL SPECIES, COR 

	AEROSOL(LNUM, COR) = AEROSOL(LNUM, COR) * EXPWET 
!	AEROSOL(LSOILC,COR) = AEROSOL(LSOILC,COR) * EXPWET
!	AEROSOL(LSEASC,COR) = AEROSOL(LSEASC,COR) * EXPWET
!	AEROSOL(LANTHC,COR) = AEROSOL(LANTHC,COR) * EXPWET
	AEROSOL(LSO4,COR) = AEROSOL(LSO4,COR) * EXPWET
	AEROSOL(LNH4,COR) = AEROSOL(LNH4,COR) * EXPWET
	AEROSOL(LNO3,COR) = AEROSOL(LNO3,COR) * EXPWET
	AEROSOL(LCL,COR) = AEROSOL(LCL,COR) * EXPWET	
	
	AEROSOL(LPRICOR,COR) = AEROSOL(LPRICOR,COR) * EXPWET
	AEROSOL(LNA,COR) = AEROSOL(LNA,COR) * EXPWET	
	AEROSOL(LA3FE,COR) = AEROSOL(LA3FE,COR) * EXPWET	
	AEROSOL(LB2MN,COR) = AEROSOL(LB2MN,COR) * EXPWET	
	AEROSOL(LCACO3,COR) = AEROSOL(LCACO3,COR) * EXPWET	
	AEROSOL(LMGCO3,COR) = AEROSOL(LMGCO3,COR) * EXPWET	
	AEROSOL(LK,COR) = AEROSOL(LK,COR) * EXPWET	
	
	DO I = 1, NAER
	IF (AEROSOL(I, COR) .LT. 1D-30) AEROSOL(I, COR) = 0.d0
	ENDDO	
	
!    AERWDEP, ACC	   

!slz	AERWDEP(LSOA, ACC) = AEROSOL(LSOA,ACC) * (1 - EXPWET) * CFACTOR !* WFACTOR  
	
!	WDFECOR   = 0.0281D0  * ( 100.0D0 / 55.8D0 ) * AERWDEP(LSOILC,COR) / ( 1.0 - 0.04642 ) &
!                + 0.0467D0  * ( 100.0D0 / 55.8D0 ) * AERWDEP(LANTHC,COR) / ( 1.0 - 0.00325 )
!        WDMNCOR   = 0.00078D0 * ( 100.0D0 / 54.9D0 ) * AERWDEP(LSOILC,COR) / ( 1.0 - 0.04642 ) &
!                + 0.0011D0  * ( 100.0D0 / 54.9D0 ) * AERWDEP(LANTHC,COR) / ( 1.0 - 0.00325 )	
!        WDNACOR   = 0.8373D0  * (  23.0D0 / 23.0D0 ) * AERWDEP(LSEASC, COR) &                    
!                + 0.0652D0  * ( 100.0D0 / 23.0D0 ) * AERWDEP(LSOILC, COR) / ( 1.0 - 0.04642 ) &
!                + 0.0023D0  * ( 100.0D0 / 23.0D0 ) * AERWDEP(LANTHC, COR) / ( 1.0 - 0.00325 )
!        WDMGCOR   = 0.0997D0  * (  23.0D0 / 24.3D0 ) * AERWDEP(LSEASC, COR) &                    
!                + 0.0000D0  * ( 100.0D0 / 24.3D0 ) * AERWDEP(LSOILC, COR) / ( 1.0 - 0.04642 ) &
!                + 0.0032D0  * ( 100.0D0 / 24.3D0 ) * AERWDEP(LANTHC, COR) / ( 1.0 - 0.00325 )
!        WDCACOR   = 0.0320D0  * (  23.0D0 / 40.1D0 ) * AERWDEP(LSEASC, COR) &                 
!                + 0.0872D0  * ( 100.0D0 / 40.1D0 ) * AERWDEP(LSOILC, COR) / ( 1.0 - 0.04642 ) &
!                + 0.0562D0  * ( 100.0D0 / 40.1D0 ) * AERWDEP(LANTHC, COR) / ( 1.0 - 0.00325 )
!        WDKCOR    = 0.0310D0  * (  23.0D0 / 39.1D0 ) * AERWDEP(LSEASC, COR) &                 
!                + 0.0252D0  * ( 100.0D0 / 39.1D0 ) * AERWDEP(LSOILC, COR) / ( 1.0 - 0.04642 ) &
!                + 0.0176D0  * ( 100.0D0 / 39.1D0 ) * AERWDEP(LANTHC, COR) / ( 1.0 - 0.00325 ) 
	
!	AERWDEP(LFEACC, ACC) = MAX(VAR(ind_WD_FEPLUS3)/FE_III/FE_SOL - WDFECOR, 0.d0)
!	AERWDEP(LMNACC,ACC) = MAX(VAR(ind_WD_MNPLUS2)/MN_SOL/MN_II - WDMNCOR, 0.d0)			
!	AERWDEP(LNA, ACC) = MAX(VAR(ind_WD_NAPLUS) - WDNACOR, 0.d0)
!	AERWDEP(LCAACC,ACC) = MAX(VAR(ind_WD_CAPLUS2) - WDCACOR, 0.d0)
!        AERWDEP(LMGACC,ACC) = MAX(VAR(ind_WD_MGPLUS2) - WDMGCOR, 0.d0)
!        AERWDEP(LKACC,ACC) = MAX(VAR(ind_WD_KPLUS) - WDKCOR, 0.d0)
	
        AERWDEP(LSO4,ACC) = MAX((VAR(ind_WD_H2SO4)) - AERWDEP(LSO4,COR), 0.d0)
        AERWDEP(LNH4,ACC) = MAX((VAR(ind_WD_NH4PLUS)) - AERWDEP(LNH4,COR), 0.d0)
        AERWDEP(LNO3,ACC) = MAX((VAR(ind_WD_NO3MIN)) - AERWDEP(LNO3,COR), 0.d0)
        AERWDEP(LCL,ACC) = MAX((VAR(ind_WD_CLMIN)) - AERWDEP(LCL,COR), 0.d0)
	
	AERWDEP(LNA,ACC) = MAX((VAR(ind_WD_NAPLUS)) - AERWDEP(LNA,COR), 0.d0)
			
	AERWDEP(LPRI,ACC) = VAR(ind_WD_PRIACC)
        AERWDEP(LEC,ACC) = VAR(ind_WD_PECACC)
        AERWDEP(LORGC,ACC) = VAR(ind_WD_ORGC)
!slz        AERWDEP(LPOA,ACC) = VAR(ind_WD_POAACC)	
	
	
!  FOR VOLATILE SPECIES IN THE COARSE MODE

	IF(AERWDEP(LNH4,COR) .GT. VAR(ind_WD_NH4PLUS)) THEN
	AERWDEP(LNH4,COR) = (1.d0-FNH4ACC) * VAR(ind_WD_NH4PLUS)
	AERWDEP(LNH4,ACC) = FNH4ACC * VAR(ind_WD_NH4PLUS)
	AEROSOL(LNH4,COR) = (1.d0-FNH4ACC) * (VAR(ind_L_NH4OH) + VAR(ind_L_NH4PLUS))*INVCFAC
	ENDIF
	
	IF(AERWDEP(LNO3,COR) .GT. VAR(ind_WD_NO3MIN)) THEN
	AERWDEP(LNO3,COR) = (1.d0-FNO3ACC) * VAR(ind_WD_NO3MIN)
	AERWDEP(LNO3,ACC) = FNO3ACC * VAR(ind_WD_NO3MIN)
	AEROSOL(LNO3,COR) = (1.d0-FNO3ACC) * (VAR(ind_L_HNO3) + VAR(ind_L_NO3MIN))*INVCFAC
	ENDIF
	
	IF(AERWDEP(LCL,COR) .GT. VAR(ind_WD_CLMIN)) THEN
	AERWDEP(LCL,COR) = (1.d0-FCLACC) * VAR(ind_WD_CLMIN)
	AERWDEP(LCL,ACC) = FCLACC * VAR(ind_WD_CLMIN)
	AEROSOL(LCL,COR) = (1.d0-FCLACC) * (VAR(ind_L_CLMIN))*INVCFAC
	ENDIF	
	  
!    AEROSOL SPECIES, ACC
     	
        AEROSOL(LPRI,ACC) = VAR(ind_L_PRIACC) *INVCFAC
        AEROSOL(LEC,ACC) = VAR(ind_L_PECACC) *INVCFAC 
        AEROSOL(LORGC,ACC) = VAR(ind_L_ORGC)*INVCFAC 
!slz        AEROSOL(LPOA,ACC) = VAR(ind_L_POAACC)*INVCFAC 
!slz	AEROSOL(LSOA, ACC) = AEROSOL(LSOA, ACC) * EXPWET  
	
!	FECOR   = 0.0281D0  * ( 100.0D0 / 55.8D0 ) * AEROSOL(LSOILC,COR) / ( 1.0 - 0.04642 ) &
!                + 0.0467D0  * ( 100.0D0 / 55.8D0 ) * AEROSOL(LANTHC,COR) / ( 1.0 - 0.00325 )
!        MNCOR   = 0.00078D0 * ( 100.0D0 / 54.9D0 ) * AEROSOL(LSOILC,COR) / ( 1.0 - 0.04642 ) &
!                + 0.0011D0  * ( 100.0D0 / 54.9D0 ) * AEROSOL(LANTHC,COR) / ( 1.0 - 0.00325 )
!        NACOR   = 0.8373D0  * (  23.0D0 / 23.0D0 ) * AEROSOL(LSEASC,COR) &                    
!                + 0.0652D0  * ( 100.0D0 / 23.0D0 ) * AEROSOL(LSOILC,COR) / ( 1.0 - 0.04642 ) &
!                + 0.0023D0  * ( 100.0D0 / 23.0D0 ) * AEROSOL(LANTHC,COR) / ( 1.0 - 0.00325 )
!        MGCOR   = 0.0997D0  * (  23.0D0 / 24.3D0 ) * AEROSOL(LSEASC,COR) &                    
!                + 0.0000D0  * ( 100.0D0 / 24.3D0 ) * AEROSOL(LSOILC,COR) / ( 1.0 - 0.04642 ) &
!                + 0.0032D0  * ( 100.0D0 / 24.3D0 ) * AEROSOL(LANTHC,COR) / ( 1.0 - 0.00325 )
!        CACOR   = 0.0320D0  * (  23.0D0 / 40.1D0 ) * AEROSOL(LSEASC,COR) &                 
!                + 0.0872D0  * ( 100.0D0 / 40.1D0 ) * AEROSOL(LSOILC,COR) / ( 1.0 - 0.04642 ) &
!                + 0.0562D0  * ( 100.0D0 / 40.1D0 ) * AEROSOL(LANTHC,COR) / ( 1.0 - 0.00325 )
!        KCOR    = 0.0310D0  * (  23.0D0 / 39.1D0 ) * AEROSOL(LSEASC,COR) &                 
!                + 0.0252D0  * ( 100.0D0 / 39.1D0 ) * AEROSOL(LSOILC,COR) / ( 1.0 - 0.04642 ) &
!                + 0.0176D0  * ( 100.0D0 / 39.1D0 ) * AEROSOL(LANTHC,COR) / ( 1.0 - 0.00325 )	
	
!	AEROSOL(LFEACC, ACC) = MAX((VAR(ind_L_FEPLUS3)/FE_III/FE_SOL - FECOR*CFACTOR)*INVCFAC, 0.d0)
!	AEROSOL(LMNACC, ACC) = MAX((VAR(ind_L_MNPLUS2)/MN_II/MN_SOL - MNCOR*CFACTOR) *INVCFAC, 0.d0)			
!	AEROSOL(LNA, ACC) = MAX((VAR(ind_L_NAPLUS) - NACOR*CFACTOR) *INVCFAC, 0.d0)
!	AEROSOL(LCAACC,ACC) = MAX((VAR(ind_L_CAPLUS2) - CACOR*CFACTOR) *INVCFAC, 0.d0) 
!        AEROSOL(LMGACC,ACC) = MAX((VAR(ind_L_MGPLUS2) - MGCOR*CFACTOR) *INVCFAC, 0.d0) 
!        AEROSOL(LKACC,ACC) = MAX((VAR(ind_L_KPLUS) - KCOR*CFACTOR) *INVCFAC, 0.d0) 
	
	AEROSOL(LSO4,ACC) = MAX(((VAR(ind_L_H2SO4) + VAR(ind_L_SO4MIN2) + &
              VAR(ind_L_HSO4MIN)) *INVCFAC) - AEROSOL(LSO4,COR), 0.d0) 
	AEROSOL(LCL,ACC) = MAX((VAR(ind_L_CLMIN) *INVCFAC) - AEROSOL(LCL,COR), 0.d0)
	    
	AEROSOL(LNA,ACC) = MAX((VAR(ind_L_NAPLUS) *INVCFAC) - AEROSOL(LNA,COR), 0.d0) 
	
       TOTAMM = VAR(ind_G_NH3) + VAR(ind_L_NH4OH) + VAR(ind_L_NH4PLUS) - AEROSOL(LNH4,COR)*CFACTOR
       TOTNIT = VAR(ind_G_HNO3) + VAR(ind_L_HNO3) + VAR(ind_L_NO3MIN) - AEROSOL(LNO3,COR)*CFACTOR

       TOTAMM = MAX(TOTAMM, 0.d0)
       TOTNIT = MAX(TOTNIT, 0.d0)
    
!      AEROSOL(LNO3,ACC) = (FNO3ACC*TOTNIT) * INVCFAC
!       AEROSOL(LNH4,ACC) = (FNH4ACC*TOTAMM) * INVCFAC      

      AEROSOL(LNO3,ACC) = ((1.d0-FHNO3)*TOTNIT) * INVCFAC
       AEROSOL(LNH4,ACC) = ((1.d0-FNH3)*TOTAMM) * INVCFAC      
	
!       AEROSOL(LNUM, ACC) = AEROSOL(LNUM, ACC) * EXPWET 

!    GAS PHASE SPECIES

        GAS(LSO2) = (VAR(ind_G_SO2) + VAR(ind_L_SO2) + VAR(ind_L_HSO3MIN) + VAR(ind_L_SO3MIN2))*INVCFAC
        GAS(LN2O5) = 0.D0
        GAS(LCO2) = (VAR(ind_G_CO2) + VAR(ind_L_H2CO3) + VAR(ind_L_HCO3MIN) + VAR(ind_L_CO3MIN2))*INVCFAC
        GAS(LH2O2)= (VAR(ind_G_H2O2) + VAR(ind_L_H2O2))*INVCFAC 
        GAS(LO3) = (VAR(ind_G_O3) + VAR(ind_L_O3))*INVCFAC  
        GAS(LFOA) = (VAR(ind_G_HCOOH) + VAR(ind_L_HCOOH) + VAR(ind_L_HCOOMIN))*INVCFAC
        GAS(LMHP) = (VAR(ind_G_MHP) + VAR(ind_L_MHP))*INVCFAC
        GAS(LPAA) = (VAR(ind_G_PAA) + VAR(ind_L_PAA))*INVCFAC 
        GAS(LH2SO4) = 0.D0
        GAS(LHCL) = (VAR(ind_G_HCL) + VAR(ind_L_HCL))*INVCFAC ! for now, just putting non"ionized" back into gas
        GAS(LGLY) = (VAR(ind_G_GLY) + VAR(ind_L_GLY))*INVCFAC
        GAS(LMGLY) = (VAR(ind_G_MGLY) + VAR(ind_L_MGLY))*INVCFAC
!        GAS(LHO) = (VAR(ind_G_HO) + VAR(ind_L_HO))*INVCFAC	
        GAS(LHNO3) = (FHNO3*TOTNIT)*INVCFAC
	GAS(LNH3) = (FNH3*TOTAMM)*INVCFAC

!    GASWDEP

     GASWDEP(LSO2) = VAR(ind_WD_SO2) 
     GASWDEP(LHNO3) = VAR(ind_WD_HNO3)
     GASWDEP(LN2O5) = 0.D0  ! already transferred to HNO3
     GASWDEP(LCO2) = VAR(ind_WD_CO2)
     GASWDEP(LNH3) = VAR(ind_WD_NH4OH)
     GASWDEP(LH2O2) = VAR(ind_WD_H2O2)
     GASWDEP(LO3) = VAR(ind_WD_O3)
     GASWDEP(LFOA) = VAR(ind_WD_HCOOH)
     GASWDEP(LMHP) = VAR(ind_WD_MHP)
     GASWDEP(LPAA) = VAR(ind_WD_PAA)
     GASWDEP(LH2SO4) = 0.D0  ! already transferred to SO4
     GASWDEP(LHCL) = VAR(ind_WD_HCL)
     GASWDEP(LGLY) = VAR(ind_WD_GLY)
     GASWDEP(LMGLY) = VAR(ind_WD_MGLY)
!     GASWDEP(LHO) = VAR(ind_WD_HO)
         
! Convert to appropriate units (mol / m2)
     
     DO I=1,NGAS
     GASWDEP(I) = GASWDEP(I) * WFACTOR
     ENDDO
     
     DO J=1,NMODES
     DO I=1,NAER
     AERWDEP(I,J) = AERWDEP(I,J) * WFACTOR
     ENDDO
     ENDDO     
     
     DO I = 1, NGAS
     IF(GAS(I) .LT. 0.d0) GAS(I) = 0.d0
     IF(GASWDEP(I) .LT. 0.d0) GASWDEP(I) = 0.d0
     ENDDO
     
     DO J=1,NMODES
     DO I=1,NAER
     IF(AEROSOL(I,J) .LT. 0.d0) AEROSOL(I,J) = 0.d0
     IF(AERWDEP(I,J) .LT. 0.d0) AERWDEP(I,J) = 0.d0
     ENDDO
     ENDDO  

!...store the amount of hydrogen deposition

      HPWDEP = VAR( ind_WD_HPLUS ) * WFACTOR
      BETASO4 = 0.D0
      DEPSUM =  AERWDEP( LSO4,ACC ) / WFACTOR
      
      IF( AEROSOL(LSO4,ACC) * CFACTOR + DEPSUM .NE. 0.d0 ) THEN
        BETASO4 = DEPSUM / ( AEROSOL(LSO4,ACC) * CFACTOR + DEPSUM ) &
	 / TAUCLD	
      ELSE
        BETASO4 = 0.d0
      ENDIF
      
       AEROSOL(LNUM, ACC) = AEROSOL(LNUM, ACC) * EXP(-BETASO4 * TAUCLD)

!       AEROSOL(LNUM, ACC) = AEROSOL(LNUM, ACC) * EXPWET 


     
!           S_FINAL2 = (GAS(LSO2) + AEROSOL(LSO4, AKN) + AEROSOL(LSO4,ACC) +&
!	   AEROSOL(LSO4,COR))*CFACTOR + (GASWDEP(LSO2) + AERWDEP(LSO4,ACC) + &
!	   AERWDEP(LSO4,COR))/WFACTOR
	   
!	   IF(S_INIT .gt. 0d0) then
!	   S_PTDIFF2 = 100.d0 * (S_INIT - S_FINAL2) / S_INIT
!!	   else
!!	   write(6,*) "NO INIT S"
!	   endif

	
!	write(45,*) S_PTDIFF, S_PTDIFF2

     
      RETURN

!...formats

!1001  FORMAT ( 1X, 'STORM RATE=', F6.3, 'DSIVDT(0) =', F10.5,
!     &       'TS6=', F10.5, 'DTW(0)=', F10.5, 'CTHK1=', F10.5,
!     &       'WTAVG=', F10.5 )

      END
