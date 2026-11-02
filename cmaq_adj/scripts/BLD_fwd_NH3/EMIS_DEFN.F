C***********************************************************************
C   Portions of Models-3/CMAQ software were developed or based on      *
C   information from various groups: Federal Government employees,     *
C   contractors working on a United States Government contract, and    *
C   non-Federal sources (including research institutions).  These      *
C   research institutions have given the Government permission to      *
C   use, prepare derivative works, and distribute copies of their      *
C   work in Models-3/CMAQ to the public and to permit others to do     *
C   so.  EPA therefore grants similar permissions for use of the       *
C   Models-3/CMAQ software, but users are requested to provide copies  *
C   of derivative works to the Government without restrictions as to   *
C   use by others.  Users are responsible for acquiring their own      *
C   copies of commercial software associated with Models-3/CMAQ and    *
C   for complying with vendor requirements.  Software copyrights by    *
C   the MCNC Environmental Modeling Center are used with their         *
C   permissions subject to the above restrictions.                     *
C***********************************************************************

C RCS file, release, date & time of last delta, author, state, [and locker]
C $Header: /Volumes/Data/CVS/CMAQ_CVSrepos/CCTM/src/vdiff/acm2_inline_adj_fwd/EMIS_DEFN.F,v 1.1 2011/02/22 01:10:45 ppercell Exp $

C what(1) key, module and SID; SCCS file; date and time of last delta:
C %W% %P% %G% %U%

C:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      MODULE EMIS_DEFN

C-----------------------------------------------------------------------
C Function: emissions interface to the chemistry-transport model

C Revision History:
C     28 Jul 2006 J.Young: initial implementation
C     18 Aug 2007 J.Young: move beis part to separate module; add plume rise
C     26 Jan 2010 J.Young: fix bug overwriting point source layer 1 NH3; inline rdemis

C-----------------------------------------------------------------------

      USE GRID_CONF           ! horizontal & vertical domain specifications
      USE ADJ_ARRAY_MOD, only : FDMTEST ! logical controlling finite difference test !Added by mhrzmomeni 1.2019

      IMPLICIT NONE

      REAL, ALLOCATABLE, SAVE :: VDEMIS( :,:,:,: ) ! total emissions array

      INTEGER, SAVE :: N_SPC_EMIS ! global emissions species
      INTEGER, SAVE :: EMLAYS     ! no. of emis integration layers
                                  ! EMLAYS must be .LT. NLAYS
      INTEGER,          SAVE :: EMLYRS     ! no. of layers on base emis input file -
                                           ! a 2d file if inline, otherwise a 3d file
      INTEGER, PRIVATE, SAVE :: NEMIS_AE   ! no. of aero emis species

      LOGICAL, PRIVATE, SAVE :: EM_TRAC = .FALSE. ! do tracer emissions?
      REAL,    PRIVATE, SAVE :: CNVTE      ! combined conversion factor
      REAL,    PRIVATE, SAVE :: DT         ! TSTEP (output) in sec

      REAL,    PRIVATE, ALLOCATABLE, SAVE :: VDEMIS_AE( :,:,:,: ) ! aerosol emis
      REAL,    PRIVATE, ALLOCATABLE, SAVE :: BUFF( :,:,: )        ! read buffer

      INTEGER, PRIVATE, SAVE :: STRT_GC, FINI_GC, STRT_AE, FINI_AE,
     &                          STRT_NR, FINI_NR, STRT_TR, FINI_TR
      INTEGER, PRIVATE, SAVE :: SDATE, STIME  ! scenario start date/time (beis)
      INTEGER, PRIVATE       :: LDATE, LTIME  ! step start date/time (beis)
      INTEGER, PRIVATE, SAVE :: NDATE, NTIME  ! step next date/time (beis)

      CONTAINS

C-----------------------------------------------------------------------
         FUNCTION EMIS_INIT ( JDATE, JTIME, TSTEP ) RESULT ( SUCCESS ) 

         USE BEIS_DEFN           ! biogenic emissions
         USE PT3D_DEFN           ! plume rise emissions
         USE PMEM_DEFN           ! defines emissions file(s) PM mapping

         IMPLICIT NONE
      
