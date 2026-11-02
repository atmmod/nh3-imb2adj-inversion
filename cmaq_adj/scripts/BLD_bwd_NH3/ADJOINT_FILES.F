C:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

      MODULE ADJOINT_FILES
C-----------------------------------------------------------------------
C Function:
C   Define adjoint file functions

C Revision History:
C   Aug 2007 by Peter Percell at UH-IMAQS: created for adjoint/4dvar
C   Oct 2010 J.Resler ICS: checkpoint files moved to CHK_FILES module
C   Feb 2011 by Peter Percell at UH-IMAQS: removed unneeded code
C   May 2013 by Peter Percell at UH-IMAQS:
C   - the adjoint file implementation here uses IOAPI3 tools, so a constant
C     output step is required
C   Aug 2013 by Peter Percell at UH-IMAQS:
C   - made the LGRID output frequency selectable by user
C-----------------------------------------------------------------------

      IMPLICIT NONE
      SAVE

C-----------------------------------
C Data
C-----------------------------------

C Parameters
      CHARACTER(16), PARAMETER :: CTM_XFIRST_IN   = 'CTM_XFIRST_IN'
      CHARACTER(16), PARAMETER :: CTM_XFIRST_OUT  = 'CTM_XFIRST_OUT'

      CHARACTER(16), PARAMETER :: CTM_CONC_FWD    = 'CTM_CONC_FWD'
      CHARACTER(16), PARAMETER :: INIT_LGRID_1    = 'INIT_LGRID_1'
      CHARACTER(16), PARAMETER :: ADJ_LGRID       = 'ADJ_LGRID'
      !CHARACTER(16), PARAMETER :: ADJ_FORCE       = 'ADJ_FORCE' ! duplicative declaration from FILES_CTM.EXT !Edited by mhrzmomeni 1.2019
      CHARACTER(16), PARAMETER :: ADJ_LGRID_EM    = 'ADJ_LGRID_EM'
      CHARACTER(16), PARAMETER :: ADJNLAYS_FRC = 'ADJNLAYS_FRC' ! env. var. number of layers forced
      CHARACTER(16), PARAMETER :: ADJNSPC_FRC = 'ADJNSPC_FRC' ! env. var. index of variable forced !cl3293

      CHARACTER(16) :: LGRID_OUTPUT_FREQ
      !Added by mhrzmomeni 1.2019------------------Start
      INTEGER, EXTERNAL :: ENVINT 
      INTEGER :: STATUS         ! ENVINT or ENVREAL status
      CHARACTER(80) :: VARDESC  ! environment variable description

      INTEGER, SAVE     :: NLAYS_FRC 
      INTEGER, SAVE     :: NSPC_FRC 
      INTEGER           :: ALLOCSTAT
      !mhrzmomeni 1.2019---------------------------End
C$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

      CONTAINS

C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
C Create new adjoint file
C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
      SUBROUTINE OP_ADJ_FILE(JDATE, JTIME, TSTEP, ADJ_FILE)

      USE GRID_CONF             ! horizontal & vertical domain specifications
      USE CHK_FILES_DEFS        ! adjoint checkpoint files definition
      USE PMEM_DEFN, only: N_EMIS_PM !slz
      USE EMIS_DEFN, ONLY: EMLAYS

      IMPLICIT NONE

C Include Files:
      INCLUDE SUBST_GC_SPC      ! gas chemistry species table
      INCLUDE SUBST_AE_SPC      ! aerosol species table
      INCLUDE SUBST_NR_SPC      ! non-reactive species table
      INCLUDE SUBST_TR_SPC      ! tracer species table
      INCLUDE SUBST_GC_EMIS     ! gas chem diffusion species and map table
      INCLUDE SUBST_AE_EMIS     ! aerosol diffusion species and map table
      INCLUDE SUBST_NR_EMIS     ! non-react diffusion species and map table
      INCLUDE SUBST_TR_EMIS     ! tracer diffusion species and map table
      INCLUDE SUBST_IOPARMS     ! I/O parameters definitions
      INCLUDE SUBST_IODECL      ! I/O definitions and declarations
      INCLUDE SUBST_IOFDESC     ! file header data structure
      INCLUDE SUBST_FILES_ID    ! file name parameters

