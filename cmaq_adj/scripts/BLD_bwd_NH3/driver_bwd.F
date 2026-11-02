
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
C $Header: /Volumes/Data/CVS/CMAQ_CVSrepos/CCTM/src/driver/yamo_adj_bwd/driver_bwd.F,v 1.2 2013/05/15 20:14:11 ppercell Exp $

C what(1) key, module and SID; SCCS file; date and time of last delta:
C @(#)driver.F  1.2 /project/mod3/CMAQ/src/driver/ctm/SCCS/s.driver.F 07 Jul 1997 09:20:18

C:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      PROGRAM DRIVER_BWD

C-----------------------------------------------------------------------
C Function:
C   Do backward run to compute adjoint sensitivities

C Revision History:
C   Apr 2007 Kumaresh Singh and Adrian Sandu at Virginia Tech: created
C   Aug 2010 by Peter Percell at UH-IMAQS: rewrote for adjoint/4dvar
C   May 2013 by Peter Percell at UH-IMAQS:
C   - support both constant and variable synchronization steps, depending on
C     the choice of checkpointing method
C   - changed the calling argument NADVSS back to the traditional ASTEP
C   - changed XFIRST to an array indexed by layer
C   Aug 2013 by Peter Percell at UH-IMAQS:
C   - made the LGRID output frequency selectable by user
C   Nov 2013 S.Capps (US EPA): shifted emissions-related sensitivity
C            arrays to module
C-----------------------------------------------------------------------

!!!*******************************************
!!!*******************************************
!!! All "!!!"s were applied for editing this file for tracer model by mhrzmomeni (Semko)
!!!*******************************************
!!!*******************************************

      USE PCGRID_DEFN           ! inherits HGRD_DEFN and CGRID_SPCS
      USE VGRD_DEFN             ! vertical layer specifications
      USE CGRID_SPCS            ! CGRID species number and offsets
      USE ADJOINT_FILES         ! adjoint file data and functions
      USE CHK_FILES_DEFS        ! adjoint checkpoint files definition
      USE CHK_FILES             ! adjoint checkpoint files routines
      USE ADJ_ARRAY_MOD, ONLY: FDMTEST, FDM_TEST !Added by mhrzmomeni 1.2019

      IMPLICIT NONE

C Include Files:
      INCLUDE SUBST_IOPARMS     ! I/O parameters definitions
      INCLUDE SUBST_IODECL      ! I/O definitions and declarations
      INCLUDE SUBST_FILES_ID    ! file name parameters

C Load the mechanism COMMON ... (next two INCLUDE files)
      INCLUDE SUBST_RXCMMN      ! chemical mechamism reactions COMMON
      INCLUDE SUBST_RXDATA      ! chemical mechamism reactions DATA

C External Functions:
      INTEGER, EXTERNAL :: GETEFILE
      logical, external :: envyn      !Added by mhrzmomeni 1.2019

C Local Variables:
      INTEGER, SAVE :: LOGDEV   ! FORTRAN unit number for log file

      CHARACTER(16) :: PNAME = 'DRIVER_BWD'
      CHARACTER(96) :: XMSG = ' '
      CHARACTER(2) :: COLROW = 'CR' ! col/row arg list order

      INTEGER, ALLOCATABLE, SAVE :: ASTEP(:) ! advection time steps
      LOGICAL, ALLOCATABLE, SAVE :: XFIRST(:)
      REAL, ALLOCATABLE :: LGRID_FRC(:, :, :, :)
      REAL, ALLOCATABLE :: LGRID_FRC_TOT(:, :, :, :)
      REAL, POINTER :: LGRID(:, :, :, :)
      REAL, POINTER :: LGRID_EM(:, :, :, :)
      
!      INTEGER :: ALLOCSTAT   !Edited by mhrzmomeni 1.2019

      REAL :: CLOCK             ! Wall-clock time (sec) at initialization.
      INTEGER :: PAR_ERR        ! Error code from parallel initialization.

      INTEGER :: JDATE          ! current model date, coded YYYYDDD
      INTEGER :: JTIME          ! current model time, coded HHMMSS

      INTEGER :: SDATE          ! start date, format YYYYDDD
      INTEGER :: STIME          ! start time, format HHMMSS
      INTEGER :: EDATE          ! end date, format YYYYDDD
      INTEGER :: ETIME          ! end time, format HHMMSS
      INTEGER :: TSTEP(2)       ! time step vector (HHMMSS)
                                ! TSTEP(1) = local output step
                                ! TSTEP(2) = sciproc sync. step (chem)
      INTEGER :: NSTEPS         ! run duration: number of output time steps

      INTEGER :: NREPS          ! number of sync steps per output step

      INTEGER :: IUNIT

      INTEGER :: STEP_NUM       ! current output time step number
      INTEGER :: IREP           ! model step number within this output step
      real*8     :: start, finish

      INTERFACE
         SUBROUTINE INIT_LGRID(LGRID, SDATE, STIME, EDATE, ETIME, TSTEP, NSTEPS)
            IMPLICIT NONE
            REAL, POINTER :: LGRID(:, :, :, :)
            INTEGER, INTENT(OUT) :: SDATE
            INTEGER, INTENT(OUT) :: STIME
            INTEGER, INTENT(OUT) :: EDATE
            INTEGER, INTENT(OUT) :: ETIME
            INTEGER, INTENT(OUT) :: TSTEP(2)
            INTEGER, INTENT(OUT) :: NSTEPS
         END SUBROUTINE INIT_LGRID
         SUBROUTINE SYNCSTEP(JDATE, JTIME, TSTEP, NSTEPS, NREPS)
            IMPLICIT NONE
            INTEGER, INTENT(IN)    :: JDATE, JTIME
            INTEGER, INTENT(INOUT) :: TSTEP(2)
            INTEGER, INTENT(IN)    :: NSTEPS
            INTEGER, INTENT(OUT)   :: NREPS
         END SUBROUTINE SYNCSTEP
         SUBROUTINE ADVSTEP(JDATE, JTIME, TSTEP, ASTEP)
            IMPLICIT NONE
            INTEGER, INTENT(IN)  :: JDATE, JTIME
            INTEGER, INTENT(IN)  :: TSTEP(2)
            INTEGER, INTENT(OUT) :: ASTEP(:)
         END SUBROUTINE ADVSTEP
         SUBROUTINE SCIPROC_BWD(LGRID, LGRID_EM,
     &                          JDATE, JTIME, TSTEP, ASTEP, XFIRST)
            IMPLICIT NONE
            REAL, POINTER          :: LGRID(:, :, :, :)
            REAL, POINTER          :: LGRID_EM(:, :, :, :) ! adjoint variable
            INTEGER, INTENT(INOUT) :: JDATE, JTIME
            INTEGER, INTENT(IN)    :: TSTEP(2)
            INTEGER, INTENT(IN)    :: ASTEP(:)
            LOGICAL, INTENT(INOUT) :: XFIRST(:)
         END SUBROUTINE SCIPROC_BWD
      END INTERFACE

C-----------------------------------------------------------------------

      JDATE = 0
      JTIME = 0

C Get number of species, and starting indices for CGRID array.
      !WRITE( LOGDEV, * ) 'enter CALL CGRID_MAP'
      !CALL cpu_time(start)  
      CALL CGRID_MAP(NSPCSD, GC_STRT, AE_STRT, NR_STRT, TR_STRT)
      !CALL cpu_time(finish)
      !WRITE( LOGDEV, * ) 'leave CALL CGRID_MAP'
      !WRITE( LOGDEV,'(/ F7.3)' ) finish
      !WRITE( LOGDEV,'(/ F7.3)' ) finish-start  

C Start up processor communication and define horizontal domain decomposition
C and vertical layer structure
      !WRITE( LOGDEV, * ) 'enter CALL PAR_INIT'
      !CALL cpu_time(start)  
      CALL PAR_INIT(COLROW, NSPCSD, CLOCK, PAR_ERR)
      !CALL cpu_time(finish)
      !WRITE( LOGDEV, * ) 'leave CALL PAR_INIT'
      !WRITE( LOGDEV,'(/ F7.3)' ) finish
      !WRITE( LOGDEV,'(/ F7.3)' ) finish-start  

      IF ( PAR_ERR /= 0 ) THEN
         XMSG = 'Error in PAR_INIT'
         CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)
      END IF

      LOGDEV = INIT3()

      IF ( NSPCSD .GT. MXVARS3 ) THEN
         WRITE(XMSG,'(5X, A, I5, A)') 'The number of variables,', NSPCSD,
     &        ' to be written to the LGRID File'
         WRITE(LOGDEV, '(A)') XMSG
         WRITE(XMSG,'(5X, A, I5)') 'exceeds the I/O-API limit:', MXVARS3
         WRITE(LOGDEV, '(A)') XMSG
         XMSG = 'Recompile with an I/O-API lib having a larger MXVARS3'
         WRITE(LOGDEV, '(5X, A)') XMSG
         CALL M3EXIT(PNAME, JDATE, JTIME, ' ', XSTAT1)
      END IF

