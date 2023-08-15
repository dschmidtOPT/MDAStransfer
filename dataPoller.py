# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 10:55:38 2023

@author: dschmidt
"""


import numpy as np
import pandas as pd
import pdb
from matplotlib import pyplot as plt

pared= []
colors = ['r','g','m','b','k','y','c','w']
fig = plt.figure(0)
ax = fig.add_subplot(111)
ax.set_facecolor('black')
ax.set_xlim([-74.08333333,-73.750])
ax.set_ylim([39.9166666666,40.58333333])
fig.tight_layout()
plt.ion()


## Open Data ##
with open( r"C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\tb-01.gateway.bacis.tracks30min.log", 'r') as f:
    raw = f.readlines()

## Pare down data by throwing away blank lines and head lines ##
for line in raw:
    line.rstrip('\n')
    if line[0] == "[":
        continue
    if line == '\n':
        continue
    if line[0:13] == 'correlationID':
        continue
    pared.append(line)


targets = {}
                     
## Transform Data ##
print("Transforming data")
i = 0
for row in pared:
    lat = []
    lon = []
    created = []
    source = []
    mmsi = []
    cog = []
    sog = []
    row = row.replace("true","True") # <-- prepare strings for Pythonic keyword conversion below
    row = row.replace("false","False") 
    row = row.replace("null","None")
    temp = dict(eval(row))  # <-- read the line of text as a python dictionary
    ### Broken into posits ##
    try:
        mmsi.append(temp['mmsi'])
    except:
        try:
            mmsi.append( 'name' )
        except:
            mmsi.append( None )
    if mmsi[0] in targets.keys():
        targets[ mmsi[0] ] = targets[ mmsi[0] ] + 1 
    else:
        targets[ mmsi[0] ] = 1
    if mmsi[0] == '990901713':
        continue
    
    for full in temp['posits']:
        
        if full['latitude'] == 91:
            continue
        else:
            lat.append(full['latitude'])
        if full['longitude'] == 181:
            continue
        else: 
            lon.append(full['longitude'])
        source.append(full['sensorSource'])
        created.append(full['source_timestamp'])
        try:
            cog.append(full['heading'])
        except:
            cog.append(None)
        try:
            sog.append(full['speed'])
        except:
            sog.append(None)
    #ax.scatter(lon,lat,10,color = colors[i%len(colors)], marker='o',label=mmsi[0])
    ax.plot(lon,lat,color = colors[i%len(colors)], marker='o', label=mmsi[0]+source[0])
    i+=1
# [-73.99637, 39.95858333333333]
ax.scatter(-73.99637, 39.95858333333333, s=50,marker="^",c="r", label="TB1 true pos")
ax.set_title("NATs Track Stream")
ax.set_xlabel('Longitude [deg]')
ax.set_ylabel('Latitude [deg]')
ax.legend(loc='center', fontsize=5, bbox_to_anchor=(1.05,0.5))
#ax.grid()
plt.show()
xlims = ax.get_xlim()
ylims = ax.get_ylim()
print("Map Bounding Box")
print(f'{np.floor(xlims[0])} {(xlims[0]-np.floor(xlims[0])) * 60}", {np.floor(ylims[0])} {(ylims[0]-np.floor(ylims[0])) * 60}"')
print(f'{np.floor(xlims[1])} {(xlims[1]-np.floor(xlims[1])) * 60}", {np.floor(ylims[1])} {(ylims[1]-np.floor(ylims[1])) * 60}"')
targets = pd.DataFrame( targets, columns = targets.keys())
import pdb; pdb.set_trace()

