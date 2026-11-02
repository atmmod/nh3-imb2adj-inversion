C:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

      MODULE OFFLINE_FILE_FOR_NH3
C-----------------------------------------------------------------------
C Function:
C   Define external offline file functions for NH3 Tracer Model

C Revision History:
C   Aug 2019 by Mahmoudreza (Semko) Momeni (mhrzmomeni) at Drexel University
C-----------------------------------------------------------------------
      IMPLICIT NONE
      SAVE

C-----------------------------------
C Data
C-----------------------------------

C Parameters
      CHARACTER(16), PARAMETER :: NH3_OFFLINE_FILE       = 'NH3_OFFLINE_FILE'

      !!!INTEGER, EXTERNAL :: ENVINT 

      !!!INTEGER, SAVE     :: NLAYS_FRC 
      !!!INTEGER, SAVE     :: NSPC_FRC 
      INTEGER, PARAMETER :: NSPC_OFFLN = 16
      INTEGER, PARAMETER :: HNO3_OFFLN_IDX    = 1  !GC2 !CGRID2
      INTEGER, PARAMETER :: HCL_OFFLN_IDX     = 2  !GC3 !CGRID3
      INTEGER, PARAMETER :: ASO4J_OFFLN_IDX   = 3  !AE1 !CGRID5
      INTEGER, PARAMETER :: ASO4I_OFFLN_IDX   = 4  !AE2 !CGRID6
      INTEGER, PARAMETER :: ANO3J_OFFLN_IDX   = 5  !AE5 !CGRID9
      INTEGER, PARAMETER :: ANO3I_OFFLN_IDX   = 6  !AE6 !CGRID10
      INTEGER, PARAMETER :: ANAJ_OFFLN_IDX    = 7  !AE7 !CGRID11
      INTEGER, PARAMETER :: ANAI_OFFLN_IDX    = 8  !AE8 !CGRID12
      INTEGER, PARAMETER :: ACLJ_OFFLN_IDX    = 9  !AE9 !CGRID13
      INTEGER, PARAMETER :: ACLI_OFFLN_IDX    = 10 !AE10 !CGRID14
      INTEGER, PARAMETER :: DGATK_OFFLN_IDX   = 11 !AE22 !CGRID26
      INTEGER, PARAMETER :: DGACC_OFFLN_IDX   = 12 !AE23 !CGRID27
      INTEGER, PARAMETER :: XXLSGAT_OFFLN_IDX = 13 !AE24 !CGRID28
      INTEGER, PARAMETER :: XXLSGAC_OFFLN_IDX = 14 !AE25 !CGRID29
      INTEGER, PARAMETER :: PDENSAT_OFFLN_IDX = 15 !AE26 !CGRID30
      INTEGER, PARAMETER :: PDENSAC_OFFLN_IDX = 16 !AE27 !CGRID31
C$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

      CONTAINS

C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
C Open an offline file
C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
      SUBROUTINE OPEN_NH3_OFFLINE_FILE( JDATE, JTIME )
! This subroutine is created to open an offline file to run NH3 as a tracer
! Programmer: Mahmoudreza Momeni (Semko) [mhrzmomeni]

      IMPLICIT NONE

      INCLUDE SUBST_IOPARMS     ! I/O parameters definitions
      INCLUDE SUBST_IODECL      ! I/O definitions and declarations
      INCLUDE SUBST_IOFDESC     ! file header data structure

      INTEGER, INTENT(IN) :: JDATE ! current model date, coded YYYYDDD
      INTEGER, INTENT(IN) :: JTIME ! current model time, coded HHMMSS
      CHARACTER(16) :: PNAME = 'OPEN_NH3_OFFLINE_FILE'
      CHARACTER(96) :: XMSG = ' '


      IF ( .NOT. OPEN3( NH3_OFFLINE_FILE, FSREAD3, PNAME ) ) THEN
          XMSG = 'Could not open ' // TRIM(NH3_OFFLINE_FILE) //
     &             ' file; exiting'
          CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)
      ENDIF

      RETURN
      END SUBROUTINE OPEN_NH3_OFFLINE_FILE

C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
C Read from an offline file
C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
      SUBROUTINE READ_NH3_OFFLINE_FILE(NH3_OFFLINE_DATA, JDATE, JTIME)