C Initialize PCGRID
      IF ( .NOT. PCGRID_INIT() ) THEN
         XMSG = 'Failure defining horizontal domain'
         CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT2)
      END IF

      LGRID => PLGRID(1:NCOLS, 1:NROWS, :, :)
      LGRID_EM => PLGRID_EM(1:NCOLS, 1:NROWS, :, :)

!Added by mhrzmomeni 1.2019----------------Start 
C Read number of layers to be forced
      NLAYS_FRC = 1          ! default
      VARDESC = 'No. of layers in forcing file'
      NLAYS_FRC = ENVINT(ADJNLAYS_FRC, VARDESC, NLAYS_FRC, STATUS)
      IF ( STATUS /= 0 ) WRITE(LOGDEV, '(5X, A)') VARDESC
      IF ( STATUS == 1 ) THEN
         XMSG = 'Environment variable improperly formatted'
         CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT2)
      END IF
!mhrzmomeni 1.2019-------------------------End 

C Allocate memory
      ALLOCATE(
     &     ASTEP(1:NLAYS),
     &     XFIRST(1:NLAYS),
     &     STAT = ALLOCSTAT)
      IF ( ALLOCSTAT /= 0 ) THEN
         XMSG = 'Failure allocating LGRID, ASTEP, XFIRST'
         CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)
      END IF

