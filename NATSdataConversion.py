# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 10:55:38 2023

@author: dschmidt
"""


import numpy as np
import pandas as pd
import os
from matplotlib import pyplot as plt

pared= []
colors = ['r','g','m','b','k','y','c','w']
fig = plt.figure(0)
ax = fig.add_subplot(111)
ax.set_facecolor((0.1,0.1,0.1))
fig.tight_layout()
plt.ion()


## Open Data ##
with open( r"C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\ARPAclocking\TB1_9_7_23_NATS_combined.txt", 'r') as f:
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

ARPA = True
                     
## Transform Data ##
print("Transforming NATs data")
i = 0
for row in pared:
    lat = []
    lon = []
    created = []
    brng = []
    rng = []
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
    ## Filtering
    #if mmsi[0] == '990901713':
    #    continue
    if ARPA:
        if mmsi[0] != "999999999":
            continue
    #print(len(temp["posits"]))
    breaker = False
    lastLat = temp['posits'][0]['latitude']
    for full in temp['posits']:
        
        if full['latitude'] == [0,91]:
            continue
        else:
            if lastLat != full['latitude']:
                breaker = True
            lat.append(full['latitude'])
        if full['longitude'] in [0, 181]: 
            continue
        else: 
            lon.append(full['longitude'])
        
        if mmsi[0] in targets.keys():
            targets[ mmsi[0] ] = targets[ mmsi[0] ] + 1 
        else:
            targets[ mmsi[0] ] = 1
        source.append(full['sensorSource'])
        created.append(full['source_timestamp'])
        brng.append(full['bearing'])
        rng.append(full['range'])
        try:
            cog.append(full['heading'])
        except:
            cog.append(None)
        try:
            sog.append(full['speed'])
        except:
            sog.append(None)
    #print(mmsi[0],breaker)
    #ax.scatter(lon,lat,10,color = colors[i%len(colors)], marker='o',label=mmsi[0])
    #import pdb; pdb.set_trace()
    ax.plot(lon,lat,color = colors[i%len(colors)], marker='o', label=mmsi[0]+source[0])
    i+=1

PB3 = [40.04246833,-73.97525333] 
TB1 = [ 39.958247, -73.996408]
asset = TB1
assetname  = "TB1"
ax.scatter(asset[1], asset[0], s=50,marker="^",c="r", label="f{assetname} true pos")
ax.set_title("NATs Track Stream")
ax.set_xlabel('Longitude [deg]')
ax.set_ylabel('Latitude [deg]')
ax.legend(loc='center', fontsize=5, bbox_to_anchor=(1.05,0.5))
longBounds = [-74.10, -73.75]
latBounds = [39.725, 40.00]
#ax.set_xlim([asset[1]- (0.015* abs(asset[1])), asset[1] + (0.015* abs(asset[1]))])
#ax.set_ylim([asset[0] - (0.025*abs(asset[0])), asset[0] + (0.025 * abs(asset[0]))]) 
ax.set_xlim(longBounds[0],longBounds[1])
ax.set_ylim(latBounds[0], latBounds[1])
#ax.grid()
plt.show()
xlims = ax.get_xlim()
ylims = ax.get_ylim()
print("Map Bounding Box")
print(f'{np.floor(xlims[0])} {(xlims[0]-np.floor(xlims[0])) * 60}", {np.floor(ylims[0])} {(ylims[0]-np.floor(ylims[0])) * 60}"')
print(f'{np.floor(xlims[1])} {(xlims[1]-np.floor(xlims[1])) * 60}", {np.floor(ylims[1])} {(ylims[1]-np.floor(ylims[1])) * 60}"')
#targets = pd.DataFrame( {targets, columns = targets.keys())
import pdb; pdb.set_trace()
filtered = pd.DataFrame({
        'created':created,
        'sender': [assetname for i in created],
        'mmsi': mmsi,
        'lat': lat,
        'lon': lon,
        'brng': brng,
        'rng': rng,
        'cog': cog,
        'sog': sog
        })
partial = 0
for key in targets.keys():
    print(key, ": ", targets[ key ])
    partial += targets[key] 
print( "Total updates: ",partial)
filtered.to_csv(os.path.join(os.getcwd(),"ARPAclocking_NATSconversion.csv"))