C Parameters:

C Arguments:
      INTEGER, INTENT(IN) :: JDATE ! starting date (YYYYDDD)
      INTEGER, INTENT(IN) :: JTIME ! starting time (HHMMSS)
      INTEGER, INTENT(IN) :: TSTEP(2) ! time step vector (HHMMSS)
                                !   TSTEP(1) = local output step
                                !   TSTEP(2) = sciproc sync. step (chem)
      CHARACTER(16), INTENT(IN) :: ADJ_FILE

C Local Variables:
      INTEGER, SAVE :: LOGDEV   ! FORTRAN unit number for log file

      CHARACTER(16) :: PNAME = 'OP_ADJ_FILE'
      CHARACTER(96) :: XMSG = ' '

      !CHARACTER(80) :: VARDESC  ! environment variable description !Edited mhrzmomeni 1.2019

      !INTEGER :: STATUS     !Edited mhrzmomeni 1.2019

      INTEGER :: K, S           ! loop counters

      CHARACTER( 16 ) :: PM_EMIS( N_EMIS_PM ) !slz

C-----------------------------------------------------------------------

      LOGDEV = INIT3()

      VARDESC =
     &     'LGRID output frequency: SYNC_STEP, OUTPUT_STEP or ONCE (at start time)'
      LGRID_OUTPUT_FREQ = 'OUTPUT_STEP'
      CALL ENVSTR('ADJ_LGRID_FREQ', VARDESC, LGRID_OUTPUT_FREQ,
     &     LGRID_OUTPUT_FREQ, STATUS)
      IF ( STATUS /= 0 ) WRITE(LOGDEV, '(5X, A)') VARDESC
      IF ( STATUS == 1 ) THEN
         XMSG = 'Environment variable improperly formatted'
         CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT3)
      ELSE IF ( STATUS == -1 ) THEN
         XMSG = 'Environment variable set, but empty ... Using default'
         WRITE(LOGDEV, '(5X, A)') XMSG
      ELSE IF ( STATUS == -2 ) THEN
         XMSG = 'Environment variable not set ... Using default'
         WRITE(LOGDEV, '(5X, A)') XMSG
      END IF

      IF ( TRIM(LGRID_OUTPUT_FREQ) /= 'SYNC_STEP' .AND.
     &     TRIM(LGRID_OUTPUT_FREQ) /= 'OUTPUT_STEP' .AND.
     &     TRIM(LGRID_OUTPUT_FREQ) /= 'ONCE' ) THEN
         WRITE(LOGDEV, '(5X, A)')
     &        'ADJ_LGRID_FREQ was set to ' // LGRID_OUTPUT_FREQ
         XMSG = 'It must be SYNC_STEP, OUTPUT_STEP or ONCE'
         CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT3)
      END IF

      IF ( .NOT. CONST_SYNC_STEP .AND.
     &     TRIM(LGRID_OUTPUT_FREQ) == 'SYNC_STEP' ) THEN
         XMSG = 'ADJ_LGRID_FREQ cannot be SYNC_STEP ... Using OUTPUT_STEP'
         CALL M3WARN(PNAME, JDATE, JTIME, XMSG)
         LGRID_OUTPUT_FREQ = 'OUTPUT_STEP'
      END IF

      IF ( MYPE == 0 ) THEN

!         IF ( ADJ_FILE == ADJ_LGRID ) THEN

C Get file characteristics of CTM_CONC_FWD
            IF ( .NOT. OPEN3(CTM_CONC_FWD, FSREAD3, PNAME) ) THEN
               XMSG = 'Could not open ' // TRIM(CTM_CONC_FWD) //
     &              ' file as OLD:READ-ONLY'
               CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)
            END IF

            IF ( .NOT. DESC3(CTM_CONC_FWD) ) THEN
               XMSG = 'Could not get ' // TRIM(CTM_CONC_FWD) // ' file description'
               CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)
            END IF

            IF ( .NOT. CLOSE3(CTM_CONC_FWD) ) THEN
               XMSG = 'Could not close ' // TRIM(CTM_CONC_FWD)
               CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)
            END IF