C Includes:

         INCLUDE SUBST_AE_SPC    ! aerosol species table
         INCLUDE SUBST_GC_EMIS   ! gas chem emis surrogate names & map table
         INCLUDE SUBST_AE_EMIS   ! aerosol emission surrogate names & map table
         INCLUDE SUBST_NR_EMIS   ! non-react emis surrogate names & map table
         INCLUDE SUBST_TR_EMIS   ! tracer emis surrogate names & map table
         INCLUDE SUBST_CONST     ! constants
         INCLUDE SUBST_IOPARMS   ! I/O parameters definitions
#include         SUBST_IODECL    ! I/O definitions and declarations

C Arguments:

         INTEGER JDATE, JTIME, TSTEP
         LOGICAL :: SUCCESS

C External Functions:

         INTEGER, EXTERNAL :: ENVINT

C Parameters:

         REAL, PARAMETER :: CMLMR = 1.0E+06       ! ppmV/Molar Mixing Ratio

C Local Variables:

         REAL    CONVEM          ! conversion for emissions rates to Kg/s
         REAL    DX1, DX2        ! CX x1- and x2-cell widths

         CHARACTER( 16 ), SAVE :: CTM_EMLAYS = 'CTM_EMLAYS'    ! env var for no. of
                                                               ! emiss. layers
         CHARACTER( 16 ) :: PNAME = 'EMIS_INIT'
         CHARACTER( 80 ) :: VARDESC   ! env variable description
         CHARACTER( 120 ) :: XMSG = ' '
         INTEGER V, K, LOGDEV, STATUS

C-----------------------------------------------------------------------

         SUCCESS = .TRUE.

         LOGDEV = INIT3()

         IF ( GDTYP_GD .EQ. LATGRD3 ) THEN
            DX1 = DG2M * XCELL_GD ! in m.
            DX2 = DG2M * YCELL_GD
     &          * COS( PI180*( YORIG_GD + YCELL_GD*FLOAT( GL_NROWS/2 )))! in m.
         ELSE
            DX1 = XCELL_GD        ! in m.
            DX2 = YCELL_GD        ! in m.
         END IF

