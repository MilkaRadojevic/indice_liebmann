
"""
  Program allows to: 
    1. select days within a water year
    2. compute Anamalouse Accumulation indice (AA) using Liebmann's method
    3. identify Onset dates of the wet season for year/(year+1) as next day
       of the day for which maximum of AA occurs 
    4. draw a graph of Onset dates over years, for given locations
    5. draw the maps of a number of statistics of Onset dates
 
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

  Author : Milka Radojevio
  Date   : November 2020
  Version: 1.1 (Dec 2020) 

"""

import os
import sys
import numpy

import netCDF4

from datetime import datetime
import matplotlib.pyplot as plt

# Import the local custom functions
list_func = ['get_ncvar','calc_ind,get_range','nearest_idxs',
             'draw_plot','plot_settings','draw_map']
from ilfunc import *

#==================
# INPUT PARAMETERS
#==================
# Use case: ANGOLA
in_fileName = 'tp_era5-land_reg_hour00_1981-2011.nc'
print('Input dataset:', in_fileName)

# Water year in Southern Hemisphere, Y/07/01 to Y+1/06/30
hydroYearStart = 7

# Locations for which we plot temporal distribution of AA
dict_Location = dict()
dict_Location['Malanje'] = [-9.55, 16.34]
dict_Location['Huambo'] = [-12.77, 15.73]


#==================
# READ NetCDF FILE
#==================
in_file = netCDF4.Dataset(in_fileName, 'r')
#print(in_file.dimensions)
#print(in_file.variables)

# Get 3D matrice of accumulated daily precipitation 
field_grpName = 'tp'
prcp_daily = get_ncvar(in_file, field_grpName)

# Convert precipitation units from m to mm
if in_file.variables[field_grpName].units in 'm':
   prcp_daily = prcp_daily * 1000


# Space coordinates
lats = in_file.variables['latitude'][:]
lons = in_file.variables['longitude'][:]
nlons = lons.shape[0]
nlats = lats.shape[0]


# Time coordinate
time = in_file.variables['time'][:]
units = in_file.variables['time'].units
calendar = in_file.variables['time'].calendar
# Conversion of time array to the array of dates
dtime = netCDF4.num2date (time[:]-24, units=units, calendar=calendar)

startYear = min(dtime).year
endYear   = max(dtime).year
#listYears = list( range(startYear,endYear+1) )
listYears = list( range(startYear,endYear) )
statPeriod = str(startYear)+ '-' +str(endYear)

print('Start date:', min(dtime))
print('End date  :', max(dtime))


#=======================
# WET SEASON: AA, ONSET
#=======================

# Initialize dictionaries
#dict_APcp  = dict()     # Annual accumulation of precipitation
dict_AA    = dict()	# Anomalous Accumulation in mm per year
dict_Onset = dict()	# Onset date

# Split calculation of AA and Onset dates into individual years
# and save 3D data array to corresponding dictionary:
for Year in listYears:

   # Extract prcp_daily within water year
   hydroYear = [ it for it in range(len(dtime)) if
             ( (dtime[it].year == Year) & ( dtime[it].month >= hydroYearStart) ) |
             ( (dtime[it].year == Year+1) & ( dtime[it].month < hydroYearStart) ) ]

   pdYear = prcp_daily[hydroYear,:,:]

   # Compute annual average of precipitation and add 3D array to dict_PA
   #dict_APcp[Year] = numpy.sum(pdYear, axis=0)

   # Compute AA indice for each day of a yer and add 3D array to dict_AA
   AAYear = calc_ind( pdYear )
   dict_AA[Year] = AAYear
  
   # Identify the Onset date of rainy season Y/Y+1
   onsetYear = numpy.argmax( AAYear, axis=0 ) + 1
   dict_Onset[Year] = numpy.array( [*onsetYear] )
   del hydroYear, pdYear, AAYear, onsetYear

# Convert a dictionary of Onset dates to ndarray
Onset = numpy.array( list(dict_Onset.values()) )


#=====================
# PLOT TIME EVOLUTION
#=====================
# Plot yearly evolution of Onset date for the locations in dict_Location
fig1,ax1 = plt.subplots(figsize=(10, 5))

evolTitle = 'Time evolution of Onset date for 2 cities'
tdistImage = 'timeEvolution_' +str(min(listYears))+ '-' +str(max(listYears))

tindOnset = plot_settings(ax1, evolTitle, listYears, Onset)
for locName, locPos in dict_Location.items():
   print('Plot temporal distribution for <',locName,'>')

   # Find the grid indices closest to locPos
   idx_lat, idx_lon = nearest_idxs(lats, lons, locPos)

   # Data array for locName is spatial mean over the nearest grid indices
   locData = [ numpy.mean( Onset[it, idx_lat, idx_lon], dtype=int) 
               for it in tindOnset ]

   if locName in 'Malanje':
      locPlt1, = draw_plot(tindOnset, locData, 'b')
   else: # locName in 'Huambo':
      locPlt2, = draw_plot(tindOnset, locData, 'r')

plt.legend( [locPlt1, locPlt2], ('Malanje','Huambo'), loc="upper right")
plt.savefig(tdistImage, dpi=88, bbox_inches='tight', pad_inches=0)
print('Figure filename of <time evolution>: ' +tdistImage+ '.png')
plt.close(fig1)


#======================
# STATISTICS & MAPPING
#======================
# Compute statistics and save in dictionary of Onset stats
dict_statOnset = dict()
dict_statOnset['meanOnset'] = numpy.mean(Onset, axis=0, dtype=int)
dict_statOnset['minOnset']  = numpy.amin(Onset, axis=0)
dict_statOnset['maxOnset']  = numpy.amax(Onset, axis=0)
dict_statOnset['10pOnset']  = numpy.percentile(Onset, 10, axis=0)
dict_statOnset['90pOnset']  = numpy.percentile(Onset, 90, axis=0)

# Map each statistic and save the figure
for statName, statArr in dict_statOnset.items():
   print('Mapping ' +statName+ ':')
   
   fig,ax = plt.subplots(figsize=(nlons/3, nlats/3))
   statTitle = ('The ' +statName+ ' relative to ' +statPeriod+ ' period')
   plt.title(statTitle, loc='center', size=12)

   statMap = draw_map(lons, lats, statArr, statName)

   # Add the locations situated within the region
   for locName, locPos in dict_Location.items():
      locXs, locYs = statMap(locPos[1], locPos[0])
      statMap.plot(locXs, locYs, 
             marker='x', 
             markeredgecolor='black', 
             markersize=6)
      ax.text(locXs+0.05, locYs+0.1, 
              locName,
              color='k',
              fontsize=10)

   statImage = statName+ '_' +statPeriod
   plt.savefig(statImage, dpi=88, bbox_inches='tight', pad_inches=0)
   print('Figure filename of <' +statName+ '>: '+statImage+ '.png')
   plt.close(fig)

   del statName, statArr, statMap


in_file.close()