!         ELSE
!
!C Get file characteristics of CTM_CONC_1
!            IF ( .NOT. OPEN3(CTM_CONC_1, FSREAD3, PNAME) ) THEN
!               XMSG = 'Could not open ' // TRIM(CTM_CONC_1) //
!     &              ' file as OLD:READ-ONLY'
!               CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)
!            END IF
!
!            IF ( .NOT. DESC3(CTM_CONC_1) ) THEN
!               XMSG = 'Could not get ' // TRIM(CTM_CONC_1) // ' file description'
!               CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)
!            END IF
!
!            IF ( .NOT. CLOSE3(CTM_CONC_1) ) THEN
!               XMSG = 'Could not close ' // TRIM(CTM_CONC_1)
!               CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)
!            END IF
!
!         END IF

C Set file characteristics that differ from the base file, CTM_CONC_FWD or
C CTM_CONC_1
         SELECT CASE ( ADJ_FILE )

         CASE ( ADJ_LGRID )

            IF ( TRIM(LGRID_OUTPUT_FREQ) == 'SYNC_STEP' ) THEN
               TSTEP3D = TSTEP(2) ! sync step
            ELSE IF ( TRIM(LGRID_OUTPUT_FREQ) == 'OUTPUT_STEP' ) THEN
               TSTEP3D = TSTEP(1) ! output step
            ELSE
               TSTEP3D = 0      ! make it a time-independent file
            END IF

            FDESC3D(1) = 'Sensitivity output'
            FDESC3D(2) = 'From CMAQ model dyn alloc version CTM'
            DO K = 3, MXDESC3
               FDESC3D(K) = ' '
            END DO

            NLAYS3D = NLAYS
            NVARS3D = 0

C Note: "CF" stands for "cost function units"
            DO S = 1, N_GC_SPC
               NVARS3D = NVARS3D + 1
               VTYPE3D(NVARS3D) = M3REAL
               VNAME3D(NVARS3D) = GC_SPC(S)
               UNITS3D(NVARS3D) = 'CF/ppmV'
               VDESC3D(NVARS3D) = 'Sensitivity of cost function to ' //
     &              TRIM(VNAME3D(NVARS3D))
            END DO

            NVARS3D = NVARS3D + 1
            VTYPE3D(NVARS3D) = M3REAL
            VNAME3D(NVARS3D) = 'RHOJ'
            UNITS3D(NVARS3D) = 'CF/m*kg/m**3'
            VDESC3D(NVARS3D) = 'Sensitivity of cost function to ' //
     &           TRIM(VNAME3D(NVARS3D))

            DO S = 1, N_AE_SPC
               NVARS3D = NVARS3D + 1
               VTYPE3D(NVARS3D) = M3REAL
               VNAME3D(NVARS3D) = AE_SPC(S)
               IF ( VNAME3D(NVARS3D)(1:3) == 'NUM' ) THEN
                  UNITS3D(NVARS3D) = 'CF/number/m**3'
               ELSE IF ( VNAME3D(NVARS3D)(1:3) == 'SRF' ) THEN
                  UNITS3D(NVARS3D) = 'CF/m**2/m**3'
               ELSE
                  UNITS3D(NVARS3D) = 'CF/microg/m**3'
               END IF
               VDESC3D(NVARS3D) = 'Sensitivity of cost function to ' //
     &              TRIM(VNAME3D(NVARS3D))
            END DO

            DO S = 1, N_NR_SPC
               NVARS3D = NVARS3D + 1
               VTYPE3D(NVARS3D) = M3REAL
               VNAME3D(NVARS3D) = NR_SPC(S)
               UNITS3D(NVARS3D) = 'CF/ppmV'
               VDESC3D(NVARS3D) = 'Sensitivity of cost function to ' //
     &              TRIM(VNAME3D(NVARS3D))
            END DO

            DO S = 1, N_TR_SPC
               NVARS3D = NVARS3D + 1
               VTYPE3D(NVARS3D) = M3REAL
               VNAME3D(NVARS3D) = TR_SPC(S)
               UNITS3D(NVARS3D) = 'CF/ppmV'
               VDESC3D(NVARS3D) = 'Sensitivity of cost function to ' //
     &              TRIM(VNAME3D(NVARS3D))
            END DO

         CASE ( ADJ_LGRID_EM )

            TSTEP3D = TSTEP(1)  ! output step

            FDESC3D(1) = 'Sensitivity output wrt emissions'
            FDESC3D(2) = 'From CMAQ model dyn alloc version CTM'
            DO K = 3, MXDESC3
               FDESC3D(K) = ' '
            END DO

            NLAYS3D = EMLAYS !slz defined in PCGRID
            NVARS3D = 0

            IF ( TRIM(LGRID_OUTPUT_FREQ) == 'SYNC_STEP' ) THEN
               TSTEP3D = TSTEP(2) ! sync step
            ELSE IF ( TRIM(LGRID_OUTPUT_FREQ) == 'OUTPUT_STEP' ) THEN
               TSTEP3D = TSTEP(1) ! output step
            ELSE
               TSTEP3D = 0      ! make it a time-independent file
            END IF

