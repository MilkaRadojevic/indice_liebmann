

"""
  This Python script contains the custom made functions for
  purposes of executing: indice_liebmann.py

  List of functions:
    - get_ncvar
    - calc_ind 
    - get_range
    - nearest_idxs
    - draw_plot
    - plot_settings  
    - draw_map
  
  Author: Milka Radojevio
  Date  : November 2020

"""

import os
import sys
import numpy
from datetime import datetime

import netCDF4

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.basemap import Basemap


def get_ncvar(in_file, field_grpName):
   """
      Returns precipitation field from a NetCDF file
      Read, unpack and assign filled and missing values  
   """
   scale_factor = in_file.variables[field_grpName].scale_factor
   add_offset   = in_file.variables[field_grpName].add_offset
   _FillValue    = in_file.variables[field_grpName]._FillValue
   missing_value = in_file.variables[field_grpName].missing_value

   prcp_daily = in_file.variables[field_grpName][:] * scale_factor + add_offset
   numpy.where((prcp_daily == _FillValue) | (prcp_daily == missing_value), 
                numpy.nan,
                prcp_daily)
   
   return prcp_daily


def calc_ind(Rda):
   """
      Returns a 3D array of Anomalous Accumulation (AA)
      for a given year, expressed in mm
   """
   try:
      Rada = numpy.mean(Rda, 0)		# Annual daily average
      AA = numpy.cumsum(Rda - Rada, axis=0)
      return AA
   except:
      print('ERROR while computing AA.')
      raise KeyError


def get_range(dataQ, intQ):
   minQ = numpy.min(dataQ)
   maxQ = numpy.max(dataQ)
   return numpy.arange(minQ, maxQ+intQ, intQ)


def nearest_idxs(lats, lons, locPos):
   """ 
   Find the grid indices closest to a given user location
   """
   idx_lat = numpy.where( (lats >= locPos[0]-0.2) & (lats <= locPos[0]+0.2) )
   idx_lon = numpy.where( (lons >= locPos[1]-0.2) & (lons <= locPos[1]+0.2) )
   return idx_lat, idx_lon


def draw_plot(tindData, locData, locColor):
   """
      Plot time evolution of locData for a given loc
   """
   locPlt = plt.plot(tindData, locData, 
                    marker='o',
                    markersize=4,
                    color=locColor,
                    linewidth=1.25)
   return locPlt


def plot_settings(ax1, evolTitle, listYears, dataQ):
   """
      Set title, ticks and tick labels for plot by draw_plot() 
   """
   plt.title(evolTitle, 
             loc='center',
             fontsize=12,
             fontweight=1.5,
             color='black')

   plt.xlabel('Year')
   tindQ = list( range(0, dataQ.shape[0]) )
   plt.xticks(tindQ, listYears, rotation=45)
   ax1.set_xlim( [0, len(tindQ)-1] )

   plt.ylabel('Onset date of the wet season')
   rangeQ = get_range(dataQ, 2) # 2-day interval
   plt.yticks( rangeQ )
   #ax1.set_ylim([min(rangeQ),max(rangeQ)])
   ax1.set_ylim([254,320])  # custom limits for dict_Location
   ax1.yaxis.set_major_formatter( mdates.DateFormatter('%b-%d') )

   plt.tick_params(axis='both', labelsize=8)

   return tindQ


def draw_map(lons, lats, dataQ, nameQ):

   """
      Draw the contour filled map of 2D data array
      such as statistics of Onset or End date of
      the wet season over a given region.
   """
   xs, ys = numpy.meshgrid(lons, lats)
   m = Basemap(projection='cyl',
               llcrnrlon = min(lons)-1.5,
               llcrnrlat = min(lats)-0.5,
               urcrnrlon = max(lons)+1,
               urcrnrlat = max(lats)+0.5,
               resolution = 'i' )

   # Add continent and admin outlines
   m.drawcoastlines(linewidth=1.25)
   m.drawcountries(linewidth=1.0)
   m.shadedrelief(ax=None, scale=0.5)

   # Other parameters
   if nameQ in ['meanOnset']:
      intQ = 2
      cmapName = 'jet_r'
      minQ = numpy.min(dataQ)
      maxQ = numpy.max(dataQ)
   else:
      intQ = 7
      cmapName = 'hsv'
      minQ = 364/2
      maxQ = 364
      """
      intQ = 14
      cmapName = 'hsv' #'jet_r'
      minQ = 1
      maxQ = 364
      """

   boundsQ = numpy.arange(minQ, maxQ+intQ, intQ)
   normQ = mpl.colors.BoundaryNorm(boundsQ, len(boundsQ)-1)
   cmapQ = plt.cm.get_cmap(cmapName, len(boundsQ))

   # Filled contours
   cnt = m.contourf(xs, ys, dataQ,
                  vmin = minQ,
                  vmax = maxQ,
                  levels = boundsQ,
                  cmap = cmapQ,
                  norm = normQ,
                  alpha = 0.75)
                  #antialiased = True )

   # Colorbar
   cb = m.colorbar(cnt, location='right', pad=0.15, size='3%')
   cb.set_clim(minQ, maxQ)
   cb.set_ticks(boundsQ)
   boundsQstr = numpy.array([ '{:.0f}'.format(bnd) for bnd in boundsQ ])
   boundsQdate = [datetime.strptime(bnd, '%j').date().strftime('%b-%d') 
                   for bnd in boundsQstr]
   cb.ax.set_yticklabels(boundsQdate, fontsize=10)

   return m