C In-line biogenic emissions?

         IF ( .NOT. BEIS_INIT( JDATE, JTIME, TSTEP ) ) THEN
            XMSG = 'Failure initializing biogenics emissions module'
            CALL M3EXIT ( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
         END IF

C Open Emissions files

         CALL OPEMIS ( JDATE, JTIME, N_GC_EMIS, EM_TRAC, CONVEM, EMLAYS )

C Get number of emissions layers

         IF ( EMLAYS .LE. 1 ) THEN   ! better be inline plume rise run
            EMLAYS = NLAYS   ! env var default
            VARDESC = 'Number of emission layers'
            EMLAYS = ENVINT( CTM_EMLAYS, VARDESC, EMLAYS, STATUS )
            IF ( STATUS .NE. 0 ) THEN
               WRITE( LOGDEV, '(5X, A)' ) VARDESC
               IF ( STATUS .EQ. 1 ) THEN
                  XMSG = 'Environment variable improperly formatted'
                  CALL M3WARN ( PNAME, JDATE, JTIME, XMSG )
                  SUCCESS = .FALSE.; RETURN
               ELSE
                  XMSG = 'Environment variable not set or empty ... Using default:'
                  WRITE( LOGDEV, '(5X, A, I9)' ) XMSG, JTIME
               END IF
            END IF
         END IF

         EMLAYS = MIN ( EMLAYS, NLAYS )

         WRITE( LOGDEV,1009 ) EMLAYS, NLAYS
1009     FORMAT( / 10X, 'Number of Emissions Layers:         ', I3
     &           / 10X, 'out of total Number of Model Layers:', I3 )

         IF ( N_AE_SPC .GT. 0 ) THEN
            WRITE( LOGDEV,'( /5X, A )' ) 'Aerosol Emissions Processing in '
     &                                // 'Vertical diffusion ...'
            NEMIS_AE = N_AE_EMIS  ! from AE_EMIS.EXT
C set up PM species mapping from emissions file(s) for use in GET_AERO_EMIS
            CALL GET_PMEM_MAP ( JDATE, JTIME )   ! set in PMEM_DEFN
         ELSE
            NEMIS_AE = 0
         END IF

         N_SPC_EMIS = N_GC_EMIS
     &              + NEMIS_AE
     &              + N_NR_EMIS
     &              + N_TR_EMIS

C 3D point source emissions (N_SPC_EMIS+1 serves as the null map for PTEM_MAP)
         IF ( .NOT. PT3D_INIT( N_SPC_EMIS, EMLAYS, JDATE, JTIME, TSTEP ) ) THEN
            XMSG = 'Failure initializing plume rise emissions module'
            CALL M3EXIT ( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
         END IF

         ALLOCATE ( VDEMIS ( N_SPC_EMIS+1,EMLAYS,MY_NCOLS,MY_NROWS ),
     &              STAT = STATUS )
         IF ( STATUS .NE. 0 ) THEN
            XMSG = 'VDEMIS memory allocation failed'
            CALL M3WARN ( PNAME, JDATE, JTIME, XMSG )
            SUCCESS = .FALSE.; RETURN
         END IF

         IF ( PT3DEMIS ) THEN
            EMLYRS = 1
         ELSE
            EMLYRS = EMLAYS
         END IF

         IF ( N_SPC_EMIS .LE. 0 ) THEN
            XMSG = 'There are no emissions: VDEMIS is set to zero' ! below
            CALL M3WARN ( PNAME, JDATE, JTIME, XMSG )
         END IF

         IF ( N_AE_SPC .GT. 0 ) THEN   ! all EMLAYS
            ALLOCATE ( VDEMIS_AE( NEMIS_AE,EMLAYS,MY_NCOLS,MY_NROWS ),
     &                 STAT = STATUS )
            IF ( STATUS .NE. 0 ) THEN
               XMSG = 'VDEMIS_AE memory allocation failed'
               CALL M3WARN ( PNAME, JDATE, JTIME, XMSG )
               SUCCESS = .FALSE.; RETURN
            END IF
            VDEMIS_AE = 0.0   ! array assignment
         END IF

         ALLOCATE ( BUFF( NCOLS,NROWS,EMLYRS ), STAT = STATUS )
         IF ( STATUS .NE. 0 ) THEN
            XMSG = 'BUFF memory allocation failed'
            CALL M3WARN ( PNAME, JDATE, JTIME, XMSG )
            SUCCESS = .FALSE.; RETURN
         END IF
         BUFF = 0.0   ! array assignment

C combined gas emssions conversion factor

         CNVTE = CMLMR * CONVEM * MWAIR / ( DX1 * DX2 )

         STRT_GC = 1
         FINI_GC = N_GC_EMIS
         STRT_AE = N_GC_EMIS + 1
         FINI_AE = N_GC_EMIS + NEMIS_AE
         STRT_NR = N_GC_EMIS + NEMIS_AE + 1
         FINI_NR = N_GC_EMIS + NEMIS_AE + N_NR_EMIS
         STRT_TR = N_GC_EMIS + NEMIS_AE + N_NR_EMIS + 1
         FINI_TR = N_GC_EMIS + NEMIS_AE + N_NR_EMIS + N_TR_EMIS

         SUCCESS = .TRUE.; RETURN

         END FUNCTION EMIS_INIT

C-----------------------------------------------------------------------
         SUBROUTINE GET_EMIS ( JDATE, JTIME, TSTEP, CONVPA,
     &                         RDX3F, RRHOJ, RJACM )

         USE AERO_EMIS           ! inherits GRID_CONF
         USE BEIS_DEFN           ! biogenic emissions
         USE BIOG_EMIS, ONLY: MSPCS
         USE PT3D_DEFN           ! plume rise emissions
         USE PMEM_DEFN           ! defines emissions file(s) PM mapping
         USE PTMAP               ! defines emissions file(s) PM mapping
         USE ADJ_ARRAY_MOD       !Added by mhrzmomeni 1.2019 for perturbation test flag and particle species         
         IMPLICIT NONE

C Includes:

         INCLUDE SUBST_AE_SPC    ! aerosol species table
         INCLUDE SUBST_GC_EMIS   ! gas chem emis surrogate names & map table
         INCLUDE SUBST_NR_EMIS   ! non-react emis surrogate names & map table
         INCLUDE SUBST_TR_EMIS   ! tracer emis surrogate names & map table
         INCLUDE SUBST_FILES_ID  ! file name parameters
         INCLUDE SUBST_IOPARMS   ! I/O parameters definitions
         INCLUDE SUBST_IOFDESC   ! file header data structure
         INCLUDE SUBST_IODECL    ! I/O definitions and declarations

C Arguments:

         INTEGER JDATE, JTIME
         INTEGER TSTEP( 2 )                 ! time step vector (HHMMSS)
         REAL    CONVPA             ! conversion factor to pressure in Pascals
         REAL    RDX3F( NLAYS )             ! reciprocal layer thickness
         REAL    RRHOJ( NCOLS,NROWS,NLAYS ) ! reciprocal density X Jacobian
         REAL    RJACM( NCOLS,NROWS,NLAYS ) ! reciprocal mid-layer Jacobian

C External Functions:

         INTEGER, EXTERNAL :: TRIMLEN

C Local Variables:

         REAL             CNVTC         ! combined conversion factor
         REAL             CNVTI         ! intermediate combined conv. factor
         REAL,    SAVE :: CNVTP         ! intermediate combined conv. factor
         REAL             DELT          ! interpolation factor
         INTEGER          C, R, L, N, S, V ! loop induction variables
         INTEGER :: I_EMIS !Added by mhrzmomeni 2.2019

         CHARACTER( 16 ) :: PNAME = 'GET_EMIS'
         CHARACTER( 120 ) :: XMSG = ' '
         INTEGER, SAVE :: LOGDEV
         LOGICAL, SAVE :: FIRSTIME = .TRUE.
         INTEGER          GXOFF, GYOFF         ! global origin offset from file
         INTEGER, SAVE :: STARTCOL, ENDCOL, STARTROW, ENDROW

!Added by mhrzmomeni 1.2019--------------------Start
         ! For finite difference perturbation 
         ! force perturbation of all cells
         !CHARACTER(32) :: PERTCOLS = 'PERTCOLS'
         !CHARACTER(32) :: PERTROWS = 'PERTROWS'
         
         !CHARACTER(32) :: PERTLEVS = 'PERTLEVS'   !Edited by mhrzmomeni 1.2019 for particle species
         !CHARACTER(32) :: PERTSPCS = 'PERTSPCS'   !Edited by mhrzmomeni 1.2019 for particle species
         !CHARACTER(32) :: PERTTIME = 'PERTTIME'   !Edited by mhrzmomeni 1.2019 for particle species
         !CHARACTER(32) :: PERTDELT = 'PERTDELT'   !Edited by mhrzmomeni 1.2019 for particle species
   
         ! force perturbation of all cells
         !INTEGER, ALLOCATABLE, SAVE :: PERTI ( : )    ! columns to perturb
         !INTEGER, ALLOCATABLE, SAVE :: PERTJ ( : )    ! rows to perturb

         !INTEGER, SAVE :: PERTL          ! layer to perturb    !Edited by mhrzmomeni 1.2019 for particle species
         !INTEGER, SAVE :: PERTV          ! species to perturb  !Edited by mhrzmomeni 1.2019 for particle species     
         !INTEGER, SAVE :: PERTT          ! time to perturb     !Edited by mhrzmomeni 1.2019 for particle species 
         !INTEGER, SAVE :: PERTDATE       ! date to perturb  !Edited by mhrzmomeni 1.2019 for particle species 
         !REAL, SAVE    :: PERTD   ! multiplicative perturbation !Edited by mhrzmomeni 1.2019 for particle species
         INTEGER, EXTERNAL :: SEC2TIME, TIME2SEC 
         
         CHARACTER( 16 ) :: V_LIST( 1 )
         CHARACTER( 80 ) :: VARDESC                ! env variable description
         INTEGER  STATUS                           ! ENV... status

         INTEGER :: NV = 1
       
         REAL, EXTERNAL    :: ENVREAL
         INTEGER, EXTERNAL :: ENVINT
         LOGICAL, EXTERNAL :: ENVYN
         INTEGER      ALLOCSTAT

         INTERFACE
            SUBROUTINE GET_ENVLIST ( ENV_VAR, NVARS, VAL_LIST )
               IMPLICIT NONE
               CHARACTER( * ),  INTENT ( IN )  :: ENV_VAR
               INTEGER,         INTENT ( OUT ) :: NVARS
               CHARACTER( 16 ), INTENT ( OUT ) :: VAL_LIST( : )
            END SUBROUTINE GET_ENVLIST
         END INTERFACE
!mhrzmomeni 1.2019----------------------------End
C-----------------------------------------------------------------------

         IF ( FIRSTIME ) THEN
            FIRSTIME = .FALSE.
D           logdev = init3()
C Get domain decomp info from the emissions file
            CALL SUBHFILE ( EMIS_1, GXOFF, GYOFF, STARTCOL, ENDCOL, STARTROW, ENDROW )
            CNVTP = CONVPA * CNVTE

!Added by mhrzmomeni 1.2019--------------------Start
C    Retrieve the perturbation information
            FDMTOFFSET = TIME2SEC( TSTEP( 2 ) ) / 2 
            FDMTOFFSET = SEC2TIME( FDMTOFFSET ) 
   
C Read number of layers to be forced (3.2018.slc)
            PERTL = 1          ! default
            VARDESC = 'Layer of perturbation'
            PERTL = ENVINT(PERTLEVS, VARDESC, PERTL, STATUS)
            IF ( STATUS /= 0 ) WRITE(LOGDEV, '(5X, A)') VARDESC
            IF ( STATUS == 1 ) THEN
               XMSG = 'Environment variable improperly formatted for ' // trim(PERTLEVS)
               CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT2)
            END IF

            !Added by mhrzmomeni 2.2019-----------------Start
            !Read PERTEMIS from the run script and specify PERTEMIS whether is
            !gas species, or Particle, or non-reactive species or tracer
            CALL GET_ENVLIST (PERTEMIS, N_PERTE, PERTE)
            IF (N_PERTE /= 1) THEN
                XMSG = 'Environment variable error for ' // trim(PERTEMIS) // ', the number of input value  must be 1'
                CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT3 )
            END IF

            PERTPM = .FALSE.
            PERTGC = .FALSE.
            PERTNR = .FALSE.
            PERTTR = .FALSE.