C Note: "CF" stands for "cost function units"
!slz sens to emitted species
!
!slz emitted PM species
            !Added mhrzmomeni 1.2019---------------------Start
!            IF(N_AE_SPC.GT.0) THEN
!               PM_EMIS(1)="POC"
!               PM_EMIS(2)="PSO4"
!               PM_EMIS(3)="PNO3"
!               PM_EMIS(4)="PEC"
!               PM_EMIS(5)="PMFINE"
!               PM_EMIS(6)="PMC" !slz could be tricky; check PMEM_DEFN
!               DO S = 1, N_EMIS_PM
!                  NVARS3D = NVARS3D + 1
!                  VTYPE3D(NVARS3D) = M3REAL
!                  VNAME3D(NVARS3D) = PM_EMIS(S)
!                  UNITS3D(NVARS3D) = 'CF/(g/s)'
!                  VDESC3D(NVARS3D) = 
!!!     &                 'Sensitivity of cost function to emissions of ' //
!!!     &                 TRIM(VNAME3D(NVARS3D))
!               END DO
!            END IF
            !mhrzmomeni 1.2019---------------------------End

            DO S = 1, N_GC_EMIS
               NVARS3D = NVARS3D + 1
               VTYPE3D(NVARS3D) = M3REAL
               VNAME3D(NVARS3D) = GC_EMIS(S)
               UNITS3D(NVARS3D) = 'CF/(mol/s)'
               VDESC3D(NVARS3D) = 
     &              'Sensitivity of cost function to emissions of ' //
     &              TRIM(VNAME3D(NVARS3D))
            END DO

!        Ammonia and semi-volatile compounds
            DO S = 1, N_NR_EMIS
               NVARS3D = NVARS3D + 1
               VTYPE3D(NVARS3D) = M3REAL
               VNAME3D(NVARS3D) = NR_EMIS(S)
               UNITS3D(NVARS3D) = 'CF/(mol/s)'
               VDESC3D(NVARS3D) = 
     &              'Sensitivity of cost function to emissions of ' //
     &              TRIM(VNAME3D(NVARS3D))
            END DO

!        Tracer species - slc.7.2014
            DO S = 1, N_TR_EMIS
               NVARS3D = NVARS3D + 1
               VTYPE3D(NVARS3D) = M3REAL
               VNAME3D(NVARS3D) = TR_EMIS(S)
               UNITS3D(NVARS3D) = 'CF/(mol/s)'
               VDESC3D(NVARS3D) = 
     &              'Sensitivity of cost function to emissions of ' //
     &              TRIM(VNAME3D(NVARS3D))
            END DO

         CASE DEFAULT

            XMSG =  '"' // TRIM(ADJ_FILE) // '"' //
     &           ' is not a valid file selection'
            CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT3)

         END SELECT