C Allocate memory for adjoint forcing (6.2014.slc)
      ALLOCATE(
     &     LGRID_FRC(1:NCOLS, 1:NROWS, 1:NLAYS_FRC, 1:NSPCSD),
     &     STAT = ALLOCSTAT)
      IF ( ALLOCSTAT /= 0 ) THEN
         XMSG = 'Failure allocating LGRID_FRC, ASTEP, XFIRST'
         CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)
      END IF
C dbg. cl3293
      !WRITE(*,*) 'NSPCSD: ',NSPCSD
      !WRITE(*,*) 'Shape LGRID_FRC: ',shape(LGRID_FRC)


      ALLOCATE(
     &     LGRID_FRC_TOT(1:NCOLS, 1:NROWS, 1:NLAYS_FRC, 1:NSPCSD),
     &     STAT = ALLOCSTAT)
      IF ( ALLOCSTAT /= 0 ) THEN
         XMSG = 'Failure allocating LGRID_FRC_TOT'
         CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)
      END IF

C Determine the simulation time period and time stepping constants;
C initialize the LGRID array.
      
      LGRID_FRC = 0.0
      LGRID_FRC_TOT = 0.0
      
      !dbg.3.2015.slc
      !write(*,*) 'Shape(LGRID_FRC): ',shape(LGRID_FRC)
      !write(*,*) 'Shape(LGRID_FRC_TOT): ',shape(LGRID_FRC_TOT)
      LGRID = 0.0
      
      !WRITE( LOGDEV, * ) 'enter CALL INIT_LGRID'
      !CALL cpu_time(start)  
      CALL INIT_LGRID(LGRID, SDATE, STIME, EDATE, ETIME, TSTEP, NSTEPS)
      !CALL cpu_time(finish)
      !WRITE( LOGDEV, * ) 'leave CALL INIT_LGRID'
      !WRITE( LOGDEV,'(/ F7.3)' ) finish
      !WRITE( LOGDEV,'(/ F7.3)' ) finish-start  