!            DO I_EMIS = 1, 6
!                IF(PM_EMIS(I_EMIS) == PERTE(1)) THEN
!                    PERTPM = .TRUE.
!                    PERTV  = I_EMIS
!                    EXIT
!                END IF
!            END DO

            IF (.NOT. PERTPM) THEN
                DO I_EMIS = 1, N_GC_EMIS
                    IF (GC_EMIS(I_EMIS) == PERTE(1)) THEN
                        PERTGC = .TRUE.
                        PERTV  = I_EMIS
                        EXIT
                    END IF
                END DO
            ENDIF

            IF (.NOT. PERTPM .AND. .NOT. PERTGC) THEN
                DO I_EMIS = 1, N_NR_EMIS
                    IF (NR_EMIS(I_EMIS) == PERTE(1)) THEN
                        PERTNR = .TRUE.
                        PERTV  = I_EMIS
                        EXIT
                    END IF
                END DO
            ENDIF

            IF (.NOT. PERTPM .AND. .NOT. PERTGC .AND. .NOT. PERTNR) THEN
                DO I_EMIS = 1, N_TR_EMIS
                    IF (TR_EMIS(I_EMIS) == PERTE(1)) THEN
                        PERTTR = .TRUE.
                        PERTV  = I_EMIS
                        EXIT
                    END IF
                END DO
            ENDIF

            IF (.NOT. PERTPM .AND. .NOT. PERTGC .AND. .NOT. PERTNR .AND. .NOT. PERTTR) THEN
                XMSG = 'Environment variable error for ' // PERTEMIS // ', the variable name is not valid'
                CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT3 )
            ENDIF
            !mhrzmomeni 2.2019--------------------------End

            !Edited by mhrzmomeni 2.2019-----------------Start
            !Forward model can read the pertured emission from the run script by string name, 
            !so model no longer needs to know the pertured emission is particle or not
            !Added by mhrzmomeni 1.2019 for particle species ---------------Start
            !Determin whether species are particle or gas
            !PERTP = .FALSE.          ! default 
            !VARDESC = 'Whether species are particle or gas'
            !PERTP = ENVYN(PERTPART, VARDESC, PERTP, STATUS)
            !IF ( STATUS /= 0 ) WRITE(LOGDEV, '(5X, A)') VARDESC
            !IF ( STATUS == 1 ) THEN
            !   XMSG = 'Environment variable for PERTPART improperly formatted'
            !   CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT2)
            !END IF
            !mhrzmomeni 1.2019 for particle species ------------------------End
             
            !Forward model can read PERTSPCS (which this name was changed to PERTEMIS) from 
            !the run script as a string name, so the model no longer needs to read PERTSPCS 
            !as an integer number
            !PERTV = 1          ! default
            !VARDESC = 'Layer of perturbation'
            !PERTV = ENVINT(PERTSPCS, VARDESC, PERTV, STATUS)
            !IF ( STATUS /= 0 ) WRITE(LOGDEV, '(5X, A)') VARDESC
            !IF ( STATUS == 1 ) THEN
            !   XMSG = 'Environment variable improperly formatted'
            !   CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT2)
            !END IF
            !mhrzmomeni 2.2019--------------------------End

            PERTT = 1          ! default
            VARDESC = 'Time of perturbation'
            PERTT = ENVINT(PERTTIME, VARDESC, PERTT, STATUS)
            IF ( STATUS /= 0 ) WRITE(LOGDEV, '(5X, A)') VARDESC
            IF ( STATUS == 1 ) THEN
               XMSG = 'Environment variable improperly formatted'
               CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT2)
            END IF
                     
            PERTD = 0.0            ! default
            VARDESC = 'finite difference perturbation size'
            PERTD = ENVREAL(PERTDELT, VARDESC, PERTD, STATUS)
            IF ( STATUS /= 0 ) WRITE( LOGDEV, '(5X, A)' ) VARDESC
            IF ( STATUS == 1 ) THEN
               XMSG = 'Environment variable improperly formatted'
               CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT2)
            END IF

        END IF