C Create new file
         IF ( .NOT. OPEN3(ADJ_FILE, FSCREA3, PNAME) ) THEN
            XMSG = 'Could not create ' // TRIM(ADJ_FILE) // ' file'
            CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)
         END IF
        
      END IF                    ! MYPE == 0

      END SUBROUTINE OP_ADJ_FILE

C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
C close adjoint file
C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
      SUBROUTINE CLOSE_ADJ_FILE(JDATE, JTIME, ADJ_FILE)

      IMPLICIT NONE

      INCLUDE SUBST_IOPARMS
      INCLUDE SUBST_IOFDESC
      INCLUDE SUBST_IODECL

      CHARACTER(16), INTENT(IN) :: ADJ_FILE
      INTEGER, INTENT(IN) :: JDATE ! YYYYDDD
      INTEGER, INTENT(IN) :: JTIME ! HHMMSS

C Local Variables:

      CHARACTER(16) :: PNAME = 'CLOSE_ADJ_FILE'
      CHARACTER(96) :: XMSG = ' '

C-----------------------------------------------------------------------

       IF ( .NOT. CLOSE3(ADJ_FILE) ) THEN
          XMSG = 'Could not close ' // TRIM(ADJ_FILE)
          CALL M3WARN(PNAME, JDATE, JTIME, XMSG)
       END IF

      END SUBROUTINE CLOSE_ADJ_FILE

C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
C Write to an adjoint file
C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
      SUBROUTINE WR_ADJ_FILE(ARRAY, JDATE, JTIME, ADJ_FILE)

      IMPLICIT NONE

C Include Files:
      INCLUDE SUBST_IOPARMS     ! I/O parameters definitions
#include      SUBST_IODECL      ! I/O definitions and declarations

C Arguments:
      REAL, INTENT(IN) :: ARRAY(*)
      INTEGER, INTENT(IN) :: JDATE ! current model date, coded YYYYDDD
      INTEGER, INTENT(IN) :: JTIME ! current model time, coded HHMMSS
      CHARACTER(16), INTENT(IN) :: ADJ_FILE

C Local variables:
      LOGICAL, SAVE :: FIRSTIME = .TRUE.
      INTEGER, SAVE :: LOGDEV

      CHARACTER(16) :: PNAME = 'WR_ADJ_FILE'
      CHARACTER(96) :: XMSG = ' '

C-----------------------------------------------------------------------

      IF ( FIRSTIME ) THEN
         FIRSTIME = .FALSE.
         LOGDEV = INIT3()
      END IF

      IF ( .NOT. WRITE3(ADJ_FILE, ALLVAR3, JDATE, JTIME, ARRAY) ) THEN
         XMSG = 'Could not write to ' // TRIM(ADJ_FILE)
         CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)
      END IF

      WRITE(LOGDEV, '(/5X, 3(A, :, 1X), I8, ":", I6.6)')
     &     'Timestep written to', ADJ_FILE,
     &     'for date and time', JDATE, JTIME

      END SUBROUTINE WR_ADJ_FILE

C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
C Read from an adjoint file
C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
      SUBROUTINE RD_ADJ_FILE(ARRAY, JDATE, JTIME, ADJ_FILE)

      USE GRID_CONF             ! horizontal & vertical domain specifications

      IMPLICIT NONE

C Include Files:
      INCLUDE SUBST_IOPARMS     ! I/O parameters definitions
      INCLUDE SUBST_IODECL      ! I/O definitions and declarations
      INCLUDE SUBST_IOFDESC     ! file header data structure

C Arguments:
      REAL, INTENT(OUT) :: ARRAY(*)
      INTEGER, INTENT(IN) :: JDATE ! current model date, coded YYYYDDD
      INTEGER, INTENT(IN) :: JTIME ! current model time, coded HHMMSS
      CHARACTER(16), INTENT(IN) :: ADJ_FILE

