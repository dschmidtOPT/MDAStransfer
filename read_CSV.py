# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 10:55:38 2023

@author: dschmidt
"""


import os
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np


from svgpathtools import svg2paths
# from svgpath2mpl import parse_path

# markerlist = ('whitemarker.svg',
#               'bluemarker.svg',
#               'goldmarker.svg',
#               'greenmarker.svg',
#               'whitemarker.svg')

# markerLib = {}
# for  m in markerlist:
#     _, attributes = svg2paths(os.path.join(r'C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\SVG)', m)) 
#     marker = parse_path(attributes[0]['d'])
#     marker.vertices -= marker.vertices.mean(axis=0)
#     marker = marker.transformed(mpl.transforms.Affine2D().rotate_deg(180))
#     marker = marker.transformed(mpl.transforms.Affine2D().scale(-1,1))
#     name = m.split(".")[0]
#     markerLib[ name ] = marker

NWhemi = np.asarray(Image.open(r'C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\NWhemi.jpg'))

trulong = [-73.974303333, -73.975616, -73.97703, -73.980650,  -73.983200, -73.986833, -73.9904833]
trulat = [40.043081666,40.051450,40.059367,40.075967,40.092417,40.108750,40.125217]
trulabs = ["12:57:??UTC", "13:11:??UTC", "13:23:??UTC","13:39:??UTC", 
           "13:55:??UTC","14:04:??UTC", "14:11:??UTC"]
#df = pd.read_csv(r"C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\Test_Videos\KnownAIS\dbWrites_fromFathom5_testdata2.csv")
df = pd.read_csv(r"C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\8_2_AISjitter.csv")
fig = plt.figure(0)

class PlotVals:
    colorDict = {}
    chooseColor = []
    labels = set()
    mmsi_count = {}
    def __init__(self, mmsi_count ):
        self.chooseColor = [(np.round(np.random.rand(),1),
                             np.round(np.random.rand(),1),
                             np.round(np.random.rand(),1)) for i in range(100)]    
        self.mmsi_count = mmsi_count
    def mmsi_color_picker(self, mmsi):
        if mmsi not in self.colorDict.keys():
            self.colorDict[ mmsi ] = self.chooseColor.pop(0)
        return self.colorDict[ mmsi ]
    def labelin( self, name):
        if name in self.labels:
            return "__nolegend__"
        else:
            self.labels.add( name )
            return name + "\n" +  str(self.mmsi_count[ name ]) +'x'
    
            
        
def labelMaker( ax, dataset):
    print("Function prototype")
    
meta = df['meta'].values
lat = []
lon = []
created = []
sender = []
mmsi = []
cog = []
for row in meta:
    row = row.replace("true","True")
    row = row.replace("false","False")
    full = dict(eval(row))
    mmsi.append(full['Mmsi'])
    lat.append(full['Latitude'])
    lon.append(full['Longitude'])
    sender.append(full['SenderId'])
    try: 
        cog.append(full['CourseOverGround'])
    except:
        cog.append(0)
created = df['created'].values
created = [elem.split(" ")[1] for elem in created]

#lat = df["Latitude"].values
#lon = df['Longitude'].values
#lon = [elem for elem in lon]

filtered = pd.DataFrame({
    'created':created,
    'sender': sender,
    'mmsi': mmsi,
    'lat': lat,
    'lon': lon,
    'cog': cog
    })
###############################################################################
#### Map of lat long writes for all assets ####################################
###############################################################################
ax = fig.add_subplot(111)
plt.ion()
ax.grid()
ax.set_title("Fathom5 DB Writes: AIS Contact Created")
ax.set_xlabel("Lon - deg")
ax.set_ylabel("Lat - deg")
print(filtered['sender'].value_counts())
for asset, data in filtered.groupby('sender'):
    t = np.arange(len(data['lat']))
    ax.scatter(data['lon'], data['lat'], label=asset) #, c=t)    
    sub = data['sender'].values[0].split(":")[0] #+ " " + data['created'].values[0]
    ax.text(data['lon'].values[-1],
            data['lat'].values[-1],
            sub,
            horizontalalignment="right",
            verticalalignment='top',
            #horizontalalignment=["right",'left'][switch],
            #verticalalignment=['top','bottom'][switch],
            fontsize=6,color='k')
    #for i,j,cr,sn in zip(data['lat'],data['lon'],data['created'],data['sender']):
    #    sub = sn.split(":")[0] + " " + cr
    #    ax.text(j+( 0.0001*abs(j)),i,sub,
    #            horizontalalignment="right",
    #            verticalalignment='top',
                #horizontalalignment=["right",'left'][switch],
                #verticalalignment=['top','bottom'][switch],
    #            fontsize=6,color='k')
ax.scatter(-73.974303333, 40.043081666, s=50,marker="^",c="r", label="TB1")
ax.set_xlim([-180,15])
ax.set_ylim([0,90])      
ax.imshow(NWhemi)
ax.legend(loc='lower right')
plt.show()

### Truth Map
fig2 = plt.figure(1)
ax = fig2.add_subplot(111)
plt.ion()
#ax.set_title("Fathom5 DB Writes: TB1 Source")
ax.set_xlabel("Lon - deg")
ax.set_ylabel("Lat - deg")

###############################################################################
############## Specific asset uploads== gss-desktop:#### is TB1 ###############
###############################################################################

#thisAsset = filtered [ filtered['sender'] == "gss-desktop:1875" ] 
thisAsset = filtered [ filtered['sender'] == "gss-desktop:1914" ] 
#thisAsset = thisAsset [ thisAsset['mmsi'] == "367327080"]
t = np.arange( len(thisAsset['lat'].values) )
#ax.scatter( thisAsset['lon'], thisAsset['lat'],s=20,marker = 'o',label="F5 DB Write:\ncontact Created", c=t)    
#tstep = 8
tstep = 4
count = tstep
alt = 0 
thisPlot = PlotVals( thisAsset['mmsi'].value_counts() )
for i,j,cr, mm, rot in zip(thisAsset['lat'], thisAsset['lon'],
                           thisAsset['created'], thisAsset['mmsi'],
                           thisAsset['cog']):
    if i == 91:
        continue
    thisColor = color = thisPlot.mmsi_color_picker(mm)
    if rot:
        #ms = max(8, int( thisPlot.mmsi_count[mm] / 2.6 ) ),
        ax.plot(j,i,marker = (2,0,-1*(rot)), markersize= 8, 
                linestyle = None, color = thisColor, label= thisPlot.labelin( mm ))
        #ax.scatter(j,i, max(8, int( thisPlot.mmsi_count[mm] / 2.0 )), 
        #           marker = "o", color = thisPlot.mmsi_color_picker(mm), 
        #           label= thisPlot.labelin( mm ))
        #p[-1].set_visible(False)
        ax.text(j,i, ">", horizontalalignment='center',verticalalignment='center', 
                rotation = -1*(rot-90), color = thisColor,
                fontsize= 10) #max(8, int( thisPlot.mmsi_count[mm] / 1.5 )))
    else:
        ax.scatter(j,i,s= max(20, int(  thisPlot.mmsi_count[mm] / 2.0 )),
                   marker = 'o', color = thisColor, label= thisPlot.labelin( mm ))
    sub = cr.split(".")[0]
    #sub = cr #+ "\n" + mm
    ### Time annotations ###
    # if count % tstep == 0: 
    #     #if "13" in sub:  ### Time based annotation logic
    #     if alt:
    #         ax.text(j+( 0.00005*abs(j)),i-( 0.00005*abs(i)),sub,
    #                 horizontalalignment="left",
    #                 verticalalignment='bottom',
    #                 rotation = -22,
    #                 fontsize=5,color='k', 
    #                 bbox=dict(facecolor='y', edgecolor='k', boxstyle='round,pad=0.2'))
    #         alt = 0
    #     else:
    #         ax.text(j-( 0.00005*abs(j)),i+( 0.00005*abs(i)),sub,
    #                 horizontalalignment="right",
    #                 verticalalignment='top',
    #                 rotation = 22,
    #                 fontsize=5,color='k',
    #                 bbox=dict(facecolor='y', edgecolor='black', boxstyle='round,pad=0.2'))
    #         alt = 1
    count += 1

print(sub)

# #data = filtered[ filtered['sender'] == "gss-desktop:1875" ]
# t = np.arange(len(data['lat']))
# #ax.scatter(data['lon'], data['lat'],s=10,c=t, ec='k',label="gss-desktop:1875") #, c=t)    
# ax.scatter(trulong, trulat,s=25,c='r',ec='r',marker = '+',label="41351-T2 true pos") #, c=t)    
# tstep = 1
# count = tstep
# for i,j,cr in zip(trulat, trulong,trulabs):
#     #sub = cr.split(".")[0]
#     sub = cr
#     if count % tstep == 0: 
#         if "13" in sub:
#             ax.text(j+( 0.00005*abs(j)),i-( 0.00005*abs(i)),sub,
#                     horizontalalignment="left",
#                     verticalalignment='bottom',
#                     rotation = 00,
#                     fontsize=6,color='w', 
#                     bbox=dict(facecolor='k', edgecolor='k', boxstyle='round,pad=0.2'))
#         else:
#             ax.text(j-( 0.00005*abs(j)),i-( 0.00005*abs(i)),sub,
#                     horizontalalignment="right",
#                     verticalalignment='top',
#                     rotation = 0,
#                     fontsize=6,color='w',
#                     bbox=dict(facecolor='k', edgecolor='black', boxstyle='round,pad=0.2'))
#     count += 1
ax.set_facecolor('black')
ax.scatter(-73.974303333, 40.043081666, s=75,marker="^",c="r", label="TB1 true pos")

## Known AIS Test lat long bounds
#ax.set_xlim([-74.116667,-73.9])
#ax.set_ylim([40.033333,40.13333])      

## AIS Jitter test bounds
#ax.set_ylim([39.966667,40.166667])
#ax.set_xlim([-74.083333,-73.783333])
# l = ax.legend(loc='upper right', fontsize=10, bbox_to_anchor=(1.1,1.0))
# l.set_title("MMSI \ndbWrite Density")
# l.get_frame().set_facecolor((0.9,0.9,0.9))
# l.get_frame().set_edgecolor("k")
# for text in l.get_texts():
#     text.set_color("k")
plt.show()

# fig3 = plt.figure(3)
# ax = fig3.add_subplot(111)
# ax.set_title("AIS Road Test")

# data = pd.read_csv(r'C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\Test_Videos\KnownAIS\AIS_Drives.csv')

# ax.scatter( data['Long'], data['Lat'],150,marker="*",c='r',ec='r',label='True Vehicle Locations')
# for ts,snippet in data.groupby("UTC"):
#     ax.text( snippet['Long'], snippet['Lat'], ts, c='k')
    
# ax.set_xlim(-74.520833,-74.45)
# ax.set_ylim(40.304167,40.333333)
    
