"""
David Forel
Seismic Rocks LLC
David@SeismicRocks.com
2020-September

This script builds on another script.
The previous work was done by:
Ryan A. Mardani, linkedin.com/in/amardani
The reference work is:
https://towardsdatascience.com/10-steps-in-pandas-to-process-las-file-and-plot-610732093338
"10 Steps in Pandas to Process LAS File and Plot (Part 1)"

This script adds two extensions to the Mardani work:
 (1) Two logs in the additional 7th track.
 (2) Add a "fraction" track to the previous conventional well log display.
"""

# Begin with the usual imports
import sys
import numpy as np
import pandas as pd
import lasio
import matplotlib.pyplot as plt
from matplotlib.contour import ContourSet
import matplotlib.cm as cm

# These three lines prevent truncating columns of "head" and "tail" commands.
np.set_printoptions(threshold=sys.maxsize)
pd.options.display.max_columns = None
pd.options.display.max_rows = None


#    -->  1.  Read the LAS file (from the Kansas Geological Survey)
print('\n     --->  1.   Read the LAS file')
las = lasio.read(r'1050383876.las')

# Convert LAS file into a pandas data frame to get advantages of its popular functions.
# Store las file in "df" variable as a pandas dataframe
df = las.df()

print(las.curves)


#    -->  2.  Data inspection
print('\n     --->  2.   Data inspection')
# Print the first 5 rows and full columns
print('\n     --->  2a.  df.head()')
print(df.head())

# data frame has X log data in Y columns
print('\n     --->  2b.   df.shape')
print(df.shape)


#    -->  3.  Log (column) selection
print('\n     --->  3.   Log selection')
# Look at the available logs in this LAS file:
print(df.columns)

# From these logs, I select columns of
#  -   CNPOR  --  Neutron Porosity
#  -      GR  --  Gamma Ray
#  -    RHOB  --  Bulk Density
#  -      DT  --  Sonic
#  -  MELCAL  --  Caliper
#  -    SPOR  --  Calculated Sonic Porosity
# and store in a new variable. Remember to use double brackets as follows:
df_selected = df[['CNPOR', 'GR', 'RHOB', 'DT', 'MELCAL', 'SPOR']]


#    -->  4.  Test missing data
print('\n     --->  4.   Test missing data')
# Missing values are very common in LAS files because depth of interest may vary for
# specific measurements. Printed values of -999.2500 in LAS files means null value.
# Missing values are not common in the middle part of the dataset. Usually, it happens
# in the head or tail of a file. "isna" function returns True if the location has a null value,
# otherwise, it will be False. We may add up these boolean values using sum() function as below:
print('\n     --->  4a.   df_selected.isna().sum()')
print(df_selected.isna().sum())


#    -->  5.  Dropping rows
print('\n     --->  5.   Dropping rows')
# Let’s suppose we want to preserve GR, DT, and SPOR as important logs in the data set.
# So, to get rid of missing values we can drop rows that one of those logs is missing in that row.

# Drop all rows that one (or more) of the subset logs ('GR', 'DT', 'SPOR') has a null value.
df_dropped = df_selected.dropna(subset=['GR', 'DT', 'SPOR'],axis=0, how='any')


#    -->  6.  Statistics
print('\n     --->  6.   Statistics')
# Run "describe" command to see data statistics.
# This can be helpful to see the data range and outliers.
print('\n     --->  6a.  df_dropped.describe()')
print(df_dropped.describe())

print('\n     --->  6b.  df_dropped.shape')
print(df_dropped.shape)

#    Normal Range
#   Log   Min    Max
# CNPOR   -15     50
#    GR     0    250
#  RHOB     1      3
#    DT    30    140
#  SPOR   -10     50
#                 ^^

# Compare this table with our file’s statistics. We have some values out of range.
# For example, the maximum value of ‘SPOR’ is 162%, which is an impossible amount in nature.


#    -->  7.  Filtering
print('\n     --->  7.   Filtering')
# There are several ways to filter data, such as zscore.
# In this method, we can get rid of values that are out of a specific range
# of standard deviation such as 2 or more. I personally prefer high/low cut filter
# because I can control the minimum and maximum values as:
df_filt = df_dropped[(df_dropped.CNPOR > -15) & (df_dropped.CNPOR <= 50)]
df_filt = df_dropped[(df_dropped.GR > 0)      & (df_dropped.GR <= 250)]
df_filt = df_dropped[(df_dropped.RHOB > 1)    & (df_dropped.RHOB <= 3)]
df_filt = df_dropped[(df_dropped.DT > 30)     & (df_dropped.DT <= 140)]
# We do not need to filter SPOR because it is a function of DT.