C Local variables:
      LOGICAL, SAVE :: FIRSTIME = .TRUE.
      INTEGER, SAVE :: LOGDEV   ! unit number for log device !Added by mhrzmomeni 1.2019

      CHARACTER(16) :: PNAME = 'RD_ADJ_FILE'
      CHARACTER(96) :: XMSG = ' '

!      REAL :: BUFFER(1:NCOLS, 1:NROWS, 1:NLAYS)
      REAL, ALLOCATABLE :: BUFFER(:, :, :)  !Edited by mhrzmomeni 1.2019
      
      INTEGER, SAVE :: STRTCOL, ENDCOL, STRTROW, ENDROW ! local window in global domain

      INTEGER :: K, C, R, L, V  ! loop counters

C-----------------------------------------------------------------------

      IF ( FIRSTIME ) THEN
         FIRSTIME = .FALSE.
         ALLOCATE( BUFFER(1:NCOLS, 1:NROWS, 1:NLAYS), STAT=ALLOCSTAT ) !Added by mhrzmomeni 1.2019

C Get local window in global domain
         STRTCOL = COLSX_PE(1, MYPE+1)
         ENDCOL = STRTCOL + NCOLS - 1
         STRTROW = ROWSX_PE(1, MYPE+1)
         ENDROW = STRTROW + NROWS - 1
      END IF

C Get file characteristics of ADJ_FILE
      IF ( .NOT. DESC3(ADJ_FILE) ) THEN
         XMSG = 'Could not get ' // TRIM(ADJ_FILE) // ' file description'
         CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)
      END IF

      K = 0
      DO V = 1, NVARS3D
         IF ( .NOT. XTRACT3(ADJ_FILE, VNAME3D(V),
     &        1, NLAYS, STRTROW, ENDROW, STRTCOL, ENDCOL,
     &        JDATE, JTIME, BUFFER) ) THEN
            XMSG = 'Could not read  ' // VNAME3D(V)
     &           // ' from ' // TRIM(ADJ_FILE)
            CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)
         END IF

         DO L = 1, NLAYS
            DO R = 1, NROWS
               DO C = 1, NCOLS
                  K = K + 1
                  ARRAY(K) = BUFFER(C, R, L)
               END DO
            END DO
         END DO
      END DO

      END SUBROUTINE RD_ADJ_FILE


C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
C Read from an offline forcing file
C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
      SUBROUTINE RD_FORCE_FILE(ARRAY, JDATE, JTIME) !, ADJ_FORCE)

      USE CGRID_SPCS            ! CGRID species number and offsets
      USE GRID_CONF             ! horizontal & vertical domain specifications
      !USE CGRID_SPCS, ONLY: NSPCSD !Added by mhrzmomeni 2.2019

      IMPLICIT NONE

C Include Files:
      INCLUDE SUBST_IOPARMS     ! I/O parameters definitions
      INCLUDE SUBST_IODECL      ! I/O definitions and declarations
      INCLUDE SUBST_IOFDESC     ! file header data structure
      INCLUDE SUBST_FILES_ID    ! file name parameters
      INCLUDE SUBST_GC_SPC      ! gas chemistry species table
      INCLUDE SUBST_AE_SPC      ! aerosol species table
      INCLUDE SUBST_NR_SPC      ! non-reactive species table
      INCLUDE SUBST_TR_SPC      ! tracer species table

C Arguments:

      !INTEGER, PARAMETER :: NLAYS_FRC = 1 !Edited by mhrzmomeni 1.2019

      REAL, INTENT(INOUT) :: ARRAY(:,:,:,:)
      INTEGER, INTENT(IN) :: JDATE ! current model date, coded YYYYDDD
      INTEGER, INTENT(IN) :: JTIME ! current model time, coded HHMMSS
!      CHARACTER(16), INTENT(IN) :: ADJ_FORCE

