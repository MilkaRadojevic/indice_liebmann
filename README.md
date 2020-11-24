  Program allows to:
    1. compute Anamalouse Accumulation indice (AA) using Liebmann's method
    2. identify Onset dates of the wet season
    3. draw a graph of Onset dates over years, for given locations
    4. draw the maps of a number of statistics of Onset dates

  Input dataset:
  Serie of ERA5-Land total (stratiform+convective) precipitation tp
     - daily accumulation over 1981 to 2010 time window,
     - the time step d+1 at 00h contains the accumulated tp over
       the previous 24 hours (day d),
     - defined on a regular latitude/longitude grid of 0.1°x0.1°,
     - downloaded via the cdsapirequest, in NetCDF format.

  Development environment: CentOS 7.4

  Python requirements:
     - version 3.5
     - modules: netCDF4-1.2.5, matplotlib-1.2.1

  Functions: ilfunc.py

  Execution:
     python indice_liebmann.py

  Note  : The code is created for purposes of the MFI test use case.

