MODULE aqchem_Model

!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
!  Completely defines the model aqchem
!    by using all the associated modules
!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  USE aqchem_Precision
  USE aqchem_Parameters
  USE aqchem_Global
  USE aqchem_Function
  USE aqchem_Integrator
  USE aqchem_Integrator_ADJ
  USE aqchem_Rates
  USE aqchem_Jacobian
  USE aqchem_Hessian
  USE aqchem_LinearAlgebra
!  USE aqchem_Monitor
!  USE aqchem_Util

END MODULE aqchem_Model