C Local variables:
      LOGICAL, SAVE :: FIRSTIME_FRC = .TRUE.
      INTEGER, SAVE :: LOGDEV   ! unit number for log device !Added by mhrzmomeni 1.2019

      CHARACTER(16) :: PNAME = 'RD_FORCE_FILE'
      CHARACTER(96) :: XMSG = ' '
      CHARACTER(16) :: ADJNLAYS_FRC = 'ADJNLAYS_FRC' ! env. var. max sync step !Added by mhrzmomeni 1.2019
      CHARACTER(16) :: ADJNSPC_FRC = 'ADJNSPC_FRC' ! env. var. max sync step   !Added by mhrzmomeni 1.2019

      REAL :: BUFFER(1:NCOLS, 1:NROWS, 1:NLAYS_FRC)
!      REAL :: BUFFER(1:NCOLS, 1:NROWS)

      INTEGER :: STRTCOL, ENDCOL, STRTROW, ENDROW ! local window in global domain
      INTEGER :: CARRAY, RARRAY, LENROW, LENCOL

      INTEGER :: K, C, R, L, V  ! loop counters
      INTEGER :: I_SPC, NSPC !Added by mhrzmomeni 2.2019
      CHARACTER(16) :: SPCSNAME(1:NSPCSD) !Added by mhrzmomeni 2.2019
C-----------------------------------------------------------------------
      !Edited by mhrzmomeni 2.2019------------Start
      !NSPC_FRC = 1          ! default
      !VARDESC = 'Index of species in forcing file'
      !NSPC_FRC = ENVINT(ADJNSPC_FRC, VARDESC, NSPC_FRC, STATUS)
      !IF ( STATUS /= 0 ) WRITE(LOGDEV, '(5X, A)') VARDESC
      !IF ( STATUS == 1 ) THEN
      !   XMSG = 'Environment variable improperly formatted'
      !   CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT2)
      !END IF
      !mhrzmomeni 1.2019---------------------End

C Get local window in global domain
      STRTCOL = COLSX_PE(1, MYPE+1)
      ENDCOL = STRTCOL + NCOLS - 1
      STRTROW = ROWSX_PE(1, MYPE+1)
      ENDROW = STRTROW + NROWS - 1
      
      BUFFER = 0.d0
      ARRAY  = 0.d0


C Get file characteristics of ADJ_FILE
      IF ( .NOT. DESC3(ADJ_FORCE) ) THEN
         XMSG = 'Could not get ' // TRIM(ADJ_FORCE) // ' file description'
         CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)
      END IF

!     Debug (mhrzmomeni 2.2019)
      !WRITE(*,*) 'NVARS3D: ',NVARS3D
      !WRITE(*,*) 'VNAME3D(1): ',VNAME3D(1)
      !WRITE(*,*) 'VNAME3D(:): ',VNAME3D(:)
      !STOP
      !WRITE(*,*) 'FTYPE3D: ',FTYPE3D
      !WRITE(*,*) 'SDATE3D: ',SDATE3D
      !WRITE(*,*) 'ADJOINT files'
      !WRITE(*,*) 'NCOLS: ',NCOLS,' NROWS: ',NROWS
      !WRITE(*,*) 'NLAYS: ',NLAYS,'NSPCSD: ',NSPCSD
      !WRITE(*,*) 'STRTCOL: ',STRTCOL
      !WRITE(*,*) 'ENDCOL: ',ENDCOL
      !WRITE(*,*) 'STRTROW: ',STRTROW
      !WRITE(*,*) 'ENDROW: ',ENDROW

      !WRITE(*,*) 'JDATE: ',JDATE
      !WRITE(*,*) 'JTIME: ',JTIME

      K = 0
      ! Specify chemical species based on index in *_SPC files 
      ! in cmaq_adj/ICL directory, read as NSPC_FRC
      
      !V = 22 ! CO (NSPC index) !Edited by mhrzmomeni 1.2019
      !V = 4 ! O3 (NSPC index)  !Edited by mhrzmomeni 1.2019