! This subroutine was created to read species
! required from an offline file to run NH3 active
! Programmer: Mahmoudreza Momeni (Semko) [mhrzmomeni]

      USE CGRID_SPCS            ! CGRID species number and offsets
      USE GRID_CONF             ! horizontal & vertical domain specifications
      !USE CGRID_SPCS, ONLY: NSPCSD !Added by mhrzmomeni 2.2019
      !USE PRECURSOR_DATA

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

      REAL, INTENT(OUT) :: NH3_OFFLINE_DATA(1:NCOLS, 1:NROWS, 1:NLAYS, 1:NSPC_OFFLN)
      !REAL :: NH3_OFFLINE_DATA(1:NCOLS, 1:NROWS, 1:NLAYS, 1:5 ) !NSPC_OFFLN)
      INTEGER, INTENT(IN) :: JDATE ! current model date, coded YYYYDDD
      INTEGER, INTENT(IN) :: JTIME ! current model time, coded HHMMSS
!      CHARACTER(16), INTENT(IN) :: ADJ_FORCE

C Local variables:
      LOGICAL, SAVE :: FIRSTIME_FRC = .TRUE.
      INTEGER, SAVE :: LOGDEV   ! unit number for log device !Added by mhrzmomeni 1.2019

      CHARACTER(16) :: PNAME = 'READ_NH3_OFFLINE_FILE'
      CHARACTER(96) :: XMSG = ' '

      REAL :: BUFFER(1:NCOLS, 1:NROWS, 1:NLAYS)

      INTEGER :: STRTCOL, ENDCOL, STRTROW, ENDROW ! local window in global domain
      INTEGER :: CARRAY, RARRAY, LENROW, LENCOL

      INTEGER :: K, C, R, L, V  ! loop counters
      INTEGER :: I_SPC, I_SPC_OFFLN, NSPC !Added by mhrzmomeni 2.2019
      !INTEGER :: ALLOCSTAT
      CHARACTER(16) :: SPCSNAME(1:NSPC_OFFLN)
      LOGICAL :: XTRACT_FLAG, ASO4I_FLAG, ASO4J_FLAG, ANO3I_FLAG
      LOGICAL :: ANO3J_FLAG, HNO3_FLAG, HCL_FLAG
C-----------------------------------------------------------------------

C Get local window in global domain
      STRTCOL = COLSX_PE(1, MYPE+1)
      ENDCOL = STRTCOL + NCOLS - 1
      STRTROW = ROWSX_PE(1, MYPE+1)
      ENDROW = STRTROW + NROWS - 1
     
      BUFFER = 0.d0
      !WRITE(*,*) '--->: ', shape(NH3_OFFLINE_DATA), NROWS, NCOLS, NLAYS 
      !WRITE(*,*) '---> ', NSPC_OFFLN
      !WRITE(*,*) '---> ', NH3_OFFLINE_DATA( 1, 1, 1, 5)
      !DO C=1,NCOLS
      !    DO R=1,NROWS
      !        DO L=1,NLAYS
      !            DO V=1,NSPC_OFFLN
      !                !IF( V>5 ) CYCLE
      !                WRITE(*,*) '-->',C,R,L,V, NH3_OFFLINE_DATA( C, R, L, V)
      !                NH3_OFFLINE_DATA( C, R, L, V) = 0.d0
      !                WRITE(*,*) '-->',C,R,L,V, NH3_OFFLINE_DATA( C, R, L, V)
      !            ENDDO
      !        ENDDO
      !    ENDDO
      !ENDDO
      NH3_OFFLINE_DATA  = 0.d0
 
      !WRITE(*,*) '----->', BUFFER(1:4,1:4,1)
      !WRITE(*,*) '----->', NH3_OFFLINE_DATA(1:4,1:4,1, 16:18)
C Get file characteristics of NH3_FRC_FILE
      IF ( .NOT. DESC3(NH3_OFFLINE_FILE) ) THEN
         XMSG = 'Could not get ' // TRIM(NH3_OFFLINE_FILE) // ' file description'
         CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)
      END IF

!     Debug (mhrzmomeni 2.2019)
      !WRITE(*,*) 'NVARS3D: ',NVARS3D
      !WRITE(*,*) 'VNAME3D(1): ',VNAME3D(1)
      !WRITE(*,*) 'VNAME3D(:): ',VNAME3D(1:8)
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
      !STOP

      ! Specify chemical species based on index in *_SPC files 
      ! in cmaq_adj/ICL directory, read as NSPC_FRC
      
      !V = 22 ! CO (NSPC index) !Edited by mhrzmomeni 1.2019
      !V = 4 ! O3 (NSPC index)  !Edited by mhrzmomeni 1.2019