!mhrzmomeni 1.2019--------------------------End

C read & interpolate emissions (create VDEMIS in the species class order)

         VDEMIS = 0.0   ! array assignment

         DO V = STRT_GC, FINI_GC
            S = V + 1 - STRT_GC
            BUFF = 0.0   ! array assignment
C                                       vvvvvvv - emis surrogate names
            IF ( .NOT. INTERPX( EMIS_1, GC_EMIS( S ), PNAME,
     &                          STARTCOL,ENDCOL, STARTROW,ENDROW, 1,EMLYRS,
     &                          JDATE, JTIME, BUFF ) ) THEN
               XMSG = 'Could not read  '
     &              // GC_EMIS( S )( 1:TRIMLEN( GC_EMIS( S ) ) )
     &              // ' from ' // EMIS_1
!              CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
               CALL M3WARN( PNAME, JDATE, JTIME, XMSG )
            END IF
            CNVTI = CNVTP * GC_EMIS_FAC( S )

C reactive gases (conversion to ppmv/s) VDEMIS in this order from RDEMIS
C "Stores read an entire cache line, modify the target, then write back the
C  entire line. Thus, non-consecutive stores are worse than non-consecutive
C  loads."

            DO R = 1, MY_NROWS
               DO C = 1, MY_NCOLS
                  DO L = 1, EMLYRS
                     CNVTC = CNVTI * RDX3F( L ) * RRHOJ( C,R,L )
                     !Added by mhrzmomeni 2.2019--------------------Start
                     !apply perturbation only for gas, added PERTGC in onder to force gaseous perturbation
                     IF ( FDMTEST .AND. PERTT .EQ. JTIME .AND. V.EQ.PERTV .AND. 
     &                    L.EQ.PERTL .AND. PERTGC) THEN 
                         VDEMIS( V,L,C,R ) = VDEMIS( V,L,C,R )
     &                                 + CNVTC * BUFF( C,R,L )*(1.+PERTD) !Edited by mhrzmomeni 1.2019 [Added (1+PERTD)] for gas species 
                     ELSE
                         VDEMIS( V,L,C,R ) = VDEMIS( V,L,C,R )
     &                                  + CNVTC * BUFF( C,R,L )
                     END IF
                     !mhrzmomeni 2.2019-----------------------------End
                  END DO
               END DO
            END DO