!Added by mhrzmomeni 1.2019----------------Start 
C Determine whether FD test or not
      FDMTEST = .false.          ! default
      VARDESC = 'FDM TEST flag'
      FDMTEST = envyn(FDM_TEST, VARDESC, FDMTEST, STATUS)
      IF ( STATUS /= 0 ) WRITE(LOGDEV, '(5X, A)') VARDESC
      IF ( STATUS == 1 ) THEN
         XMSG = 'Environment variable improperly formatted'
         CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT2)
      END IF
!mhrzmomeni 1.2019-------------------------End

C Verify input file header consistency with COORD.EXT and run duration
      !WRITE( LOGDEV, * ) 'enter CALL FLCHECK'
      !CALL cpu_time(start)  
      CALL FLCHECK(SDATE, STIME, TSTEP(1))
      !CALL cpu_time(finish)
      !WRITE( LOGDEV, * ) 'leave CALL FLCHECK'
      !WRITE( LOGDEV,'(/ F7.3)' ) finish
      !WRITE( LOGDEV,'(/ F7.3)' ) finish-start  


C If the sync step must be constant for this run, get a synchronization step,
C TSTEP(2), and number of repetitions per output step, NREPS, for the whole run
C (Note: For IOAPI compatibility, TSTEP(2) and NREPS must be constant for a run
C because checkpoints are written every sync step and the IOAPI tools require a
C constant output time step for files.)
      IF ( CONST_SYNC_STEP )
     &     CALL SYNCSTEP(SDATE, STIME, TSTEP, NSTEPS, NREPS)

C Create new adjoint output files and open for update
      !WRITE( LOGDEV, * ) 'enter CALL OP_ADJ_FILE'
      !CALL cpu_time(start)  
      CALL OP_ADJ_FILE(EDATE, ETIME, TSTEP, ADJ_LGRID)
      !CALL cpu_time(finish)
      !WRITE( LOGDEV, * ) 'leave CALL OP_ADJ_FILE'
      !WRITE( LOGDEV,'(/ F7.3)' ) finish
      !WRITE( LOGDEV,'(/ F7.3)' ) finish-start  

      ! Also for emissions related sensitivity output (mdt|slc.11.2013)
      !WRITE( LOGDEV, * ) 'enter CALL OP_ADJ_FILE'
      !CALL cpu_time(start)  
      CALL OP_ADJ_FILE(EDATE, ETIME, TSTEP, ADJ_LGRID_EM)
      !CALL cpu_time(finish)
      !WRITE( LOGDEV, * ) 'leave CALL OP_ADJ_FILE'
      !WRITE( LOGDEV,'(/ F7.3)' ) finish
      !WRITE( LOGDEV,'(/ F7.3)' ) finish-start  


      IF ( TRIM(LGRID_OUTPUT_FREQ) /= 'ONCE' ) THEN
         CALL WR_ADJ_FILE(LGRID, EDATE, ETIME, ADJ_LGRID)
         CALL WR_ADJ_FILE(LGRID_EM, EDATE, ETIME, ADJ_LGRID_EM)
      END IF

C Read XFIRST from the file CTM_XFIRST_IN
      IUNIT = GETEFILE(CTM_XFIRST_IN, .TRUE., .TRUE., PNAME)
      IF ( IUNIT > 0 ) THEN
         READ(IUNIT, '(L1)') XFIRST(1:NLAYS)
         CLOSE(IUNIT)
      ELSE
         XMSG = 'The XFIRST definition file does not exist'
         CALL M3EXIT(PNAME, EDATE, ETIME, XMSG, XSTAT1)
      END IF

C Set the current date and time to the end date and time
      JDATE = EDATE
      JTIME = ETIME

C Do backward (adjoint) solution and write sensitivities (step backwards from
C final time)
      DO STEP_NUM = NSTEPS, 1, -1 ! output time step loop
         SDATE = JDATE
         STIME = JTIME
         CALL NEXTIME(SDATE, STIME, -TSTEP(1))

C If the sync step does not need to be constant for this run, get a
C synchronization step, TSTEP(2), and number of repetitions per output
C step, NREPS, just for this output step
         IF ( .NOT. CONST_SYNC_STEP )
     &        CALL SYNCSTEP(SDATE, STIME, TSTEP, 1, NREPS)