!     Because ADJ_FORCE will only have one variable,
!        this one variable should be extracted.
!        It may also only be at one level, which is indicated by NLAYS_FRC.
!        The assignment is where V equals the species denoted above.
      IF ( .NOT. XTRACT3(ADJ_FORCE, VNAME3D(1),
     &     1, NLAYS_FRC, STRTROW, ENDROW, STRTCOL, ENDCOL,
     &     JDATE, JTIME, BUFFER) ) THEN
         XMSG = 'Could not read  variables from ' // TRIM(ADJ_FORCE) !Edited by mhrzmomeni 1.2019
         CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)

      ELSE
            
         LENROW = NROWS 
         LENCOL = NCOLS   
         !WRITE(*,*) 'LENROW: ',LENROW, ', LENCOL: ',LENCOL
         !WRITE(*,*) 'BUFFER(1,1,1): ',BUFFER(1,1,1),' on proc: ',MYPE
         !WRITE(*,*) 'BUFFER(LC,LR,1): ',BUFFER(LENCOL,LENROW,NLAYS_FRC),' on proc: ',MYPE
         
         !WRITE(*,*) '********************************' !Debug
         !WRITE(*,*) 'NSPCSD:', NSPCSD !Debug

         !Added by mhrzmomeni 2.2019-----------------Start
         !WRITE(*,*)'=======*********>>>>>>>',  N_GC_SPC, GC_SPC(1:N_GC_SPC) !Debug
         NSPC = 0
         DO I_SPC = 1, N_GC_SPC
             NSPC = NSPC + 1
             SPCSNAME(NSPC) = GC_SPC(I_SPC)
         END DO

         NSPC = NSPC + 1
         SPCSNAME(NSPC) = 'RHOJ'
         !WRITE(*,*) '=======*********>>>>>>>', N_AE_SPC, AE_SPC(1:N_AE_SPC) !Debug
         DO I_SPC = 1, N_AE_SPC
             NSPC = NSPC + 1
             SPCSNAME(NSPC) = AE_SPC(I_SPC)
         END DO

         DO I_SPC = 1, N_TR_SPC
             NSPC = NSPC + 1
             SPCSNAME(NSPC) = TR_SPC(I_SPC)
         END DO
         !WRITE(*,*) '********************************' !Debug
         !WRITE(*,*) SPCSNAME(1), SPCSNAME(NSPC) !Debug
         DO I_SPC = 1, NSPCSD
             !WRITE(*,*) SPCSNAME(I_SPC)
             IF( TRIM(SPCSNAME(I_SPC)) == TRIM(VNAME3D(1)) )THEN
                 NSPC_FRC = I_SPC
                 EXIT
             END IF
         END DO
         !mhrzmomeni 2.2019--------------------------End
         !Debug mhrzmomeni 2.2019
         !WRITE(*,*) '********************************' !Debug
         !WRITE(*,*) 'I_SPC:', I_SPC, '  NSPC_FRC:', NSPC_FRC, '  SPCSNAME:', SPCSNAME(NSPC_FRC) !Debug

         !WRITE(*,*) '********************************' 
         !WRITE(*,*) 'Species forced: ', TRIM(SPCSNAME(NSPC_FRC))
         !WRITE(*,*) '********************************'
         !WRITE(LOGDEV, '(5X, A)') '********************************'
         !WRITE(LOGDEV, '(5X, A, A)') 'Species forced: ', TRIM(SPCSNAME(NSPC_FRC))
         !WRITE(LOGDEV, '(5X, A)') '********************************'
         !STOP

         DO R = 1, LENROW
            DO C = 1, LENCOL
               DO L = 1, NLAYS_FRC
                  !RARRAY = R + STRTROW - 1
                  !CARRAY = C + STRTCOL - 1
                  !ARRAY(CARRAY, RARRAY, L, V) = BUFFER(C, R, L)
                  ARRAY(C, R, L, NSPC_FRC) = BUFFER(C, R, L) !Edited by mhrzmomeni 1.2019 ARRAY(C, R, L, V)
               END DO
            END DO
         END DO
            
      END IF

      END SUBROUTINE RD_FORCE_FILE

C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

      END MODULE ADJOINT_FILES