D           write( logdev,* ) '  GC EMIS: ', s, '  ', gc_emis( s )

         END DO   ! V

C beis

         IF ( BIOGEMIS ) THEN

            CALL GET_BEIS ( JDATE, JTIME, TSTEP )

C tmpbeis312 is based on hourly input - need to interpolate return value
C merge: VDEMIS_BI in mol/hr. Convert to ppm/sec

            L = 1
            CNVTI = CONVPA * CNVTE * RDX3F( L )  ! per sec
            DO R = 1, MY_NROWS
               DO C = 1, MY_NCOLS
                  CNVTC = CNVTI * RRHOJ( C,R,L )
                  N = 0
                  DO S = 1, MSPCS
                     V = BEIS_MAP( S )
                     IF ( V .GT. 0 ) THEN
                        N = N + 1
                        VDEMIS( V,L,C,R ) = VDEMIS( V,L,C,R )
     &                                    + CNVTC * VDEMIS_BI( N,C,R )
                      END IF
                  END DO
               END DO
            END DO

         END IF

C plume rise

         IF ( PT3DEMIS ) THEN

            CALL GET_PT3D_EMIS ( JDATE, JTIME, TSTEP )

C merge: VDEMIS_PT in mol/sec. Convert to ppm/sec
C If aerosols, then the 6 PM emissions obtained from GET_PT3D_EMIS need to be
C accessed by GET_AERO_EMIS to be "speciated" and merged with the 27 AE emissions.

            DO R = 1, MY_NROWS
               DO C = 1, MY_NCOLS
                  DO L = 1, EMLAYS
                     CNVTC = CNVTP * RDX3F( L ) * RRHOJ( C,R,L )
                     DO S = 1, N_SPC_PTEM
                        V = PTEM_MAP( S )  ! <- pointer to non-PM (non-aerosol) species
                        VDEMIS( V,L,C,R ) = VDEMIS( V,L,C,R )
     &                                    + CNVTC * VDEMIS_PT( C,R,L,S )
                     END DO
                  END DO
               END DO
            END DO

         END IF