!     Because OFFLINE_FILE must have four variables or more including, ASO4I, ASO4J, ANO3I, and ANO3J 
!     the four variables must be extracted.
!        The assignment is where V equals the species denoted above.
      
      XTRACT_FLAG = .FALSE.
      K = 0
      DO V = 1, NVARS3D
          !WRITE(*,*) '---->>>> V, VNAME3D(V): ', V, VNAME3D(V)
          IF( TRIM(VNAME3D(V)) == 'HNO3' )THEN
              I_SPC_OFFLN = HNO3_OFFLN_IDX
              XTRACT_FLAG = .TRUE.
          ELSEIF( TRIM(VNAME3D(V)) == 'HCL' )THEN
              I_SPC_OFFLN = HCL_OFFLN_IDX
              XTRACT_FLAG = .TRUE.
          ELSEIF( TRIM(VNAME3D(V)) == 'ASO4I' )THEN
              I_SPC_OFFLN = ASO4I_OFFLN_IDX
              XTRACT_FLAG = .TRUE.
          ELSEIF( TRIM(VNAME3D(V)) == 'ASO4J' )THEN
              I_SPC_OFFLN = ASO4J_OFFLN_IDX
              XTRACT_FLAG = .TRUE.
          ELSEIF( TRIM(VNAME3D(V)) == 'ANO3I' )THEN
              I_SPC_OFFLN = ANO3I_OFFLN_IDX
              XTRACT_FLAG = .TRUE.
          ELSEIF( TRIM(VNAME3D(V)) == 'ANO3J' )THEN
              I_SPC_OFFLN = ANO3J_OFFLN_IDX
              XTRACT_FLAG = .TRUE.
          ELSEIF( TRIM(VNAME3D(V)) == 'ACLI' )THEN
              I_SPC_OFFLN = ACLI_OFFLN_IDX
              XTRACT_FLAG = .TRUE.
          ELSEIF( TRIM(VNAME3D(V)) == 'ACLJ' )THEN
              I_SPC_OFFLN = ACLJ_OFFLN_IDX
              XTRACT_FLAG = .TRUE.
          ELSEIF( TRIM(VNAME3D(V)) == 'ANAI' )THEN
              I_SPC_OFFLN = ANAI_OFFLN_IDX
              XTRACT_FLAG = .TRUE.
          ELSEIF( TRIM(VNAME3D(V)) == 'ANAJ' )THEN
              I_SPC_OFFLN = ANAJ_OFFLN_IDX
              XTRACT_FLAG = .TRUE.
          ELSEIF( TRIM(VNAME3D(V)) == 'DGATK' )THEN
              I_SPC_OFFLN = DGATK_OFFLN_IDX
              XTRACT_FLAG = .TRUE.
          ELSEIF( TRIM(VNAME3D(V)) == 'DGACC' )THEN
              I_SPC_OFFLN = DGACC_OFFLN_IDX
              XTRACT_FLAG = .TRUE.
          ELSEIF( TRIM(VNAME3D(V)) == 'XXLSGAT' )THEN
              I_SPC_OFFLN = XXLSGAT_OFFLN_IDX
              XTRACT_FLAG = .TRUE.
          ELSEIF( TRIM(VNAME3D(V)) == 'XXLSGAC' )THEN
              I_SPC_OFFLN = XXLSGAC_OFFLN_IDX
              XTRACT_FLAG = .TRUE.
          ELSEIF( TRIM(VNAME3D(V)) == 'PDENSAT' )THEN
              I_SPC_OFFLN = PDENSAT_OFFLN_IDX
              XTRACT_FLAG = .TRUE.
          ELSEIF( TRIM(VNAME3D(V)) == 'PDENSAC' )THEN
              I_SPC_OFFLN = PDENSAC_OFFLN_IDX
              XTRACT_FLAG = .TRUE.
          ELSE
              XTRACT_FLAG = .FALSE.
          ENDIF

          IF( XTRACT_FLAG )THEN
              IF ( .NOT. XTRACT3(NH3_OFFLINE_FILE, VNAME3D(V),
     &             1, NLAYS, STRTROW, ENDROW, STRTCOL, ENDCOL,
     &             JDATE, JTIME, BUFFER) ) THEN
                  XMSG = 'Could not read  variables from ' // TRIM(NH3_OFFLINE_FILE) !Edited by mhrzmomeni 1.2019
                  CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)
              ELSE
                  LENROW = NROWS 
                  LENCOL = NCOLS   
                  !WRITE(*,*) 'LENROW: ',LENROW, ', LENCOL: ',LENCOL
                  !IF(TRIM(VNAME3D(V)) == 'ANAI') WRITE(*,*) 'BUFFER(1:4,1:4,1): ',BUFFER(1:4,1:4,1),' on proc: ',MYPE
                  !IF(TRIM(VNAME3D(V)) == 'ANAJ') WRITE(*,*) 'BUFFER(1:4,1:4,1): ',BUFFER(1:4,1:4,1),' on proc: ',MYPE
                  !IF(TRIM(VNAME3D(V)) == 'ACLI') WRITE(*,*) 'BUFFER(1:4,1:4,1): ',BUFFER(1:4,1:4,1),' on proc: ',MYPE
                  !IF(TRIM(VNAME3D(V)) == 'ACLJ') WRITE(*,*) 'BUFFER(1:4,1:4,1): ',BUFFER(1:4,1:4,1),' on proc: ',MYPE
                  !WRITE(*,*) 'BUFFER(LC,LR,1): ',BUFFER(LENCOL,LENROW,NLAYS_FRC),' on proc: ',MYPE
         
                  !WRITE(*,*) '********************************' !Debug
                  !WRITE(*,*) 'VNAME3D(V)', VNAME3D(V) !Debug
                  !WRITE(*,*)'=======*********>>>>>>>I_SPC_NH3FRC',  I_SPC_NH3FRC !Debug
         
                  !WRITE(*,*) '********************************' 
                  !WRITE(*,*) 'Species forced: ', TRIM(VNAME3D(V))
                  !WRITE(*,*) '********************************'
                  !WRITE(*,*) ' '
                  !WRITE(LOGDEV, '(5X, A)') '********************************'
                  !WRITE(LOGDEV, '(5X, A, A)') 'Species forced: ', TRIM(VNAME3D(V))
                  !WRITE(LOGDEV, '(5X, A)') '********************************'
                  !WRITE(LOGDEV, '(5X, A)') ' '
                  !STOP

                  DO R = 1, LENROW
                      DO C = 1, LENCOL
                          DO L = 1, NLAYS
                  !RARRAY = R + STRTROW - 1
                  !CARRAY = C + STRTCOL - 1
                  !ARRAY(CARRAY, RARRAY, L, V) = BUFFER(C, R, L)
                              NH3_OFFLINE_DATA(C, R, L, I_SPC_OFFLN) = BUFFER(C, R, L) 
                          END DO
                      END DO
                  END DO

                  !IF(I_SPC_NH3FRC==4)  WRITE(*,*) 'OFFLINE_FILE_DATA(1:4,1:4,1,I_SPC_NH3FRC): ',OFFLINE_FILE_DATA(1:4,1:4,1,I_SPC_NH3FRC),' on proc: ',MYPE
                  K = K+1
                  SPCSNAME(K) = TRIM(VNAME3D(V))
              ENDIF
          END IF
      ENDDO
      
      HNO3_FLAG  = .FALSE.
      HCL_FLAG   = .FALSE.
      ASO4I_FLAG = .FALSE.
      ASO4J_FLAG = .FALSE.
      ANO3I_FLAG = .FALSE.
      ANO3J_FLAG = .FALSE.
      ANO3J_FLAG = .FALSE.
      ANO3J_FLAG = .FALSE.
      ANO3J_FLAG = .FALSE.
      ANO3J_FLAG = .FALSE.
      ANO3J_FLAG = .FALSE.
      ANO3J_FLAG = .FALSE.
      DO K = 1, NSPC_OFFLN-6
          IF( SPCSNAME(K) == 'HNO3' )THEN
              HNO3_FLAG = .TRUE.
          ELSEIF( SPCSNAME(K) == 'HCL' )THEN
              HCL_FLAG = .TRUE.
          ELSEIF( SPCSNAME(K) == 'ASO4I' )THEN
              ASO4I_FLAG = .TRUE.
          ELSEIF( SPCSNAME(K) == 'ASO4J' )THEN
              ASO4J_FLAG = .TRUE.
          ELSEIF( SPCSNAME(K) == 'ANO3I' )THEN
              ANO3I_FLAG = .TRUE.
          ELSEIF( SPCSNAME(K) == 'ANO3J' )THEN
              ANO3J_FLAG = .TRUE.
          ENDIF
      ENDDO

      !WRITE(*,*) '----->', BUFFER(1:4,1:4,1)
      !WRITE(*,*) '----->', NH3_OFFLINE_DATA(1:4,1:4,1, 16:18)

      IF( .NOT.HNO3_FLAG .AND. .NOT.HCL_FLAG .AND. .NOT.ASO4I_FLAG .AND.  
     & .NOT.ASO4J_FLAG .AND. .NOT.ANO3I_FLAG .AND. .NOT.ANO3J_FLAG )THEN
          XMSG = 'One of the species of ASO4I, ASO4J, ANO3I, and ANO3J does not exist in ' // TRIM(NH3_OFFLINE_FILE)
          CALL M3EXIT(PNAME, JDATE, JTIME, XMSG, XSTAT1)
      ENDIF
          
      END SUBROUTINE READ_NH3_OFFLINE_FILE