#    -->  8. Add a computed column
print('\n     --->  8.   Add a computed Vshale column')
# First, make a copy of the latest dataset
df = df_filt.copy()

print('\n     --->  8.1  df.shape')
print(df.shape)

# Second, calculate the Shale Volume and add Shale Volume as a column named Vsh.
df['Vsh'] = (df.GR - df.GR.min()) / (df.GR.max() - df.GR.min())


#    -->  9. Indexing
# lasio converts the depth column as an index when we read the LAS file.
# Call depth as a new column for plotting aim and reindex dataset.
df_idx = df.rename_axis('Depth').reset_index()

print('\n     --->  9a.   df_idx.head()')
print( df_idx.head() )
print('\n     --->  9b.   df_idx.tail()')
print( df_idx.tail() )
print('\n     --->  9c.   df_idx.shape')
print(df_idx.shape)


# ---  ===  ---  ===  ---  ===  ---  ===  ---  ===  ---  ===
# ---  ===  ---  ===  ---  ===  ---  ===  ---  ===  ---  ===
print('\n  -------------------------------------------------------\n',
        ' -----              Display the Logs               -----\n',
        ' -----           Original Script Result            -----\n',
        ' -------------------------------------------------------\n')

#    -->  10. Prepare to plot

def log_plot(logs):
    logs = logs.sort_values(by='Depth')
    top = logs.Depth.min()
    bot = logs.Depth.max()

    f, ax = plt.subplots(nrows=1, ncols=6, figsize=(12, 8))
    ax[0].plot(logs.GR, logs.Depth, color='green')
    ax[1].plot(logs.CNPOR, logs.Depth, color='red')
    ax[2].plot(logs.DT, logs.Depth, color='black')
    ax[3].plot(logs.MELCAL, logs.Depth, color='blue')
    ax[4].plot(logs.RHOB, logs.Depth, color='c')
    ax[5].plot(logs.Vsh, logs.Depth, color='m')

    for i in range(len(ax)):
        ax[i].set_ylim(top, bot)
        ax[i].invert_yaxis()
        ax[i].grid()

    ax[0].set_ylabel("Depth(ft)")

    ax[0].set_xlabel("GR")
    ax[0].set_xlim(logs.GR.min(), logs.GR.max())

    ax[1].set_xlabel("CNPOR")
    ax[1].set_xlim(logs.CNPOR.min(), logs.CNPOR.max())

    ax[2].set_xlabel("DT")
    ax[2].set_xlim(logs.DT.min(), logs.DT.max())

    ax[3].set_xlabel("MELCAL")
    ax[3].set_xlim(logs.MELCAL.min(), logs.MELCAL.max())

    ax[4].set_xlabel("RHOB")
    ax[4].set_xlim(logs.RHOB.min(), logs.RHOB.max())

    ax[5].set_xlabel("Vsh")
    ax[5].set_xlim(logs.Vsh.min(), logs.Vsh.max())

    ax[1].set_yticklabels([])
    ax[2].set_yticklabels([])
    ax[3].set_yticklabels([])
    ax[4].set_yticklabels([])
    ax[5].set_yticklabels([])


    f.suptitle('Well: KOOCHEL MOUNTAIN #1', fontsize=14, y=0.94)

# # Call the plot function
log_plot(df_idx)  #                              XXXXXXX
plt.show()        #                              XXXXXXX


# ---  ===  ---  ===  ---  ===  ---  ===  ---  ===  ---  ===
# ---  ===  ---  ===  ---  ===  ---  ===  ---  ===  ---  ===
print('\n  -------------------------------------------------------\n',
        ' -----        Overlay Two Logs in 7th Track        -----\n',
        ' -----   Modify "set_xlim" min and max of Track    -----\n',
        ' -------------------------------------------------------\n')