C aerosol emissions - all units conversions done in GET_AERO_EMIS for aerosols
C GET_AERO_EMIS in f90 module AERO_EMIS

!!!         IF ( N_AE_SPC .GT. 0 ) THEN
!!!            CALL GET_AERO_EMIS ( JDATE, JTIME, TSTEP, EMLAYS, RJACM,
!!!     &                           VDEMIS, VDEMIS_AE )

!!!            DO R = 1, MY_NROWS
!!!               DO C = 1, MY_NCOLS
!!!                  DO L = 1, EMLAYS
!!!                     DO V = STRT_AE, FINI_AE
!!!                        S = V + 1 - STRT_AE
!!!                        VDEMIS( V,L,C,R ) = VDEMIS( V,L,C,R )
!!!     &                                    + VDEMIS_AE( S,L,C,R )
!!!                     END DO
!!!                  END DO
!!!               END DO
!!!            END DO

!!!         END IF

C non-reactive gases (conversion to ppmv/s) VDEMIS in this order from RDEMIS
         DO V = STRT_NR, FINI_NR
            S = V + 1 - STRT_NR
            BUFF = 0.0   ! array assignment
C                                       vvvvvvv - emis surrogate names
            IF ( .NOT. INTERPX( EMIS_1, NR_EMIS( S ), PNAME,
     &                          STARTCOL,ENDCOL, STARTROW,ENDROW, 1,EMLYRS,
     &                          JDATE, JTIME, BUFF ) ) THEN
               XMSG = 'Could not read  '
     &              // NR_EMIS( S )( 1:TRIMLEN( NR_EMIS( S ) ) )
     &              // ' from ' // EMIS_1
               CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
            END IF
            CNVTI = CNVTP * NR_EMIS_FAC( S )

            DO R = 1, MY_NROWS
               DO C = 1, MY_NCOLS
                  DO L = 1, EMLYRS
                      CNVTC = CNVTI * RDX3F( L ) * RRHOJ( C,R,L )
                      !Added by mhrzmomeni 2.2019--------------------Start
                      !apply perturbation only for non-react, added PERTNR in
                      !onder to force non-reactive perturbation
                      IF ( FDMTEST .AND. PERTT .EQ. JTIME .AND. S.EQ.PERTV .AND.
     &                    L.EQ.PERTL .AND. PERTNR) THEN
                         !Edited by mhrzmomeni 2.2019 [Added (1+PERTD)] for
                         !non-reactive species
                         VDEMIS( V,L,C,R ) = VDEMIS( V,L,C,R )
     &                                 + CNVTC * BUFF( C,R,L )*(1.+PERTD) 
                      ELSE
                          VDEMIS( V,L,C,R ) = VDEMIS( V,L,C,R )
     &                                 + CNVTC * BUFF( C,R,L )
                      ENDIF
                      !mhrzmomeni 2.2019-----------------------------End
                  END DO
               END DO
            END DO