C Get the advection time steps, ASTEP(L)
         !WRITE( LOGDEV, * ) 'enter CALL ADVSTEP'
         !CALL cpu_time(start)  
         CALL ADVSTEP(SDATE, STIME, TSTEP, ASTEP)
         !CALL cpu_time(finish)
         !WRITE( LOGDEV, * ) 'leave CALL ADVSTEP'
         !WRITE( LOGDEV,'(/ F7.3)' ) finish
         !WRITE( LOGDEV,'(/ F7.3)' ) finish-start  


C Read adjoint forcing from file
         IF ( .NOT. OPEN3(ADJ_FORCE, FSREAD3, PNAME) ) THEN
            XMSG = 'Could not open ' // TRIM(ADJ_FORCE) // 
     &             ' file; exiting'
            CALL M3EXIT(PNAME, SDATE, STIME, XMSG, XSTAT1)
         ELSE
            !WRITE( LOGDEV, * ) 'enter CALL RD_FORCE_FILE'
            !CALL cpu_time(start)  
            CALL RD_FORCE_FILE(LGRID_FRC_TOT, SDATE, STIME) !, ADJ_FORCE)
            !CALL cpu_time(finish)
            !WRITE( LOGDEV, * ) 'leave CALL RD_FORCE_FILE'
            !WRITE( LOGDEV,'(/ F7.3)' ) finish
            !WRITE( LOGDEV,'(/ F7.3)' ) finish-start  

!            WRITE(*,*) 'from driver_bwd.F Shape(LGRID_FRC_TOT): ',shape(LGRID_FRC_TOT)
!            WRITE(*,*) 'O3 forcing at (1,1,1): ',LGRID_FRC_TOT(1,1,1,4)
          END IF

         IF ( .NOT. CLOSE3(ADJ_FORCE) ) THEN
            XMSG = 'Could not close ' // TRIM(ADJ_FORCE)
            CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)
         END IF

C Since offline forcing is based on concentrations averaged over the output time step,
C   the forcing can simply be allocated evenly to each synchronization time step. (slc.11.2013)
C        LGRID_FRC and LGRID_FRC_TOT are stored in ADJ_ARRAY_MOD
         ! dbg.8.2014.slc
         LGRID_FRC = LGRID_FRC_TOT / REAL(NREPS)
         DO IREP = NREPS, 1, -1
            ! (6.2014.slc)
!            only forcing at the end of the hour - 8.2014.slc
!            WRITE(LOGDEV,*) 'Before addition, sum LGRID: ', 
!!!     &                 SUM(LGRID),' LGRID_FRC: ',SUM(LGRID_FRC), MYPE
            !WRITE(*,*) 'from driver_bwd.F Shape(LGRID_FRC): ',shape(LGRID_FRC)
     		!LGRID(:,:,1,:) = LGRID(:,:,1,:) + LGRID_FRC(:,:,1,:)  !Edited by mhrzmomeni 1.2019
            LGRID(:,:,1:NLAYS_FRC,:) = LGRID(:,:,1:NLAYS_FRC,:) + LGRID_FRC(:,:,1:NLAYS_FRC,:) !Added by mhrzmomeni 1.2019
!            WRITE(LOGDEV,*) 'After addition, sum LGRID: ', 
!!!     &                 SUM(LGRID),' LGRID_FRC: ',SUM(LGRID_FRC), MYPE
            !WRITE( LOGDEV, * ) 'enter CALL SCIPROC_BWD'
            !CALL cpu_time(start)  
            CALL SCIPROC_BWD(LGRID, LGRID_EM,
     &                       JDATE, JTIME, TSTEP, ASTEP, XFIRST)                     ! science processes
            !CALL cpu_time(finish)
            !WRITE( LOGDEV, * ) 'leave CALL SCIPROC_BWD'
            !WRITE( LOGDEV,'(/ F7.3)' ) finish
            !WRITE( LOGDEV,'(/ F7.3)' ) finish-start  