#    -->  10. Prepare to plot
#
def log_plotter(logs):
    logs = logs.sort_values(by='Depth')
    top = logs.Depth.min()
    bot = logs.Depth.max()

    ##  Add one more to "ncols" and extra width to "figsize"
    f, ax = plt.subplots(nrows=1, ncols=7, figsize=(12, 8))
    ax[0].plot(logs.GR, logs.Depth, color='green')
    ax[1].plot(logs.CNPOR, logs.Depth, color='red')
    ax[2].plot(logs.DT, logs.Depth, color='black')
    ax[3].plot(logs.MELCAL, logs.Depth, color='blue')
    ax[4].plot(logs.RHOB, logs.Depth, color='c')
    ax[5].plot(logs.Vsh, logs.Depth, color='m')

    ##  Combined track of MELCAL, RHOB
    ax[6].plot(logs.MELCAL, logs.Depth, color='blue')
    ax[6].plot(logs.RHOB, logs.Depth, color='c')


    for i in range(len(ax)):
        ax[i].set_ylim(top, bot)
        ax[i].invert_yaxis()
        ax[i].grid()

    ax[0].set_ylabel("Depth (ft)")

    ax[0].set_xlabel("GR")
    ax[0].set_xlim(logs.GR.min(), logs.GR.max())

    ax[1].set_xlabel("CNPOR")
    ax[1].set_xlim(logs.CNPOR.min(), logs.CNPOR.max())

    ax[2].set_xlabel("DT")
    ax[2].set_xlim(logs.DT.min(), logs.DT.max())

    ax[3].set_xlabel("MELCAL")
    ax[3].set_xlim(logs.MELCAL.min(), logs.MELCAL.max())

    ax[4].set_xlabel("RHOB")
    ax[4].set_xlim(logs.RHOB.min(), logs.RHOB.max())

    ax[5].set_xlabel("Vsh")
    ax[5].set_xlim(logs.Vsh.min(), logs.Vsh.max())

    ##  Create track to compare MELCAL and RHOB by overlay
    ax[6].set_xlabel("RHOB, MELCAL")
    ax[6].set_xlim(logs.RHOB.min(), logs.MELCAL.max())
    ##  The horizontal span of this track uses
    ##    RHOB as the minimum and MELCAL as the maximum


    ax[1].set_yticklabels([])
    ax[2].set_yticklabels([])
    ax[3].set_yticklabels([])
    ax[4].set_yticklabels([])
    ax[5].set_yticklabels([])
    ax[6].set_yticklabels([])

    f.suptitle('Well: KOOCHEL MOUNTAIN #1', fontsize=14, y=0.94)


# # Call the plot function
log_plotter(df_idx)  #                           XXXXXXX
plt.show()           #                           XXXXXXX


# ---  ===  ---  ===  ---  ===  ---  ===  ---  ===  ---  ===
# ---  ===  ---  ===  ---  ===  ---  ===  ---  ===  ---  ===
print('\n  -------------------------------------------------------\n',
        ' -----    Create and Plot a Blocky Fraction Log    -----\n',
        ' -------------------------------------------------------\n')


# Fraction Series
# This is an invented series to illustrate a 4-component fraction.
# That is, pretend computations have arrived at 4 components in the wellbore:
#     water, shale, sand, carbonate
# Each of these components starts as a time series of fractional value at depth.
# Then, to stack these time series (horizontally), I add the previous time series
#   value to the next one ("fraction").  Without doing this, each result would overlap.
# Finally, each independent polygon is a list of points, the forward of
#   the n "fraction" with the reverse of the previous n-1 fraction.

# In this scenario, the first element of each series adds to 1 (100%);
#                   the second element of each series adds to 1 (100%); etc.
# Note there is no need for the nth element of each series to add to 1,
#   it just makes a prettier picture (fills the track).
##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##
num_series = 4

# Define color list for my series
mycolors = 'blue', 'red', 'yellow', 'green'

series1 = [0.292,0.333,0.200,0.458,0.292]  #  the series that is closesst to zero
series2 = [0.083,0.125,0.167,0.125,0.083]  #
series3 = [0.292,0.333,0.292,0.083,0.083]  #
series4 = [0.333,0.208,0.341,0.333,0.542]  #  the series that is closest to 1.0

# Get minimum and maximum depths from the dataframe
min_depth = df_idx.Depth.min()
min_coord = [  [0.0,min_depth]  ]
max_depth = df_idx.Depth.max()
max_coord = [  [0.0,max_depth]  ]

# Generate the "float" array of "depths" to be used to create fractional series (value, depth) pairs
depths = np.linspace( min_depth, max_depth, 5 )
print('\n   -->  depths = ', depths)

##  At this point, note that my value series are merely evenly spread in depth.
##    Again, this is an artificial demonstration.  I am sure this can, without
##    much trouble, be modified for true (value, depth) series.
##  I think the important part is to see how a series is turned into a polygon.


# Above are the "series" of fractional values.
# Below, I create a "fraction" that becomes a polygon.
# The fraction must build on the time series that comes before so
# each successive polygon does not rest on the base line.

# Create the empty fractional pairs of [value,depth]
fraction1,fraction2,fraction3,fraction4 = [[]]*len(depths),[[]]*len(depths),[[]]*len(depths),[[]]*len(depths)

for i in range( len(depths) ):
    fraction1[i] = [  series1[i], depths[i]  ]
    fraction2[i] = [  series2[i] + series1[i], depths[i]  ]
    fraction3[i] = [  series3[i] + series2[i] + series1[i], depths[i]  ]
    fraction4[i] = [  series4[i] + series3[i] + series2[i] + series1[i], depths[i]  ]
fractions = [ fraction1, fraction2, fraction3, fraction4 ]