D           write( logdev,* ) '  NR EMIS: ', s, '  ', nr_emis( s )

         END DO

C tracer gases (conversion to ppmv/s)

         IF ( EM_TRAC ) THEN

            DO V = STRT_TR, FINI_TR
               S = V + 1 - STRT_TR
               BUFF = 0.0   ! array assignment
C                                               vvvvvvv - emis surrogate names
               IF ( .NOT. INTERPX( EMIS_TRAC_1, TR_EMIS( S ), PNAME,
     &                             STARTCOL,ENDCOL, STARTROW,ENDROW, 1,EMLYRS,
     &                             JDATE, JTIME, BUFF ) ) THEN
                  XMSG = 'Could not read  '
     &                 // TR_EMIS( S )( 1:TRIMLEN( TR_EMIS( S ) ) )
     &                 // ' from ' // EMIS_TRAC_1
                  CALL M3EXIT( PNAME, JDATE, JTIME, XMSG, XSTAT1 )
               END IF
               CNVTI = CNVTP * TR_EMIS_FAC( S )

               DO R = 1, MY_NROWS
                  DO C = 1, MY_NCOLS
                     DO L = 1, EMLYRS
                         CNVTC = CNVTI * RDX3F( L ) * RRHOJ( C,R,L )
                         !Added by mhrzmomeni 2.2019--------------------Start
                         !apply perturbation only for tracer, added PERTNR in
                         !onder to force tracer perturbation
                         IF ( FDMTEST .AND. PERTT .EQ. JTIME .AND. S.EQ.PERTV .AND.
     &                        L.EQ.PERTL .AND. PERTTR) THEN
                             !Edited by mhrzmomeni 2.2019 [Added (1+PERTD)] for
                             !tracer species
                             VDEMIS( V,L,C,R ) = CNVTC * BUFF( C,R,L)*(1.+PERTD)
                         ELSE
                             VDEMIS( V,L,C,R ) = CNVTC * BUFF( C,R,L )
                         ENDIF
                         !mhrzmomeni 2.2019-----------------------------End
                     END DO
                  END DO
               END DO

D              write( logdev,* ) '  TR EMIS: ', s, '  ', tr_emis( s )

            END DO

         END IF

C zero out emissions values for species not included in diffused list ...
C accounts for emissions species names as a subset of the vert. diffused species list

        VDEMIS( N_SPC_EMIS+1,:,:,: ) = 0.0

        END SUBROUTINE GET_EMIS

      END MODULE EMIS_DEFN
