# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 10:55:38 2023

@author: dschmidt
"""


import os
import numpy as np
import pandas as pd
from PIL import Image
from matplotlib.path import Path
from matplotlib import pyplot as plt
from matplotlib import transforms


verts = [
    (0., 1.),
    (0.5, -1.),
    (0., -0.25),
    (-0.5, -1.),
    (0, 1)
    ]

codes = [
    Path.MOVETO,
    Path.LINETO,
    Path.LINETO,
    Path.LINETO,
    Path.CLOSEPOLY
    ]

PB3 = [40.04246833,-73.97525333]  #PB3 position

path = Path(verts, codes)
NWhemi = np.asarray(Image.open(r'C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\NWhemi.jpg'))
#TB1png = np.asarray(Image.open(r'C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\TB1_test_area.png'))
#PB3png = np.asarray(Image.open(r"C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\PB3NJ_test_theatre.PNG"))
PB3png = np.asarray(Image.open(r"C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\NJ_DHS_Testing\PB3_NJ_DHS.PNG"))


#df = pd.read_csv(r"C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\Test_Videos\KnownAIS\dbWrites_fromFathom5_testdata2.csv")
#df = pd.read_csv(r"C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\NJ_DHS_Testing\Reduced\NJ_DHS_AISday1_8_23_23.csv")
fname = r'C:\Users\dschmidt.OCEANPOWERTECH\Documents\Test_Data\NJ_DHS_Testing\NJ_DHS_ARPAday2_8_24_23.csv'
df = pd.read_csv(fname)
fig = plt.figure(0)

#filtered = reduced( df )
filtered = df

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
            if ARPAswitch:
                return name + " " +  str(self.mmsi_count[ name ]) +'x'
            else:
                sub = str(name)
                remain = 9-len(sub)
                sub = "0"*remain + sub
                return str(sub) + " " +  str(self.mmsi_count[ name ]) +'x'
    
def normalizeLong( lon, longspan, w, base):
    return int( ( base + lon ) / float( longspan ) * w )

def normalizeLat( lat, latspan, h, base):
    return int( ( base - lat ) / float( latspan ) * h )
    
def reduce( df ): 
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
        row = row.replace("null","None")
        full = dict(eval(row))
        try:
            mmsi.append(full['Mmsi'])
        except:
            mmsi.append
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
    return filtered


###############################################################################
#### Map of lat long writes for all assets ####################################
###############################################################################
ax = fig.add_subplot(111)
fig.tight_layout()
plt.ion()
ax.grid(False)
longBounds = [ -180, 15 ]
latBounds = [ 0, 90 ]
longspan = longBounds[ 1 ] - longBounds[ 0 ]
latspan = latBounds[ 1 ] - latBounds[ 0 ]
h,w,_ = NWhemi.shape
a,b = -1*longBounds[0], latBounds[1]
if "ARPA" in fname:
    filtered['lon'] = filtered[ 'TargetLongitude' ]
    filtered['lat'] = filtered[ 'TargetLatitude' ]
    filtered['sender'] = filtered['SenderID']
    filtered['mmsi'] = filtered['msgName']
    filtered['cog'] = filtered['TrueTargetCourseDeg']
    ARPAswitch = True
else:
    ARPAswitch = False
    
filtered['normLon'] = filtered.apply( lambda x: normalizeLong( x[ 'lon' ], longspan, w, a ), axis=1)
filtered['normLat'] = filtered.apply( lambda x: normalizeLat(  x[ 'lat' ], latspan,  h, b ),  axis=1)
ax.set_title("Fathom5 DB Writes: AIS Contact Created")
ax.set_xlabel("Lon - deg")
ax.set_ylabel("Lat - deg")
print(filtered['sender'].value_counts())
ax.imshow(NWhemi)
for asset, data in filtered.groupby('sender'):
    t = np.arange(len(data['lat']))
    ax.scatter(data['normLon'], data['normLat'], label=asset) #, c=t)    
    sub = data['sender'].values[0].split(":")[0] #+ " " + data['created'].values[0]
    ax.text(data['lon'].values[-1],
            data['lat'].values[-1],
            sub,
            horizontalalignment="right",
            verticalalignment='top',
            fontsize=6,color='k')
ax.scatter(normalizeLong( -73.974303333, longspan, w, a ), 
           normalizeLat( 40.043081666, latspan, h, b ), 
           s=50,marker="^",c="r", label="PB3")

ax.legend(loc='lower right')
ax.set_xlim( 0, w )
ax.set_ylim( h, 0 )
plt.show()


###############################################################################
############## Specific asset uploads== gss-desktop:#### is TB1 ###############
###############################################################################
### Truth Map
for mmsi, subfilt in filtered.groupby(by='mmsi'):
    fig2 = plt.figure()
    fig2.tight_layout()
    ax = fig2.add_subplot(111)
    plt.ion()
    ax.imshow(PB3png)
    working_title = f"{mmsi}_" + os.path.basename(fname).split(".")[0]
    ax.set_title( working_title )
    ax.set_xlabel("Lon - deg")
    ax.set_ylabel("Lat - deg")
    h,w,_ = PB3png.shape
    longBounds = [-74.10, -73.86]
    latBounds = [39.97, 40.12]
    longspan = longBounds[ 1 ] - longBounds[ 0 ]
    latspan = latBounds[ 1 ] - latBounds[ 0 ]
    a,b = -1*longBounds[0], latBounds[1]
    thisAsset = subfilt #filtered #[ filtered['sender'] == "gss-desktop:1914" ] 
    thisAsset['normLon'] = thisAsset.apply( 
        lambda x: normalizeLong( x[ 'lon' ], longspan, w, base = a ), axis=1)
    thisAsset['normLat'] = thisAsset.apply( 
        lambda x: normalizeLat(  x[ 'lat' ], latspan,  h, base = b ),  axis=1)
    #thisAsset = filtered [ filtered['sender'] == "gss-desktop:1914" ] 
    #thisAsset = thisAsset [ thisAsset['mmsi'] == "367327080"]
    t = np.arange( len(thisAsset['lat'].values) )
    tstep = 4
    count = tstep
    alt = 0 
    thisPlot = PlotVals( thisAsset['mmsi'].value_counts() )
    for l,i,j,mm, rot in zip(thisAsset['lat'],thisAsset['normLat'], thisAsset['normLon'],
                               thisAsset['mmsi'],thisAsset['cog']):
        if l == 91:
            ## Position unknown declaration, throw this away ## 
            continue
        thisColor = color = thisPlot.mmsi_color_picker(mm)
        if rot:
            thisMarker = path.transformed(transforms.Affine2D().rotate_deg( -1*rot ))
            ax.plot(j,i,marker = thisMarker, markersize= 11, mfc = thisColor, 
                    linestyle = '', color = 'k',linewidth=0.05,
                    label= thisPlot.labelin( mm ))
        else:
            ax.scatter(j,i,s= 20, # max(20, int(  thisPlot.mmsi_count[mm] / 2.0 )),
                       marker = 'o', color = thisColor, label= thisPlot.labelin( mm ))
        
        count += 1
        
    ## Plot Target circles
    
    # radii = [0.01666666666,2*0.01666666666,3*0.01666666666]  ## 1deg lat = 60NM, so 1deg/60 = 1NM
    # center = (PB3[1], PB3[0])
    # t = np.linspace(0, 2*np.pi, 100)
    # for rad in radii:
    #     x = normalizeLat(center[0] + rad * np.cos(t), latspan, h, b)
    #     y = normalizeLong(center[1] + rad * np.sin(t), longspan, w, a)
    #     ax.plot(y,x, color = 'y', linewidth=0.25, linestyle='--', dashes=(5, 2))
    
    ## Plot first and final contact reported time
    
    xval = 15 #fixed xval
    ax.text(w-xval,-xval, "Final Contact",
                         horizontalalignment="right",
                         verticalalignment='top',
                         rotation = 0,
                         fontsize=6.5,fontweight='bold',
                         color='k', 
                         bbox=dict(facecolor='c', edgecolor='k', boxstyle='round,pad=0.2'))
    ax.text(xval,-xval, "Initial Contact",
                         horizontalalignment="left",
                         verticalalignment='top',
                         rotation = 0,
                         fontsize=6.5,fontweight='bold',
                         color='w', 
                         bbox=dict(facecolor='k', edgecolor='k', boxstyle='round,pad=0.2'))
    #for mmsi, data in thisAsset.groupby(by="mmsi"):
    if True:
        data = thisAsset
        lat = data['lat'].values[0]
        if lat == 91:
            continue
        if ARPAswitch:
            sub = mmsi
        else:
            sub = str(mmsi)
            remain = 9-len(sub)
            sub = "0"*remain + sub
        cr0 =data["created"].values[0].split(" ")[1]
        deleted =data["created"].values[-1].split(" ")[1]
        i0 = data['normLat'].values[0]
        i1 = data['normLat'].values[-1]
        j0 = data['normLon'].values[0]
        j1 = data['normLon'].values[-1]
        ax.plot([xval,j0],[i0,i0],color='w',linestyle=(0, (5, 10)),linewidth=0.4)
        ax.text(xval,i0, f"{sub}-{cr0}",
                             horizontalalignment="left",
                             verticalalignment='center',
                             rotation = 0,
                             fontsize=5.5,color='w', 
                             bbox=dict(facecolor='k', edgecolor='k', boxstyle='round,pad=0.2'))
        
        ax.plot([w-xval,j1],[i1,i1],color='w',linestyle=(0, (5, 10)),linewidth=0.4)
        ax.text(w-xval,i1, f"{sub}-{deleted}",
                             horizontalalignment="right",
                             verticalalignment='center',
                             rotation = 0,
                             fontsize=5.5,color='k', 
                             bbox=dict(facecolor='c', edgecolor='k', boxstyle='round,pad=0.2'))
        
        
    
    print(sub)
    
    
    ax.set_facecolor('black')
    ax.set_xticklabels((str(val) for val in np.around( np.linspace( longBounds[0], longBounds[1], 6 ), 2) ))
    ax.set_yticklabels((str(val) for val in np.around( np.linspace( latBounds[1], latBounds[0], 6 ), 2) ))
    ax.scatter(normalizeLong( PB3[1], longspan, w, a), 
               normalizeLat( PB3[0], latspan, h, b), 
               s=50,marker="^",c="r", label="PB3 TruPos")
    ## Known AIS Test lat long bounds
    ax.set_xlim( 0, w )
    ax.set_ylim( h, 0 )     
    
    ## AIS Jitter test bounds
    #ax.set_ylim([39.966667,40.166667])
    #ax.set_xlim([-74.083333,-73.783333])
    l = ax.legend(loc='upper left', fontsize=10, bbox_to_anchor=(1.1,1.0))
    plt.savefig(working_title + ".png",
            bbox_inches ="tight",
            pad_inches = 0.25,
            dpi=250,
            orientation ='landscape')
    #plt.tight_layout()
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
    

    