# Create the polygons
# Note that matplotlib polygons do not close on last/first point.
polygon1 = [  max_coord + min_coord + fraction1  ]
polygon2 = [  fraction1 + fraction2[::-1]  ]
polygon3 = [  fraction2 + fraction3[::-1]  ]
polygon4 = [  fraction3 + fraction4[::-1]  ]
polygons = [ polygon1, polygon2, polygon3, polygon4 ]


# ---  ===  ---  ===  ---  ===  ---  ===  ---  ===  ---  ===
# ---  ===  ---  ===  ---  ===  ---  ===  ---  ===  ---  ===

# The rest is the mechanics of plotting

# The lines below create a standalone plot of the polygons.
fig,ax = plt.subplots()

ContourSet( ax, [0,1,2,3,4], [polygon1,polygon2,polygon3,polygon4], filled=True, colors=(mycolors) )

# Legend
plt.plot([],[],color='b', label='Water', linewidth=3)
plt.plot([],[],color='r', label='Shale', linewidth=3)
plt.plot([],[],color='y', label='Sand', linewidth=3)
plt.plot([],[],color='g', label='Carbonate', linewidth=3)
plt.legend()

ax.set_ylim(min_depth, max_depth)
ax.invert_yaxis()

ax.set( xlim=(0, 1), ylim=(max_depth,min_depth), title='Fraction Panel' )
plt.show()

##  Confession:  This plot might have been easier with Matplotlib's "stackplot"
##    but I could not figure out how to turn a stackplot on its side.


# ---  ===  ---  ===  ---  ===  ---  ===  ---  ===  ---  ===
# ---  ===  ---  ===  ---  ===  ---  ===  ---  ===  ---  ===
print('\n  -------------------------------------------------------\n',
        ' -----        Plot Logs with Fraction Panel        -----\n',
        ' -------------------------------------------------------\n')


# The 7th panel of this plot contains the fraction distribution shown in the
#   previous standalone plot.  I created this by using "ax[6]" for the fraction
#   polygons.

def log_plot_combo(logs, polygons, depths):
    logs = logs.sort_values(by='Depth')
    top = logs.Depth.min()
    bot = logs.Depth.max()

    f, ax = plt.subplots(nrows=1, ncols=7, figsize=(14, 8))
    ax[0].plot(logs.GR, logs.Depth, color='green')
    ax[1].plot(logs.CNPOR, logs.Depth, color='red')
    ax[2].plot(logs.DT, logs.Depth, color='black')
    ax[3].plot(logs.MELCAL, logs.Depth, color='blue')
    ax[4].plot(logs.RHOB, logs.Depth, color='c')
    ax[5].plot(logs.Vsh, logs.Depth, color='m')

    ContourSet(ax[6], [0, 1, 2, 3, 4], [polygon1, polygon2, polygon3, polygon4],
               filled=True, colors=('blue', 'red', 'yellow', 'green'))

    # Legend
    plt.plot([], [], color='b', label='Water', linewidth=3)
    plt.plot([], [], color='r', label='Shale', linewidth=3)
    plt.plot([], [], color='y', label='Sand', linewidth=3)
    plt.plot([], [], color='g', label='Carbonate', linewidth=3)
    plt.legend()

    for i in range(len(ax)):
        ax[i].set_ylim(top, bot)
        ax[i].invert_yaxis()
        ax[i].grid()

    ax[0].set_ylabel("Depth (ft)")

    ax[0].set_xlabel("GR")
    ax[0].set_xlim(logs.GR.min(), logs.GR.max())

    ax[1].set_xlabel("CNPOR")
    ax[1].set_xlim(logs.CNPOR.min(), logs.CNPOR.max())

    ax[2].set_xlabel("DT")
    ax[2].set_xlim(logs.DT.min(), logs.DT.max())

    ax[3].set_xlabel("MELCAL")
    ax[3].set_xlim(logs.MELCAL.min(), logs.MELCAL.max())

    ax[4].set_xlabel("RHOB")
    ax[4].set_xlim(logs.RHOB.min(), logs.RHOB.max())

    ax[5].set_xlabel("Vsh")
    ax[5].set_xlim(logs.Vsh.min(), logs.Vsh.max())

    ax[6].set_xlabel("Fraction 4")
    ax[6].set_xlim(0, 1)

    ax[1].set_yticklabels([])
    ax[2].set_yticklabels([])
    ax[3].set_yticklabels([])
    ax[4].set_yticklabels([])
    ax[5].set_yticklabels([])
    ax[6].set_yticklabels([])

    f.suptitle('Well: KOOCHEL MOUNTAIN #1', fontsize=14, y=0.94)


# Call the plot function
log_plot_combo(df_idx, polygons, depths)
plt.show()