!            WRITE(LOGDEV,*) 'After SCIPROC_BWD, sum LGRID: ', 
!!!     &                 SUM(LGRID),' LGRID_FRC: ',SUM(LGRID_FRC), MYPE
            IF ( TRIM(LGRID_OUTPUT_FREQ) == 'SYNC_STEP' ) THEN
                 !WRITE( LOGDEV, * ) 'enter CALL WR_ADJ_FILE'
                 !CALL cpu_time(start)  
                 CALL WR_ADJ_FILE(LGRID, JDATE, JTIME, ADJ_LGRID)
                 CALL WR_ADJ_FILE(LGRID_EM, JDATE, JTIME,
     &                            ADJ_LGRID_EM)
                 !CALL cpu_time(finish)
                 !WRITE( LOGDEV, * ) 'leave CALL WR_ADJ_FILE'
                 !WRITE( LOGDEV,'(/ F7.3)' ) finish
                 !WRITE( LOGDEV,'(/ F7.3)' ) finish-start  
 
!                 WRITE(LOGDEV,*) 'After WR_ADJ_FILE1, sum LGRID: ', 
!!!     &                      SUM(LGRID),' LGRID_FRC: ',SUM(LGRID_FRC), MYPE
            END IF
         END DO

         IF ( TRIM(LGRID_OUTPUT_FREQ) == 'OUTPUT_STEP' ) THEN
            CALL WR_ADJ_FILE(LGRID, JDATE, JTIME, ADJ_LGRID)
            CALL WR_ADJ_FILE(LGRID_EM, JDATE, JTIME, ADJ_LGRID_EM)
!            WRITE(LOGDEV,*) 'After WR_ADJ_FILE2, sum LGRID: ', 
!!!     &                 SUM(LGRID),' LGRID_FRC: ',SUM(LGRID_FRC), MYPE
         END IF

      END DO
      IF ( TRIM(LGRID_OUTPUT_FREQ) == 'ONCE' ) THEN
           CALL WR_ADJ_FILE(LGRID, JDATE, JTIME, ADJ_LGRID)
           CALL WR_ADJ_FILE(LGRID_EM, JDATE, JTIME, ADJ_LGRID_EM)
!           WRITE(LOGDEV,*) 'After WR_ADJ_FILE3, sum LGRID: ', 
!!!     &                SUM(LGRID),' LGRID_FRC: ',SUM(LGRID_FRC), MYPE           
      END IF

C Write the final values of XFIRST to the file CTM_XFIRST_OUT
      IF ( MYPE == 0 ) THEN
         IUNIT = GETEFILE(CTM_XFIRST_OUT, .FALSE., .TRUE., PNAME)
         WRITE(IUNIT, '(L1)') XFIRST(1:NLAYS)
         CLOSE(IUNIT)
      END IF

C Close checkpoint files
      CALL CHK_FILE_CLOSE
!      WRITE(LOGDEV,*) 'After CHK_FILE_CLOSE, sum LGRID: ', 
!     &           SUM(LGRID),' LGRID_FRC: ',SUM(LGRID_FRC), MYPE  

C Close adjoint file      !slz
      CALL CLOSE_ADJ_FILE(JDATE, JTIME, ADJ_LGRID) !SLZ
      CALL CLOSE_ADJ_FILE(JDATE, JTIME, ADJ_LGRID_EM) !SLZ
!      WRITE(LOGDEV,*) 'After CLOSE_ADJ_FILE, sum LGRID: ', 
!     &           SUM(LGRID),' LGRID_FRC: ',SUM(LGRID_FRC), MYPE  

C Clean up communications
      !WRITE( LOGDEV, * ) 'enter CALL PAR_TERM'
      !CALL cpu_time(start)  
      CALL PAR_TERM(PNAME, JDATE, JTIME, CLOCK)
      !CALL cpu_time(finish)
      !WRITE( LOGDEV, * ) 'leave CALL PAR_TERM'
      !WRITE( LOGDEV,'(/ F7.3)' ) finish
      !WRITE( LOGDEV,'(/ F7.3)' ) finish-start  


      END PROGRAM DRIVER_BWD

!!!*******************************************
!!!*******************************************
!!! All "!!!"s were applied for editing this file for tracer model by mhrzmomeni (Semko)
!!!*******************************************
!!!*******************************************