C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
C Update CGRID based on an offline file
C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
      SUBROUTINE UPDATE_SPECIES_FOR_ISORROPIA( CONC, CGRID_OFFLINE )
! This subroutine was created to update species
! based on an offline file to run NH3 as a tracer
! Programmer: Mahmoudreza Momeni (Semko) [mhrzmomeni]

      USE CGRID_SPCS
      USE PRECURSOR_DATA
      USE AERO_DATA

      IMPLICIT NONE

C Include Files:
      INCLUDE SUBST_IOPARMS     ! I/O parameters definitions

C Arguments:
      REAL, INTENT(IN)   :: CGRID_OFFLINE(:)
      REAL, INTENT(OUT)   :: CONC(:)

C *** local variables:
      INTEGER :: I_SPC_OFFLN
      INTEGER :: n_CGRID( 1:NSPC_OFFLN )
      CHARACTER(16) :: PNAME = 'UPDATE_SPECIES_FOR_ISORROPIA'
      CHARACTER(96) :: XMSG = ' '
     
      CALL MAP_PRECURSOR()
      n_CGRID( HNO3_OFFLN_IDX ) = precursor_map( 1 ) !for 'HNO3'
      IF( n_CGRID( HNO3_OFFLN_IDX ) .Eq. 0 )THEN
          xmsg = 'species HNO3 in ' // TRIM(NH3_OFFLINE_FILE) // ' is not in GC_SPC'
          Call m3exit( pname, 0, 0, xmsg, xstat3 )
      ENDIF

      n_CGRID( HCL_OFFLN_IDX ) = precursor_map( 2 ) !for 'HCL'
      IF( n_CGRID( HCL_OFFLN_IDX ) .Eq. 0 )THEN
          xmsg = 'species HCL in ' // TRIM(NH3_OFFLINE_FILE) // ' is not in GC_SPC'
          Call m3exit( pname, 0, 0, xmsg, xstat3 )
      ENDIF

      CALL MAP_AERO()
      n_CGRID( ASO4I_OFFLN_IDX ) = aerospc_map( 1,1 ) !for 'ASO4I'
      IF( n_CGRID( ASO4I_OFFLN_IDX ) .Eq. 0 )THEN
          xmsg = 'species ASO4I in ' // TRIM(NH3_OFFLINE_FILE) // ' is not in AE_SPC'
          Call m3exit( pname, 0, 0, xmsg, xstat3 )
      ENDIF

      n_CGRID( ASO4J_OFFLN_IDX ) = aerospc_map( 1,2 ) !for 'ASO4J'
      IF( n_CGRID( ASO4J_OFFLN_IDX ) .Eq. 0 )THEN
          xmsg = 'species ASO4J in ' // TRIM(NH3_OFFLINE_FILE) // ' is not in AE_SPC'
          Call m3exit( pname, 0, 0, xmsg, xstat3 )
      ENDIF

      n_CGRID( ANO3I_OFFLN_IDX ) = aerospc_map( 3,1 ) !for 'ANO3I'
      IF( n_CGRID( ANO3I_OFFLN_IDX ) .Eq. 0 )THEN
          xmsg = 'species ANO3I in ' // TRIM(NH3_OFFLINE_FILE) // ' is not in AE_SPC'
          Call m3exit( pname, 0, 0, xmsg, xstat3 )
      ENDIF

      n_CGRID( ANO3J_OFFLN_IDX ) = aerospc_map( 3,2 ) !for 'ANO3J'
      IF( n_CGRID( ANO3J_OFFLN_IDX ) .Eq. 0 )THEN
          xmsg = 'species ANO3J in ' // TRIM(NH3_OFFLINE_FILE) // ' is not in AE_SPC'
          Call m3exit( pname, 0, 0, xmsg, xstat3 )
      ENDIF

      n_CGRID( ANAI_OFFLN_IDX ) = aerospc_map( 4,1 ) !for 'ANAI'
      IF( n_CGRID( ANAI_OFFLN_IDX ) .Eq. 0 )THEN
          xmsg = 'species ANAI in ' // TRIM(NH3_OFFLINE_FILE) // ' is not in AE_SPC'
          Call m3exit( pname, 0, 0, xmsg, xstat3 )
      ENDIF

      n_CGRID( ANAJ_OFFLN_IDX ) = aerospc_map( 4,2 ) !for 'ANAJ'
      IF( n_CGRID( ANAJ_OFFLN_IDX ) .Eq. 0 )THEN
          xmsg = 'species ANAJ in ' // TRIM(NH3_OFFLINE_FILE) // ' is not in AE_SPC'
          Call m3exit( pname, 0, 0, xmsg, xstat3 )
      ENDIF

      n_CGRID( ACLI_OFFLN_IDX ) = aerospc_map( 5,1 ) !for 'ACLI'
      IF( n_CGRID( ACLI_OFFLN_IDX ) .Eq. 0 )THEN
          xmsg = 'species ACLI in ' // TRIM(NH3_OFFLINE_FILE) // ' is not in AE_SPC'
          Call m3exit( pname, 0, 0, xmsg, xstat3 )
      ENDIF

      n_CGRID( ACLJ_OFFLN_IDX ) = aerospc_map( 5,2 ) !for 'ACLJ'
      IF( n_CGRID( ACLJ_OFFLN_IDX ) .Eq. 0 )THEN
          xmsg = 'species ACLJ in ' // TRIM(NH3_OFFLINE_FILE) // ' is not in AE_SPC'
          Call m3exit( pname, 0, 0, xmsg, xstat3 )
      ENDIF

      CALL CGRID_MAP( NSPCSD, GC_STRT, AE_STRT, NR_STRT, TR_STRT )
      DO I_SPC_OFFLN=1, NSPC_OFFLN-6
          CONC( n_CGRID( I_SPC_OFFLN ) ) = CGRID_OFFLINE( I_SPC_OFFLN )
      ENDDO
      DO I_SPC_OFFLN=NSPC_OFFLN-6+1, NSPC_OFFLN
          CONC( I_SPC_OFFLN+15 ) = CGRID_OFFLINE( I_SPC_OFFLN )
      ENDDO

      RETURN
      ENDSUBROUTINE UPDATE_SPECIES_FOR_ISORROPIA

C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
C Close an offline file
C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
      SUBROUTINE CLOSE_NH3_OFFLINE_FILE( JDATE, JTIME )

      IMPLICIT NONE

      INCLUDE SUBST_IOPARMS     ! I/O parameters definitions
      INCLUDE SUBST_IODECL      ! I/O definitions and declarations
      INCLUDE SUBST_IOFDESC     ! file header data structure

C Arguments:
      INTEGER, INTENT(IN) :: JDATE ! current model date, coded YYYYDDD
      INTEGER, INTENT(IN) :: JTIME ! current model time, coded HHMMSS

C Local variables:
      CHARACTER(16) :: NH3_OFFLINE_FILE = "NH3_OFFLINE_FILE"
      CHARACTER(16) :: PNAME = 'CLOSE_NH3_OFFLINE_FILE'
      CHARACTER(96) :: XMSG = ' '

      IF ( .NOT. CLOSE3( NH3_OFFLINE_FILE ) ) THEN
             XMSG = 'Could not close ' // TRIM(NH3_OFFLINE_FILE)
             CALL M3EXIT(PNAME, JDATE, JTIME, XMSG )
      END IF

      ENDSUBROUTINE CLOSE_NH3_OFFLINE_FILE

C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

      END MODULE OFFLINE_FILE_FOR_NH3
